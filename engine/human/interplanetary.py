#!/usr/bin/env python3
"""Interplanetary settlement layer for TRISOLARIS LAB.

Phase 9 connects persistent modeled populations to the other known worlds in
LTT 1445 A without assuming that migration, survival, colonization, or
evolution must occur. The model separates observed world properties from
derived transfer and settlement proxies.
"""

from __future__ import annotations

import math
from typing import Any


EARTH_YEAR_DAYS = 365.25


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _hohmann_transfer_days(origin_au: float, target_au: float, star_mass_solar: float) -> float:
    """Idealized coplanar circular Hohmann half-period in days."""
    if origin_au <= 0 or target_au <= 0 or star_mass_solar <= 0:
        raise ValueError("orbital distances and stellar mass must be positive")
    transfer_axis = 0.5 * (origin_au + target_au)
    years = 0.5 * math.sqrt((transfer_axis ** 3) / star_mass_solar)
    return years * EARTH_YEAR_DAYS


def _gravity_proxy(mass_earth: float | None, radius_earth: float | None) -> float | None:
    if not mass_earth or not radius_earth or radius_earth <= 0:
        return None
    return float(mass_earth) / (float(radius_earth) ** 2)


def _thermal_support(eq_temperature_k: float | None) -> float:
    if eq_temperature_k is None:
        return 0.0
    # Broad thermal screening only. Equilibrium temperature is not surface temperature.
    return math.exp(-((float(eq_temperature_k) - 288.0) / 95.0) ** 2)


def _gravity_support(gravity_earth: float | None) -> float:
    if gravity_earth is None:
        return 0.45
    return math.exp(-((float(gravity_earth) - 1.0) / 0.70) ** 2)


def build_world_catalog(system_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Build destinations while preserving epistemic provenance."""
    star_a = next(
        (star for star in system_data.get("stars", []) if star.get("id") == "A"),
        {},
    )
    star_mass = float(star_a.get("mass_solar", 0.257))
    origin = system_data.get("hypothetical_experiment", {})
    origin_axis = float(origin.get("semi_major_axis_au", 0.09))

    worlds = [{
        "world_id": origin.get("id", "H-01"),
        "name": origin.get("name", "TRISOLARIS H-01"),
        "role": "origin",
        "host": origin.get("host", "LTT 1445 A"),
        "semi_major_axis_au": origin_axis,
        "epistemic_level": origin.get("epistemic_level", "SPECULATIVE"),
        "source": "TRISOLARIS experimental world",
        "transfer_days_from_h01": 0.0,
        "equilibrium_temperature_k": None,
        "gravity_earth": None,
        "thermal_support_proxy": None,
        "gravity_support_proxy": None,
        "settlement_burden": 0.0,
        "controlled_habitat_required": False,
        "assessment": "modeled origin world; conditions come from the interactive experiment",
    }]

    for index, planet in enumerate(system_data.get("observed_planets", []), start=1):
        teq = planet.get("equilibrium_temperature_k")
        gravity = _gravity_proxy(planet.get("mass_earth"), planet.get("radius_earth"))
        thermal = _thermal_support(teq)
        gravity_score = _gravity_support(gravity)

        # Unknown atmosphere is treated as uncertainty, never silently assumed Earth-like.
        atmosphere_uncertainty = 0.28
        settlement_burden = _clamp01(
            0.56 * (1.0 - thermal)
            + 0.16 * (1.0 - gravity_score)
            + atmosphere_uncertainty
        )
        controlled = settlement_burden >= 0.55 or (teq is not None and float(teq) >= 360.0)

        if controlled:
            assessment = (
                "natural surface settlement is not supported by this screening; "
                "a controlled habitat is required in the model"
            )
        else:
            assessment = (
                "surface conditions remain uncertain and require atmospheric and climate evidence"
            )

        worlds.append({
            "world_id": f"OBS-{index}",
            "name": planet.get("name", f"Observed world {index}"),
            "role": "destination",
            "host": planet.get("host", "LTT 1445 A"),
            "semi_major_axis_au": float(planet["semi_major_axis_au"]),
            "epistemic_level": planet.get("epistemic_level", "OBSERVED"),
            "source": planet.get("source", "NASA Exoplanet Archive"),
            "transfer_days_from_h01": _hohmann_transfer_days(
                origin_axis,
                float(planet["semi_major_axis_au"]),
                star_mass,
            ),
            "equilibrium_temperature_k": teq,
            "gravity_earth": gravity,
            "thermal_support_proxy": thermal,
            "gravity_support_proxy": gravity_score,
            "settlement_burden": settlement_burden,
            "controlled_habitat_required": controlled,
            "assessment": assessment,
        })

    return worlds


def _society_readiness(society: dict[str, Any]) -> float:
    portfolio = society.get("technology_portfolio", {})
    infrastructure = _clamp01(portfolio.get("infrastructure", 0.0))
    mobility = _clamp01(portfolio.get("mobility", 0.0))
    return _clamp01(
        0.27 * _clamp01(society.get("technical_balance", 0.0))
        + 0.23 * _clamp01(society.get("knowledge_retention", 0.0))
        + 0.22 * _clamp01(society.get("system_redundancy", 0.0))
        + 0.18 * infrastructure
        + 0.10 * mobility
    )


def simulate_interplanetary_settlement(
    system_data: dict[str, Any],
    astroanthropology: dict[str, Any],
    *,
    years: float,
    founder_size: int = 500,
    exchange_strength: float = 0.30,
    launch_active: bool = True,
) -> dict[str, Any]:
    """Evaluate same-system dispersal from H-01 to observed LTT 1445 A worlds."""
    if years < 0:
        raise ValueError("years cannot be negative")
    if founder_size < 2:
        raise ValueError("founder_size must be at least 2")

    exchange_strength = _clamp01(exchange_strength)
    worlds = build_world_catalog(system_data)
    destinations = [world for world in worlds if world["role"] == "destination"]

    attempts: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []

    for society in astroanthropology.get("societies", []):
        readiness = _society_readiness(society)
        knowledge = _clamp01(society.get("knowledge_retention", 0.0))
        redundancy = _clamp01(society.get("system_redundancy", 0.0))
        technical = _clamp01(society.get("technical_balance", 0.0))

        for world in destinations:
            burden = _clamp01(world["settlement_burden"])
            launch_threshold = 0.34 + 0.08 * burden
            launch_feasible = readiness >= launch_threshold

            transfer_survival = _clamp01(
                0.50
                + 0.22 * readiness
                + 0.14 * knowledge
                + 0.14 * redundancy
                - 0.30 * burden
            )
            if not launch_active or not launch_feasible:
                survivors = 0
            else:
                survivors = max(0, int(round(founder_size * transfer_survival)))

            effective_founders = int(round(survivors * (0.48 + 0.22 * redundancy))) if survivors else 0

            habitat_capacity = _clamp01(
                0.34 * readiness
                + 0.26 * technical
                + 0.22 * redundancy
                + 0.18 * knowledge
                - 0.34 * burden
            )
            persists = bool(
                launch_active
                and launch_feasible
                and survivors >= 40
                and habitat_capacity >= 0.16
            )

            if persists:
                contact_capacity = _clamp01(
                    exchange_strength * (0.42 + 0.38 * readiness + 0.20 * technical)
                )
                isolation = _clamp01(1.0 - contact_capacity)
                gene_flow = _clamp01(
                    contact_capacity
                    * min(1.0, survivors / max(100.0, founder_size))
                    * (0.60 + 0.40 * redundancy)
                )
                founder_effect = _clamp01(
                    math.sqrt(120.0 / max(120.0, float(effective_founders)))
                    * (1.0 - 0.45 * gene_flow)
                )
                time_factor = 1.0 - math.exp(-years / 18_000.0) if years else 0.0
                divergence = _clamp01(
                    time_factor
                    * isolation
                    * (0.48 * founder_effect + 0.32 * burden + 0.20 * (1.0 - gene_flow))
                )
                technology_continuity = _clamp01(
                    0.46 * knowledge
                    + 0.30 * technical
                    + 0.24 * redundancy
                    - 0.26 * burden
                    + 0.20 * contact_capacity
                )
            else:
                contact_capacity = 0.0
                isolation = 0.0
                gene_flow = 0.0
                founder_effect = 0.0
                divergence = 0.0
                technology_continuity = 0.0

            branch_emerges = bool(
                persists
                and years >= 5_000
                and isolation >= 0.48
                and divergence >= 0.34
            )
            branch_id = (
                f"{society.get('lineage_id', 'L?')}-{world['world_id']}"
                if branch_emerges else None
            )

            if not launch_active:
                status = "assessment-only"
            elif not launch_feasible:
                status = "launch-not-feasible"
            elif survivors < 40:
                status = "transfer-bottleneck"
            elif not persists:
                status = "settlement-failed"
            elif branch_emerges:
                status = "persistent-offworld-branch"
            else:
                status = "persistent-settlement"

            attempt = {
                "population_alias": society.get("population_alias", society.get("lineage_id", "population")),
                "lineage_id": society.get("lineage_id"),
                "destination_id": world["world_id"],
                "destination_name": world["name"],
                "status": status,
                "years": years,
                "founder_size": founder_size,
                "launch_readiness": readiness,
                "launch_threshold": launch_threshold,
                "launch_feasible": launch_feasible,
                "transfer_days": world["transfer_days_from_h01"],
                "transfer_survival_fraction": transfer_survival if launch_feasible else 0.0,
                "arrival_survivors": survivors,
                "effective_founders": effective_founders,
                "settlement_burden": burden,
                "habitat_capacity": habitat_capacity,
                "settlement_persists": persists,
                "post_settlement_contact": contact_capacity,
                "isolation": isolation,
                "gene_flow": gene_flow,
                "founder_effect_pressure": founder_effect,
                "divergence_proxy": divergence,
                "technology_continuity": technology_continuity,
                "offworld_branch_emerges": branch_emerges,
                "offworld_branch_id": branch_id,
            }
            attempts.append(attempt)

            if persists:
                events.append({
                    "type": "offworld-settlement",
                    "lineage_id": society.get("lineage_id"),
                    "destination_id": world["world_id"],
                    "label": f"{attempt['population_alias']} maintains a settlement on {world['name']}",
                })
            if branch_emerges:
                events.append({
                    "type": "offworld-lineage-branch",
                    "lineage_id": society.get("lineage_id"),
                    "destination_id": world["world_id"],
                    "branch_id": branch_id,
                    "label": f"{attempt['population_alias']} develops a persistent off-world lineage branch",
                })

    persistent = [attempt for attempt in attempts if attempt["settlement_persists"]]
    branches = [attempt for attempt in attempts if attempt["offworld_branch_emerges"]]

    return {
        "model": "interplanetary_settlement_v0.1",
        "epistemic_level": "MODELED",
        "inputs": {
            "years": years,
            "founder_size": founder_size,
            "exchange_strength": exchange_strength,
            "launch_active": bool(launch_active),
        },
        "worlds": worlds,
        "attempts": attempts,
        "events": events,
        "summary": {
            "destination_count": len(destinations),
            "population_count": len(astroanthropology.get("societies", [])),
            "attempt_count": len(attempts),
            "launch_feasible_count": sum(1 for attempt in attempts if attempt["launch_feasible"]),
            "persistent_settlement_count": len(persistent),
            "offworld_branch_count": len(branches),
        },
        "limitations": [
            "transfer time uses an idealized coplanar circular Hohmann half-period and excludes escape/capture maneuvers",
            "equilibrium temperature is not surface temperature and no Earth-like atmosphere is assumed",
            "settlement burden, survival, contact, gene flow and divergence are exploratory modeled proxies",
            "population_index from earlier phases is not interpreted as a literal headcount; founder_size is explicit",
            "an off-world lineage branch is not a new species and does not imply anatomical change",
            "migration, settlement persistence and lineage divergence can all fail to occur",
        ],
    }
