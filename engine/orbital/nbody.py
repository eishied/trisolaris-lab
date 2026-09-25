#!/usr/bin/env python3
"""Pilot N-body ensemble for TRISOLARIS LAB.

Scientific scope
----------------
This module integrates LTT 1445 A, its confirmed planets, hypothetical H-01,
and a simplified B+C barycentric perturber with REBOUND.

The B/C internal binary is NOT resolved in this phase because a complete
orbital solution is not yet encoded in the project dataset. The model samples
unknown phases and eccentricities and must be presented as MODELED, not
OBSERVED and not a proof of long-term stability.
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass, asdict
from typing import Any

import rebound

EARTH_MASS_IN_SOLAR = 3.0034896e-6


@dataclass
class RunResult:
    seed: int
    survived: bool
    classification: str
    max_eccentricity: float
    min_pericenter_au: float
    max_apocenter_au: float
    max_semimajor_drift_fraction: float
    final_semimajor_axis_au: float | None
    sampled_outer_eccentricity: float
    sampled_h01_eccentricity: float


def _outer_semimajor_axis_au(dataset: dict[str, Any]) -> float:
    """Estimate the A-(BC) semimajor axis from the literature period.

    In AU/yr/Msun units, Kepler's third law is a^3 = P^2 M_total.
    """
    stars = {s["id"]: s for s in dataset["stars"]}
    period_years = float(dataset["hierarchy"]["outer_period_years_approx"])
    total_mass = sum(float(stars[k]["mass_solar"]) for k in ("A", "B", "C"))
    return (period_years * period_years * total_mass) ** (1.0 / 3.0)


def build_simulation(
    dataset: dict[str, Any],
    *,
    seed: int,
    candidate_a_au: float,
    candidate_mass_earth: float = 1.0,
) -> tuple[rebound.Simulation, dict[str, float]]:
    rng = random.Random(seed)
    stars = {s["id"]: s for s in dataset["stars"]}
    host_mass = float(stars["A"]["mass_solar"])
    companion_mass = float(stars["B"]["mass_solar"]) + float(stars["C"]["mass_solar"])

    sim = rebound.Simulation()
    sim.units = ("AU", "yr", "Msun")
    sim.integrator = "ias15"

    # Host star.
    sim.add(m=host_mass, hash="A")
    host = sim.particles["A"]

    # Observed planets around A. Unknown eccentricity is sampled conservatively
    # rather than silently set to exactly zero.
    for i, planet in enumerate(dataset.get("observed_planets", [])):
        a = planet.get("semi_major_axis_au")
        mass = planet.get("mass_earth")
        if a is None or mass is None:
            continue
        eccentricity = planet.get("eccentricity")
        if eccentricity is None:
            eccentricity = rng.uniform(0.0, 0.08)
        else:
            eccentricity = max(0.0, min(float(eccentricity), 0.6))
        sim.add(
            primary=host,
            m=float(mass) * EARTH_MASS_IN_SOLAR,
            a=float(a),
            e=eccentricity,
            inc=rng.uniform(0.0, math.radians(1.0)),
            Omega=rng.uniform(0.0, 2.0 * math.pi),
            omega=rng.uniform(0.0, 2.0 * math.pi),
            M=rng.uniform(0.0, 2.0 * math.pi),
            hash=f"planet-{i}",
        )

    h01_e = rng.uniform(0.0, 0.08)
    sim.add(
        primary=host,
        m=candidate_mass_earth * EARTH_MASS_IN_SOLAR,
        a=candidate_a_au,
        e=h01_e,
        inc=rng.uniform(0.0, math.radians(1.5)),
        Omega=rng.uniform(0.0, 2.0 * math.pi),
        omega=rng.uniform(0.0, 2.0 * math.pi),
        M=rng.uniform(0.0, 2.0 * math.pi),
        hash="H01",
    )

    # Phase 2.1 approximation: the unresolved B+C binary is replaced by its
    # barycentric mass. Unknown outer eccentricity and phase are sampled.
    outer_a = _outer_semimajor_axis_au(dataset)
    outer_e = rng.uniform(0.0, 0.45)
    sim.add(
        primary=host,
        m=companion_mass,
        a=outer_a,
        e=outer_e,
        inc=rng.uniform(0.0, math.radians(15.0)),
        Omega=rng.uniform(0.0, 2.0 * math.pi),
        omega=rng.uniform(0.0, 2.0 * math.pi),
        M=rng.uniform(0.0, 2.0 * math.pi),
        hash="BC",
    )

    sim.move_to_com()
    return sim, {
        "h01_e": h01_e,
        "outer_e": outer_e,
        "outer_a_au": outer_a,
    }


def run_one(
    dataset: dict[str, Any],
    *,
    seed: int,
    candidate_a_au: float,
    years: float,
    samples: int,
) -> RunResult:
    sim, sampled = build_simulation(
        dataset,
        seed=seed,
        candidate_a_au=candidate_a_au,
    )

    host = sim.particles["A"]
    h01 = sim.particles["H01"]
    initial_a = candidate_a_au

    max_e = 0.0
    min_q = math.inf
    max_Q = 0.0
    max_drift = 0.0
    final_a: float | None = initial_a
    classification = "survived pilot interval"
    survived = True

    for step in range(1, samples + 1):
        sim.integrate(years * step / samples)
        try:
            orbit = h01.orbit(primary=host)
            a = float(orbit.a)
            e = float(orbit.e)
        except Exception:
            survived = False
            classification = "orbit could not be reconstructed"
            final_a = None
            break

        if not math.isfinite(a) or not math.isfinite(e) or a <= 0 or e >= 1:
            survived = False
            classification = "unbound during pilot integration"
            final_a = None
            break

        q = a * (1.0 - e)
        Q = a * (1.0 + e)
        drift = abs(a - initial_a) / initial_a

        max_e = max(max_e, e)
        min_q = min(min_q, q)
        max_Q = max(max_Q, Q)
        max_drift = max(max_drift, drift)
        final_a = a

        if q < 0.01:
            survived = False
            classification = "critical inward excursion"
            break
        if Q > 1.0:
            survived = False
            classification = "critical outward excursion"
            break

    if survived:
        if max_drift > 0.20 or max_e > 0.50:
            classification = "survived but strongly perturbed"
        elif max_drift > 0.05 or max_e > 0.20:
            classification = "survived with measurable perturbation"

    return RunResult(
        seed=seed,
        survived=survived,
        classification=classification,
        max_eccentricity=max_e,
        min_pericenter_au=min_q if math.isfinite(min_q) else 0.0,
        max_apocenter_au=max_Q,
        max_semimajor_drift_fraction=max_drift,
        final_semimajor_axis_au=final_a,
        sampled_outer_eccentricity=sampled["outer_e"],
        sampled_h01_eccentricity=sampled["h01_e"],
    )


def run_ensemble(
    dataset: dict[str, Any],
    *,
    candidate_a_au: float,
    runs: int = 12,
    years: float = 100.0,
    samples: int = 160,
    seed_base: int = 1445,
) -> dict[str, Any]:
    results = [
        run_one(
            dataset,
            seed=seed_base + i,
            candidate_a_au=candidate_a_au,
            years=years,
            samples=samples,
        )
        for i in range(runs)
    ]

    survived = sum(1 for r in results if r.survived)
    strongly_perturbed = sum(
        1 for r in results
        if r.survived and (
            r.max_semimajor_drift_fraction > 0.20 or r.max_eccentricity > 0.50
        )
    )
    measurable = sum(
        1 for r in results
        if r.survived and r.classification == "survived with measurable perturbation"
    )

    max_e = max((r.max_eccentricity for r in results), default=0.0)
    max_drift = max((r.max_semimajor_drift_fraction for r in results), default=0.0)

    return {
        "model": "rebound_bc_barycenter_pilot_v0.1",
        "engine": f"REBOUND {rebound.__version__}",
        "epistemic_level": "MODELED",
        "candidate": {
            "name": "TRISOLARIS H-01",
            "semimajor_axis_au": candidate_a_au,
            "assumed_mass_earth": 1.0,
        },
        "ensemble": {
            "runs": runs,
            "integration_years_per_run": years,
            "samples_per_run": samples,
            "seed_base": seed_base,
        },
        "outcomes": {
            "survived_pilot_interval": survived,
            "did_not_survive_pilot_interval": runs - survived,
            "survival_fraction": survived / runs if runs else 0.0,
            "survived_with_strong_perturbation": strongly_perturbed,
            "survived_with_measurable_perturbation": measurable,
            "maximum_eccentricity_seen": max_e,
            "maximum_semimajor_drift_fraction_seen": max_drift,
        },
        "runs": [asdict(r) for r in results],
        "model_scope": {
            "host_and_confirmed_planets": "included",
            "H01": "included",
            "BC_pair": "replaced by combined barycentric perturber",
            "outer_semimajor_axis_basis": "Keplerian estimate from approximate 250-year literature period",
            "unknown_orbital_angles": "sampled",
            "unknown_outer_eccentricity": "uniform 0.00–0.45 exploratory prior",
        },
        "limitations": [
            "100-year pilot is short relative to the age of the system",
            "the internal B-C binary is unresolved",
            "outer stellar orbital elements are incompletely constrained in the project dataset",
            "planetary parameter uncertainties are not yet sampled from measurement posteriors",
            "no tides, relativity, stellar mass loss, atmosphere, or climate coupling",
            "survived means survived this pilot integration only; it does not mean long-term stable",
        ],
        "next_model": "resolve B and C individually, ingest astrometric/orbital posteriors, and expand to long-term Monte Carlo ensembles",
    }


def dumps_ensemble(dataset: dict[str, Any], **kwargs: Any) -> str:
    return json.dumps(run_ensemble(dataset, **kwargs), indent=2)
