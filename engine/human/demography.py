#!/usr/bin/env python3
"""Time-dependent demographic scaffold for TRISOLARIS LAB.

The model operates on normalized population indices, not census predictions.
It is designed to show expansion, bottlenecks, recovery and technology
dependence across named population regions.

Disturbances are explicit user scenarios. They are never inserted
automatically.
"""

from __future__ import annotations

import math
from typing import Any


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _logistic(p0: float, capacity: float, rate: float, years: float) -> float:
    if capacity <= 0:
        return 0.0
    p0 = max(1e-6, min(capacity, p0))
    if years <= 0:
        return p0
    ratio = (capacity - p0) / p0
    return capacity / (1.0 + ratio * math.exp(-rate * years))


def _disturbance_vulnerability(population: dict[str, Any], event_type: str) -> float:
    if event_type == "drought":
        return _clamp01(
            0.70 * (1.0 - float(population.get("water_recycling", 0.0)))
            + 0.30 * float(population.get("open_agriculture", 0.0))
        )
    if event_type == "cold":
        return _clamp01(1.0 - float(population.get("thermal_shelter", 0.0)))
    if event_type == "food":
        food_capacity = max(
            float(population.get("open_agriculture", 0.0)),
            float(population.get("controlled_agriculture", 0.0)),
        )
        return _clamp01(1.0 - food_capacity)
    if event_type == "infrastructure":
        dependence = max(
            float(population.get("infrastructure", 0.0)),
            float(population.get("controlled_agriculture", 0.0)),
            float(population.get("water_recycling", 0.0)),
        )
        continuity = float(population.get("knowledge_continuity", 0.0))
        return _clamp01(0.75 * dependence + 0.25 * (1.0 - continuity))
    return 0.0


def simulate_demography(
    planetary_history: dict[str, Any],
    *,
    total_years: float,
    view_years: float | None = None,
    disturbance: str = "none",
    severity: float = 0.0,
    disturbance_fraction: float = 0.55,
) -> dict[str, Any]:
    if total_years < 0:
        raise ValueError("total_years cannot be negative")
    if view_years is None:
        view_years = total_years
    view_years = max(0.0, min(float(view_years), float(total_years)))
    severity = _clamp01(float(severity))
    disturbance_fraction = _clamp01(float(disturbance_fraction))

    if disturbance not in {"none", "drought", "cold", "food", "infrastructure"}:
        raise ValueError("unsupported disturbance")

    event_year = total_years * disturbance_fraction
    population_rows = []
    events = []

    for population in planetary_history.get("populations", []):
        share = max(1e-6, float(population.get("relative_capacity_share", 0.0)))
        settlement = _clamp01(float(population.get("settlement_intensity", 0.0)))
        open_ag = _clamp01(float(population.get("open_agriculture", 0.0)))
        controlled_ag = _clamp01(float(population.get("controlled_agriculture", 0.0)))
        infrastructure = _clamp01(float(population.get("infrastructure", 0.0)))
        mobility = _clamp01(float(population.get("mobility_network", 0.0)))
        continuity = _clamp01(float(population.get("knowledge_continuity", 0.0)))

        food_support = max(open_ag, controlled_ag)
        carrying_capacity = max(
            5.0,
            1000.0
            * share
            * (0.40 + 0.60 * settlement)
            * (0.45 + 0.55 * food_support)
        )
        founder_index = max(2.0, min(carrying_capacity * 0.35, 60.0 * share + 2.0))
        growth_rate = 0.00018 + 0.00042 * settlement + 0.00012 * food_support

        baseline_now = _logistic(founder_index, carrying_capacity, growth_rate, view_years)
        baseline_event = _logistic(founder_index, carrying_capacity, growth_rate, event_year)

        vulnerability = _disturbance_vulnerability(population, disturbance)
        shock_fraction = _clamp01(0.68 * severity * vulnerability)
        population_now = baseline_now
        bottleneck = False
        recovery_fraction = 1.0

        if disturbance != "none" and view_years >= event_year:
            post_shock = max(0.5, baseline_event * (1.0 - shock_fraction))
            elapsed_after = view_years - event_year

            resilience = _clamp01(
                0.34 * continuity
                + 0.26 * mobility
                + 0.20 * infrastructure
                + 0.20 * (0.5 * open_ag + 0.5 * controlled_ag)
            )
            recovery_rate = 0.00010 + 0.00055 * resilience
            recovery_capacity = carrying_capacity * (1.0 - 0.25 * shock_fraction)
            population_now = _logistic(
                min(post_shock, recovery_capacity),
                max(post_shock, recovery_capacity),
                recovery_rate,
                elapsed_after,
            )
            bottleneck = shock_fraction >= 0.30
            recovery_fraction = _clamp01(
                (population_now - post_shock)
                / max(1e-6, baseline_event - post_shock)
            )

            events.append({
                "type": disturbance,
                "year": event_year,
                "lineage_id": population["lineage_id"],
                "refuge_name": population["refuge_name"],
                "severity": severity,
                "vulnerability": vulnerability,
                "label": f"{population['refuge_name']}: {disturbance} scenario",
            })
            if bottleneck:
                events.append({
                    "type": "bottleneck",
                    "year": event_year,
                    "lineage_id": population["lineage_id"],
                    "refuge_name": population["refuge_name"],
                    "severity": shock_fraction,
                    "label": f"{population['refuge_name']}: demographic bottleneck",
                })

        population_ratio = population_now / max(1e-6, carrying_capacity)
        baseline_ratio = baseline_now / max(1e-6, carrying_capacity)
        trend = population_now - (
            _logistic(founder_index, carrying_capacity, growth_rate, max(0.0, view_years - max(50.0, total_years * 0.01)))
            if disturbance == "none" or view_years < event_year
            else max(0.5, baseline_event * (1.0 - shock_fraction))
        )

        if population_ratio < 0.12:
            status = "collapse"
        elif bottleneck and recovery_fraction < 0.35:
            status = "bottleneck"
        elif trend > carrying_capacity * 0.015:
            status = "expansion"
        elif trend < -carrying_capacity * 0.015:
            status = "decline"
        else:
            status = "stable"

        reserve_proxy = _clamp01(
            0.44 * food_support
            + 0.24 * continuity
            + 0.18 * infrastructure
            + 0.14 * mobility
        )

        population_rows.append({
            "lineage_id": population["lineage_id"],
            "lineage_name": population["lineage_name"],
            "refuge_name": population["refuge_name"],
            "population_index": population_now,
            "baseline_population_index": baseline_now,
            "carrying_capacity_index": carrying_capacity,
            "capacity_fraction": population_ratio,
            "baseline_capacity_fraction": baseline_ratio,
            "reserve_proxy": reserve_proxy,
            "disturbance_vulnerability": vulnerability,
            "bottleneck": bottleneck,
            "recovery_fraction": recovery_fraction,
            "status": status,
        })

    total_population = sum(p["population_index"] for p in population_rows)
    total_capacity = sum(p["carrying_capacity_index"] for p in population_rows)
    weighted_reserve = (
        sum(p["reserve_proxy"] * p["population_index"] for p in population_rows)
        / max(1e-6, total_population)
        if population_rows else 0.0
    )

    return {
        "model": "time_dependent_demography_v0.1",
        "epistemic_level": "MODELED",
        "inputs": {
            "total_years": total_years,
            "view_years": view_years,
            "disturbance": disturbance,
            "severity": severity,
            "disturbance_fraction": disturbance_fraction,
            "disturbance_year": event_year,
        },
        "populations": population_rows,
        "events": sorted(events, key=lambda item: item["year"]),
        "summary": {
            "population_index_total": total_population,
            "carrying_capacity_index_total": total_capacity,
            "capacity_fraction_global": (
                total_population / max(1e-6, total_capacity)
                if total_capacity > 0 else 0.0
            ),
            "reserve_proxy_weighted": weighted_reserve,
            "bottleneck_count": sum(1 for p in population_rows if p["bottleneck"]),
            "collapse_count": sum(1 for p in population_rows if p["status"] == "collapse"),
        },
        "limitations": [
            "normalized population indices, not census forecasts",
            "single deterministic disturbance scenario at a user-selected severity",
            "logistic growth is a coarse demographic scaffold",
            "no age structure, disease, fertility schedule or explicit mortality table yet",
            "no political or cultural ranking is inferred",
        ],
        "next_model": "age structure, migration flows through time, repeated shocks, recolonization and off-world demography",
    }
