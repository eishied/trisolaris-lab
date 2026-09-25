#!/usr/bin/env python3
"""Persistent off-world divergence model for TRISOLARIS LAB Phase 9.2."""

from __future__ import annotations

import math
from typing import Any


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def simulate_offworld_divergence(
    interplanetary: dict[str, Any],
    network: dict[str, Any],
    *,
    years: float,
    generation_years: float = 28.0,
) -> dict[str, Any]:
    """Estimate conditional divergence after a settlement has its own history."""
    if years < 0:
        raise ValueError("years cannot be negative")
    if generation_years <= 0:
        raise ValueError("generation_years must be positive")

    worlds = {
        world["world_id"]: world
        for world in interplanetary.get("worlds", [])
    }
    attempts = {
        (attempt.get("lineage_id"), attempt.get("destination_id")): attempt
        for attempt in interplanetary.get("attempts", [])
    }

    branches: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    generations = years / generation_years if generation_years else 0.0

    for colony in network.get("colonies", []):
        if not colony.get("active"):
            continue

        key = (colony.get("lineage_id"), colony.get("destination_id"))
        attempt = attempts.get(key, {})
        world = worlds.get(colony.get("destination_id"), {})

        population = max(1.0, float(colony.get("population", 1.0)))
        founder_ne = max(20.0, float(attempt.get("effective_founders", 20.0)))
        effective_population = max(
            founder_ne,
            population
            * (0.38 + 0.22 * _clamp01(colony.get("resource_margin", 0.0))),
        )

        network_contact = _clamp01(
            0.55 * colony.get("post_settlement_contact", 0.0)
            + 0.45 * colony.get("resupply_strength", 0.0)
        )
        gene_flow = _clamp01(
            attempt.get("gene_flow", 0.0)
            + 0.40 * network_contact
        )

        drift = _clamp01(
            (1.0 - math.exp(-generations / (2.0 * effective_population)))
            * (1.0 - 0.65 * gene_flow)
        )

        gravity = world.get("gravity_earth")
        gravity_difference = min(1.0, abs(float(gravity) - 1.0)) if gravity is not None else 0.25
        environmental_difference = _clamp01(
            0.52 * colony.get("settlement_burden", 0.0)
            + 0.20 * gravity_difference
            + 0.28 * (1.0 - colony.get("habitat_capacity", 0.0))
        )

        # Controlled habitats buffer direct external selection; infrastructure
        # failure exposes the population more strongly to destination pressures.
        exposure = _clamp01(
            0.25
            + 0.75 * (1.0 - colony.get("infrastructure_integrity", 0.0))
        )
        selection_pressure = _clamp01(environmental_difference * exposure)

        founder_effect = _clamp01(attempt.get("founder_effect_pressure", 0.0))
        technical_divergence = _clamp01(
            0.45 * colony.get("self_sufficiency", 0.0)
            + 0.35 * (1.0 - network_contact)
            + 0.20 * colony.get("supply_dependency", 0.0)
        )

        time_factor = 1.0 - math.exp(-years / 25_000.0) if years else 0.0
        divergence = _clamp01(
            time_factor
            * (
                0.34 * drift
                + 0.30 * selection_pressure
                + 0.22 * founder_effect
                + 0.14 * technical_divergence
            )
        )

        if gene_flow >= 0.45:
            continuity = "high-contact continuity"
        elif divergence >= 0.42 and gene_flow < 0.22:
            continuity = "persistent isolated branch"
        elif divergence >= 0.24:
            continuity = "diverging off-world branch"
        else:
            continuity = "connected off-world population"

        lineage_branch = bool(
            years >= 5_000
            and divergence >= 0.24
            and gene_flow < 0.40
        )

        branch = {
            "branch_id": f"{colony.get('lineage_id')}-{colony.get('destination_id')}",
            "parent_lineage_id": colony.get("lineage_id"),
            "population_alias": colony.get("population_alias"),
            "destination_id": colony.get("destination_id"),
            "destination_name": colony.get("destination_name"),
            "active_population": population,
            "effective_population": effective_population,
            "generations": generations,
            "gene_flow": gene_flow,
            "drift_pressure": drift,
            "environmental_difference": environmental_difference,
            "selection_pressure": selection_pressure,
            "founder_effect_pressure": founder_effect,
            "technical_divergence": technical_divergence,
            "divergence_proxy": divergence,
            "continuity_state": continuity,
            "lineage_branch_emerges": lineage_branch,
            "species_claim": False,
            "anatomical_change_inferred": False,
        }
        branches.append(branch)

        if lineage_branch:
            events.append({
                "type": "offworld-divergence",
                "branch_id": branch["branch_id"],
                "label": f"{colony.get('population_alias')} develops a persistent off-world lineage history on {colony.get('destination_name')}",
            })

    return {
        "model": "offworld_divergence_v0.1",
        "epistemic_level": "MODELED",
        "inputs": {
            "years": years,
            "generation_years": generation_years,
        },
        "branches": branches,
        "events": events,
        "summary": {
            "active_branch_population_count": len(branches),
            "persistent_lineage_branch_count": sum(
                1 for branch in branches if branch["lineage_branch_emerges"]
            ),
            "mean_divergence_proxy": (
                sum(branch["divergence_proxy"] for branch in branches) / len(branches)
                if branches else 0.0
            ),
            "mean_gene_flow": (
                sum(branch["gene_flow"] for branch in branches) / len(branches)
                if branches else 0.0
            ),
        },
        "limitations": [
            "divergence is a reduced-order proxy and not a genomic simulation",
            "no new species is asserted by this model",
            "no anatomical feature is inferred without a separate explicit physiology/genetics model",
            "selection pressure is buffered by controlled habitats and depends on infrastructure continuity",
            "future SLiM integration should replace aggregate drift and selection proxies",
        ],
    }
