#!/usr/bin/env python3
"""Fast analytic orbital screening for a hypothetical planet.

This module is deliberately *not* an N-body integrator. It is a transparent
pre-screen used to reject obviously crowded configurations before expensive
long-term integrations.

Units:
- semimajor axis: AU
- stellar mass: solar masses
- planetary mass: Earth masses
- period: days
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

EARTH_MASS_IN_SOLAR = 3.0034896e-6
DAYS_PER_YEAR = 365.25
HILL_STABILITY_THRESHOLD = 2.0 * math.sqrt(3.0)


def kepler_period_days(
    semimajor_axis_au: float,
    stellar_mass_solar: float,
    planet_mass_earth: float = 0.0,
) -> float:
    """Return the two-body Keplerian period in days.

    Uses canonical AU / solar-mass / year units, where
    P_years^2 = a_AU^3 / (M_star + M_planet).
    """
    total_mass = stellar_mass_solar + planet_mass_earth * EARTH_MASS_IN_SOLAR
    if semimajor_axis_au <= 0 or total_mass <= 0:
        raise ValueError("semimajor axis and total mass must be positive")
    return DAYS_PER_YEAR * math.sqrt(semimajor_axis_au**3 / total_mass)


def mutual_hill_separation(
    a1_au: float,
    a2_au: float,
    m1_earth: float,
    m2_earth: float,
    stellar_mass_solar: float,
) -> float:
    """Return orbital spacing in mutual Hill radii.

    For two low-mass planets on nearly circular, coplanar orbits:

        R_H,m = ((m1 + m2) / (3 M_star))^(1/3) * (a1 + a2)/2
        Delta = |a2 - a1| / R_H,m

    Delta > 2*sqrt(3) is a classic analytic Hill-stability threshold for
    the idealized two-planet problem. It is only a screen here: the real
    triple-star system requires direct N-body integration.
    """
    if min(a1_au, a2_au, stellar_mass_solar) <= 0:
        raise ValueError("semimajor axes and stellar mass must be positive")
    if min(m1_earth, m2_earth) < 0:
        raise ValueError("planet masses cannot be negative")

    mass_ratio = (
        (m1_earth + m2_earth) * EARTH_MASS_IN_SOLAR
        / (3.0 * stellar_mass_solar)
    )
    mutual_hill_radius = mass_ratio ** (1.0 / 3.0) * (a1_au + a2_au) / 2.0
    if mutual_hill_radius == 0:
        return math.inf
    return abs(a2_au - a1_au) / mutual_hill_radius


def _companion_tidal_index(dataset: dict[str, Any], candidate_a_au: float) -> float | None:
    """Approximate differential forcing from the outer B+C pair.

    Uses the *projected* A-to-BC separation encoded in the literature scaffold.
    This is a scale indicator only, not an orbital solution.
    """
    stars = {s["id"]: s for s in dataset.get("stars", [])}
    hierarchy = dataset.get("hierarchy", {})
    distance_pc = dataset.get("system", {}).get("distance_pc")
    sep_arcsec = hierarchy.get("outer_projected_separation_arcsec_approx")
    if not distance_pc or not sep_arcsec or not all(k in stars for k in ("A", "B", "C")):
        return None

    projected_sep_au = float(distance_pc) * float(sep_arcsec)
    companion_mass = float(stars["B"]["mass_solar"]) + float(stars["C"]["mass_solar"])
    host_mass = float(stars["A"]["mass_solar"])
    return (companion_mass / host_mass) * (candidate_a_au / projected_sep_au) ** 3


def screen_candidate(
    dataset: dict[str, Any],
    candidate_a_au: float,
    candidate_mass_earth: float = 1.0,
) -> dict[str, Any]:
    """Screen H-01 against observed planets around LTT 1445 A."""
    stars = {s["id"]: s for s in dataset.get("stars", [])}
    host = stars["A"]
    host_mass = float(host["mass_solar"])

    pairwise = []
    for planet in dataset.get("observed_planets", []):
        a = planet.get("semi_major_axis_au")
        mass = planet.get("mass_earth")
        if a is None or mass is None:
            continue
        delta = mutual_hill_separation(
            float(a),
            candidate_a_au,
            float(mass),
            candidate_mass_earth,
            host_mass,
        )
        pairwise.append({
            "planet": planet["name"],
            "delta_mutual_hill": delta,
            "threshold": HILL_STABILITY_THRESHOLD,
            "passes_pairwise_screen": delta > HILL_STABILITY_THRESHOLD,
        })

    min_delta = min((p["delta_mutual_hill"] for p in pairwise), default=None)
    passes = bool(pairwise) and all(p["passes_pairwise_screen"] for p in pairwise)

    if min_delta is None:
        interpretation = "insufficient observed-planet mass/orbit data"
    elif min_delta < HILL_STABILITY_THRESHOLD:
        interpretation = "fails simple pairwise Hill screen"
    elif min_delta < 8.0:
        interpretation = "passes analytic threshold but remains dynamically crowded"
    else:
        interpretation = "well separated in the pairwise analytic screen"

    return {
        "model": "pairwise_hill_screen_v0.1",
        "epistemic_level": "DERIVED",
        "candidate": {
            "name": "TRISOLARIS H-01",
            "semimajor_axis_au": candidate_a_au,
            "assumed_mass_earth": candidate_mass_earth,
            "kepler_period_days": kepler_period_days(
                candidate_a_au,
                host_mass,
                candidate_mass_earth,
            ),
        },
        "host_star": {
            "name": host["name"],
            "mass_solar": host_mass,
        },
        "thresholds": {
            "two_planet_hill_delta": HILL_STABILITY_THRESHOLD,
            "strong_spacing_heuristic_delta": 8.0,
        },
        "pairwise": pairwise,
        "minimum_delta_mutual_hill": min_delta,
        "passes_pairwise_screen": passes,
        "interpretation": interpretation,
        "outer_companion_tidal_index_approx": _companion_tidal_index(
            dataset,
            candidate_a_au,
        ),
        "limitations": [
            "not an N-body integration",
            "assumes a 1 Earth-mass H-01 unless overridden",
            "pairwise Hill criterion assumes nearly circular coplanar low-mass planets",
            "does not test mean-motion resonances",
            "does not propagate uncertainties",
            "does not solve the full LTT 1445 ABC stellar orbit",
            "outer-companion forcing uses projected separation only",
        ],
        "next_model": "long-term N-body ensemble with observed-parameter uncertainties",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--a", type=float, default=None, help="H-01 semimajor axis [AU]")
    parser.add_argument("--mass-earth", type=float, default=1.0)
    args = parser.parse_args()

    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    default_a = dataset["hypothetical_experiment"]["semi_major_axis_au"]
    result = screen_candidate(
        dataset,
        candidate_a_au=args.a if args.a is not None else float(default_a),
        candidate_mass_earth=args.mass_earth,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
