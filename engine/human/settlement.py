#!/usr/bin/env python3
"""Regional human-settlement support model.

This module estimates environmental compatibility for a generic human
population. It is not medical advice, not a clinical physiology simulator,
and not a demographic prediction.

The model separates:
- natural environmental support,
- technology-assisted support,
- technology dependency,
- agricultural potential,
- regional environmental stress.

Technology can buffer some environmental limits, but never erases them and
does not trigger biological evolution automatically.
"""

from __future__ import annotations

import math
from typing import Any


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _bell(value: float, center: float, width: float) -> float:
    return math.exp(-0.5 * ((value - center) / max(width, 1e-6)) ** 2)


def _oxygen_support(partial_pressure_bar: float) -> float:
    """Broad, non-clinical oxygen-availability proxy."""
    if partial_pressure_bar <= 0:
        return 0.0
    low = 1.0 / (1.0 + math.exp(-(partial_pressure_bar - 0.13) / 0.025))
    high_penalty = 1.0 / (1.0 + math.exp((partial_pressure_bar - 0.34) / 0.04))
    return _clamp01(low * high_penalty)


def _pressure_support(pressure_bar: float) -> float:
    """Broad total-pressure compatibility proxy."""
    if pressure_bar <= 0:
        return 0.0
    low = 1.0 / (1.0 + math.exp(-(pressure_bar - 0.45) / 0.12))
    high = 1.0 / (1.0 + math.exp((pressure_bar - 2.6) / 0.45))
    return _clamp01(low * high)


def _thermal_support(temp_c: float) -> float:
    """Environmental thermal-comfort proxy before shelter/clothing support."""
    return _clamp01(_bell(temp_c, 18.0, 18.0))


def _technology_buffer(base: float, technology: float, ceiling: float) -> float:
    """Move a stressed support factor toward a bounded ceiling."""
    technology = _clamp01(technology)
    return _clamp01(base + technology * (ceiling - base))


def evaluate_settlement_support(
    surface: dict[str, Any],
    food_web: dict[str, Any],
    *,
    pressure_bar: float,
    oxygen_fraction: float,
    technology_support: float = 0.40,
    nutrient_availability: float = 1.0,
) -> dict[str, Any]:
    if pressure_bar <= 0:
        raise ValueError("pressure_bar must be positive")
    if not 0.0 <= oxygen_fraction <= 0.40:
        raise ValueError("oxygen_fraction must be between 0 and 0.40")

    tech = _clamp01(technology_support)
    p_o2 = pressure_bar * oxygen_fraction
    oxygen = _oxygen_support(p_o2)
    pressure = _pressure_support(pressure_bar)

    producer_support = 0.0
    consumer_support = 0.0
    for guild in food_web.get("guilds", []):
        gid = guild.get("id")
        support = float(guild.get("support_potential", 0.0))
        if gid in {"primary_producers", "aquatic_primary"}:
            producer_support = max(producer_support, support)
        if gid in {"grazers", "aquatic_consumers"}:
            consumer_support = max(consumer_support, support)

    nutrient_factor = _clamp01(1.0 - math.exp(-max(0.0, nutrient_availability)))
    environmental_food = _clamp01(
        0.72 * producer_support
        + 0.18 * consumer_support
        + 0.10 * nutrient_factor
    )

    bands = []
    total_weight = 0.0
    natural_sum = 0.0
    assisted_sum = 0.0
    agriculture_sum = 0.0
    viable_weight = 0.0
    natural_viable_weight = 0.0

    for row in surface["bands"]:
        lat = float(row["latitude_deg"])
        temp_c = float(row["temperature_c"])
        water = _clamp01(float(row["liquid_water_proxy"]))
        hydro = _clamp01(float(row["hydrological_cycle_proxy"]))
        productivity = _clamp01(float(row["productivity_potential"]))

        weight = max(0.0, math.cos(math.radians(lat)))
        total_weight += weight

        thermal = _thermal_support(temp_c)
        natural_food = _clamp01(
            0.55 * productivity
            + 0.30 * environmental_food
            + 0.15 * hydro
        )

        # Geometric mean prevents a single severe bottleneck from being hidden
        # by strong scores elsewhere.
        natural_support = (
            max(1e-6, thermal)
            * max(1e-6, oxygen)
            * max(1e-6, pressure)
            * max(1e-6, water)
            * max(1e-6, natural_food)
        ) ** (1.0 / 5.0)

        thermal_assisted = _technology_buffer(thermal, tech, 0.93)
        oxygen_assisted = _technology_buffer(oxygen, tech, 0.90)
        pressure_assisted = _technology_buffer(pressure, tech, 0.90)
        water_assisted = _technology_buffer(water, tech, 0.92)
        food_assisted = _technology_buffer(natural_food, tech, 0.88)

        assisted_support = (
            max(1e-6, thermal_assisted)
            * max(1e-6, oxygen_assisted)
            * max(1e-6, pressure_assisted)
            * max(1e-6, water_assisted)
            * max(1e-6, food_assisted)
        ) ** (1.0 / 5.0)

        agriculture = _clamp01(
            productivity
            * water_assisted
            * (0.55 + 0.45 * nutrient_factor)
            * (0.65 + 0.35 * thermal_assisted)
        )

        dependency = _clamp01(assisted_support - natural_support)

        if assisted_support >= 0.70:
            state = "assisted-compatible"
        elif assisted_support >= 0.50:
            state = "refuge-only"
        elif assisted_support >= 0.30:
            state = "high-dependency"
        else:
            state = "incompatible"

        if natural_support >= 0.60:
            natural_state = "natural-compatible"
        elif natural_support >= 0.40:
            natural_state = "natural-marginal"
        else:
            natural_state = "natural-hostile"

        natural_sum += weight * natural_support
        assisted_sum += weight * assisted_support
        agriculture_sum += weight * agriculture
        if assisted_support >= 0.50:
            viable_weight += weight
        if natural_support >= 0.60:
            natural_viable_weight += weight

        bands.append({
            "latitude_deg": lat,
            "temperature_c": temp_c,
            "natural_support": natural_support,
            "assisted_support": assisted_support,
            "technology_dependency": dependency,
            "agriculture_potential": agriculture,
            "state": state,
            "natural_state": natural_state,
            "stress_components": {
                "thermal": 1.0 - thermal,
                "oxygen": 1.0 - oxygen,
                "pressure": 1.0 - pressure,
                "water": 1.0 - water,
                "food": 1.0 - natural_food,
            },
        })

    total_weight = total_weight or 1.0
    natural_mean = natural_sum / total_weight
    assisted_mean = assisted_sum / total_weight
    dependency_mean = max(0.0, assisted_mean - natural_mean)
    viable_fraction = viable_weight / total_weight
    natural_viable_fraction = natural_viable_weight / total_weight

    if natural_viable_fraction >= 0.45:
        settlement_state = "broad natural settlement potential"
    elif viable_fraction >= 0.45:
        settlement_state = "broad technology-assisted settlement potential"
    elif viable_fraction >= 0.12:
        settlement_state = "regional refugia with technology dependence"
    else:
        settlement_state = "little settlement potential under current assumptions"

    return {
        "model": "human_settlement_support_v0.1",
        "epistemic_level": "MODELED",
        "inputs": {
            "pressure_bar": pressure_bar,
            "oxygen_fraction": oxygen_fraction,
            "oxygen_partial_pressure_bar": p_o2,
            "technology_support": tech,
            "nutrient_availability_relative": nutrient_availability,
        },
        "summary": {
            "natural_support_mean": natural_mean,
            "assisted_support_mean": assisted_mean,
            "technology_dependency_mean": dependency_mean,
            "agriculture_potential_mean": agriculture_sum / total_weight,
            "assisted_viable_area_fraction": viable_fraction,
            "natural_viable_area_fraction": natural_viable_fraction,
            "settlement_state": settlement_state,
        },
        "bands": bands,
        "limitations": [
            "generic population model; no individual medical prediction",
            "does not model age, disease, pregnancy, acclimatization, genetics, or anatomy",
            "oxygen and pressure are broad environmental support proxies",
            "technology is a generic support index, not a specific life-support design",
            "agriculture is potential only and does not include crops, soils, pests, seasons, or logistics",
            "no demography, migration, culture, governance, or evolution yet",
            "technology improves survival support but does not automatically create biological adaptation",
        ],
        "next_model": "demography, migration, settlement networks, agriculture systems, and population-level evolutionary pressures",
    }
