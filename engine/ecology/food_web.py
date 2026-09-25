#!/usr/bin/env python3
"""Ecological guild and food-web support model.

This model does not create species automatically. It estimates whether the
current planetary surface conditions could support broad ecological guilds if
life were present or experimentally seeded.

Outputs are support potentials, not actual biomass and not evidence of life.
"""

from __future__ import annotations

import math
from typing import Any


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _oxygen_support(oxygen_fraction: float, midpoint: float, width: float) -> float:
    """Smooth oxygen-dependence proxy for increasingly aerobic guilds."""
    x = (oxygen_fraction - midpoint) / max(width, 1e-6)
    return 1.0 / (1.0 + math.exp(-x))


def evaluate_food_web(
    surface: dict[str, Any],
    *,
    oxygen_fraction: float = 0.21,
    nutrient_availability: float = 1.0,
    life_seeded: bool = False,
) -> dict[str, Any]:
    if oxygen_fraction < 0.0 or oxygen_fraction > 0.40:
        raise ValueError("oxygen_fraction must be between 0 and 0.40")
    if nutrient_availability < 0.0:
        raise ValueError("nutrient_availability cannot be negative")

    summary = surface["summary"]

    liquid = _clamp01(float(summary["liquid_surface_proxy_area_fraction"]))
    productivity = _clamp01(float(summary["biosphere_productivity_potential"]))
    refugia = _clamp01(float(summary["thermal_hydrological_refugia_fraction"]))
    retention = _clamp01(float(summary["atmospheric_retention_proxy"]))
    hydro = _clamp01(float(summary["hydrological_cycle_strength"]))
    nutrient = _clamp01(1.0 - math.exp(-max(0.0, nutrient_availability)))

    anaerobic = _clamp01(
        0.20
        + 0.35 * refugia
        + 0.20 * liquid
        + 0.15 * retention
        + 0.10 * nutrient
    )

    photo = _clamp01(
        productivity
        * (0.55 + 0.45 * nutrient)
        * (0.55 + 0.45 * hydro)
    )

    aquatic_primary = _clamp01(
        liquid
        * productivity
        * (0.50 + 0.50 * nutrient)
    )

    decomposers = _clamp01(
        math.sqrt(max(0.0, photo * max(0.05, hydro)))
        * (0.55 + 0.45 * nutrient)
    )

    aerobic_microbes = _clamp01(
        anaerobic
        * _oxygen_support(oxygen_fraction, 0.005, 0.004)
        * (0.65 + 0.35 * retention)
    )

    grazers = _clamp01(
        photo
        * _oxygen_support(oxygen_fraction, 0.025, 0.015)
        * (0.60 + 0.40 * refugia)
    )

    aquatic_consumers = _clamp01(
        aquatic_primary
        * _oxygen_support(oxygen_fraction, 0.02, 0.012)
        * (0.55 + 0.45 * liquid)
    )

    predators = _clamp01(
        max(grazers, aquatic_consumers)
        * productivity
        * _oxygen_support(oxygen_fraction, 0.10, 0.035)
    )

    large_aerobic = _clamp01(
        predators
        * _oxygen_support(oxygen_fraction, 0.16, 0.025)
        * (0.55 + 0.45 * retention)
    )

    guilds = [
        {
            "id": "anaerobic_microbes",
            "name": "Microbios anaerobios",
            "trophic_level": 0,
            "support_potential": anaerobic,
            "requires_seeded_life": True,
        },
        {
            "id": "aerobic_microbes",
            "name": "Microbios aerobios",
            "trophic_level": 0,
            "support_potential": aerobic_microbes,
            "requires_seeded_life": True,
        },
        {
            "id": "primary_producers",
            "name": "Productores primarios",
            "trophic_level": 1,
            "support_potential": photo,
            "requires_seeded_life": True,
        },
        {
            "id": "aquatic_primary",
            "name": "Productores acuáticos",
            "trophic_level": 1,
            "support_potential": aquatic_primary,
            "requires_seeded_life": True,
        },
        {
            "id": "decomposers",
            "name": "Descomponedores",
            "trophic_level": 1,
            "support_potential": decomposers,
            "requires_seeded_life": True,
        },
        {
            "id": "grazers",
            "name": "Consumidores primarios",
            "trophic_level": 2,
            "support_potential": grazers,
            "requires_seeded_life": True,
        },
        {
            "id": "aquatic_consumers",
            "name": "Consumidores acuáticos",
            "trophic_level": 2,
            "support_potential": aquatic_consumers,
            "requires_seeded_life": True,
        },
        {
            "id": "predators",
            "name": "Depredadores",
            "trophic_level": 3,
            "support_potential": predators,
            "requires_seeded_life": True,
        },
        {
            "id": "large_aerobic",
            "name": "Fauna aerobia grande",
            "trophic_level": 4,
            "support_potential": large_aerobic,
            "requires_seeded_life": True,
        },
    ]

    if large_aerobic >= 0.35:
        trophic_depth = 4
    elif predators >= 0.25:
        trophic_depth = 3
    elif max(grazers, aquatic_consumers) >= 0.25:
        trophic_depth = 2
    elif max(photo, aquatic_primary, decomposers) >= 0.20:
        trophic_depth = 1
    elif anaerobic >= 0.15:
        trophic_depth = 0
    else:
        trophic_depth = -1

    web_links = [
        {"source": "primary_producers", "target": "grazers", "efficiency_proxy": 0.10},
        {"source": "aquatic_primary", "target": "aquatic_consumers", "efficiency_proxy": 0.10},
        {"source": "grazers", "target": "predators", "efficiency_proxy": 0.10},
        {"source": "aquatic_consumers", "target": "predators", "efficiency_proxy": 0.10},
        {"source": "predators", "target": "decomposers", "efficiency_proxy": 0.20},
        {"source": "grazers", "target": "decomposers", "efficiency_proxy": 0.20},
        {"source": "primary_producers", "target": "decomposers", "efficiency_proxy": 0.15},
    ]

    supported = [
        guild["name"]
        for guild in guilds
        if guild["support_potential"] >= 0.25
    ]

    return {
        "model": "ecological_guild_support_v0.1",
        "epistemic_level": "MODELED",
        "inputs": {
            "oxygen_fraction": oxygen_fraction,
            "nutrient_availability_relative": nutrient_availability,
            "life_seeded": life_seeded,
        },
        "summary": {
            "environmental_trophic_depth_potential": trophic_depth,
            "supported_guilds_above_0_25": supported,
            "life_state": (
                "seeded experimental biosphere"
                if life_seeded
                else "environmental support only; life not assumed"
            ),
            "maximum_guild_support": max(
                (guild["support_potential"] for guild in guilds),
                default=0.0,
            ),
        },
        "guilds": guilds,
        "food_web_links": web_links,
        "limitations": [
            "does not model abiogenesis",
            "does not create species automatically",
            "guild support is not biomass",
            "oxygen thresholds are broad ecological proxies",
            "nutrient availability is a dimensionless exploratory control",
            "does not model genetics, evolution, disease, predation dynamics, or ecological succession",
            "no explicit carbon, nitrogen, phosphorus, or sulfur cycle yet",
        ],
        "next_model": "time-dependent ecosystem dynamics, nutrient cycles, explicit populations, and evolutionary branching",
    }
