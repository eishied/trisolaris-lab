#!/usr/bin/env python3
"""Functional culture/technology layer for TRISOLARIS LAB.

This model does not rank societies and does not assume a universal progress
ladder. It represents functional strategies that can be retained, exchanged,
lost or rebuilt as populations respond to environmental and demographic
conditions.
"""

from __future__ import annotations

import math
import re
from typing import Any


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _alias_for(refuge_name: str, lineage_id: str) -> str:
    """Stable narrative alias used only to distinguish modeled populations."""
    lower = refuge_name.lower()
    if "equat" in lower:
        root = "Aster"
    elif "bore" in lower or "nival" in lower or "frío" in lower:
        root = "Nival"
    elif "litor" in lower or "cost" in lower or "mare" in lower:
        root = "Mare"
    elif "cav" in lower or "sub" in lower or "umbra" in lower:
        root = "Umbra"
    elif "alt" in lower or "mont" in lower:
        root = "Bruma"
    else:
        root = "Nova"

    match = re.search(r"(\d+)$", refuge_name)
    suffix = match.group(1) if match else lineage_id.replace("L", "") or "1"
    return f"{root}-{suffix}"


def _agriculture_strategy(open_ag: float, controlled_ag: float) -> str:
    if max(open_ag, controlled_ag) < 0.18:
        return "low-intensity food production"
    if abs(open_ag - controlled_ag) <= 0.12:
        return "mixed open and controlled agriculture"
    if controlled_ag > open_ag:
        return "controlled-environment agriculture"
    return "open regional agriculture"


def _settlement_style(settlement: float, infrastructure: float) -> str:
    if infrastructure >= 0.65:
        return "connected settlement network"
    if settlement >= 0.60:
        return "persistent regional settlements"
    if settlement >= 0.30:
        return "dispersed permanent settlements"
    return "low-density occupation"


def _contact_state(exchange: float, differentiation: float) -> str:
    if exchange >= 0.55 and differentiation < 0.50:
        return "high-contact exchange network"
    if exchange >= 0.35:
        return "intermittent exchange network"
    if differentiation >= 0.72:
        return "strong local differentiation"
    return "limited but persistent contact"


def _knowledge_state(retention: float, loss_pressure: float, recovering: bool) -> str:
    if recovering and retention < 0.60:
        return "knowledge recovery in progress"
    if retention >= 0.72 and loss_pressure < 0.30:
        return "high continuity with redundancy"
    if retention >= 0.48:
        return "partial continuity"
    return "fragile continuity"


def _dominant_pressure(population: dict[str, Any], demography: dict[str, Any]) -> str:
    water_need = _clamp01(population.get("water_recycling", 0.0))
    thermal_need = _clamp01(population.get("thermal_shelter", 0.0))
    food_need = _clamp01(1.0 - max(
        population.get("open_agriculture", 0.0),
        population.get("controlled_agriculture", 0.0),
    ))
    demographic_need = _clamp01(
        (1.0 - demography.get("reserve_proxy", 0.0))
        + (0.25 if demography.get("bottleneck") else 0.0)
    )

    values = {
        "water continuity": water_need,
        "thermal exposure": thermal_need,
        "food reliability": food_need,
        "demographic continuity": demographic_need,
    }
    return max(values, key=values.get)


def simulate_astroanthropology(
    planetary_history: dict[str, Any],
    demography: dict[str, Any],
    *,
    years: float,
    exchange_strength: float = 1.0,
) -> dict[str, Any]:
    if years < 0:
        raise ValueError("years cannot be negative")
    exchange_strength = _clamp01(exchange_strength)

    demo_by_lineage = {
        row["lineage_id"]: row
        for row in demography.get("populations", [])
    }

    links_by_lineage: dict[str, list[dict[str, Any]]] = {}
    for link in planetary_history.get("migration_links", []):
        links_by_lineage.setdefault(link["source_lineage_id"], []).append(link)
        links_by_lineage.setdefault(link["target_lineage_id"], []).append(link)

    societies = []
    events = []

    for population in planetary_history.get("populations", []):
        lineage_id = population["lineage_id"]
        demo = demo_by_lineage.get(lineage_id, {})

        open_ag = _clamp01(population.get("open_agriculture", 0.0))
        controlled_ag = _clamp01(population.get("controlled_agriculture", 0.0))
        infrastructure = _clamp01(population.get("infrastructure", 0.0))
        mobility = _clamp01(population.get("mobility_network", 0.0))
        continuity = _clamp01(population.get("knowledge_continuity", 0.0))
        differentiation = _clamp01(population.get("cultural_differentiation_proxy", 0.0))
        water = _clamp01(population.get("water_recycling", 0.0))
        thermal = _clamp01(population.get("thermal_shelter", 0.0))
        reserve = _clamp01(demo.get("reserve_proxy", 0.0))

        link_flow = sum(
            _clamp01(link.get("migration_flow", 0.0))
            for link in links_by_lineage.get(lineage_id, [])
        )
        exchange = _clamp01(
            exchange_strength * (0.55 * mobility + 0.45 * min(1.0, link_flow))
        )

        archive_capacity = _clamp01(
            continuity * (0.55 + 0.45 * infrastructure)
        )
        food_redundancy = _clamp01(
            min(open_ag, controlled_ag) * 1.7
            + 0.25 * max(open_ag, controlled_ag)
        )
        system_redundancy = _clamp01(
            0.34 * food_redundancy
            + 0.24 * mobility
            + 0.24 * archive_capacity
            + 0.18 * reserve
        )

        dependence = _clamp01(
            0.28 * water
            + 0.25 * thermal
            + 0.27 * controlled_ag
            + 0.20 * infrastructure
        )

        bottleneck = bool(demo.get("bottleneck", False))
        status = demo.get("status", "stable")
        demographic_stress = {
            "collapse": 1.0,
            "bottleneck": 0.78,
            "decline": 0.52,
            "stable": 0.16,
            "expansion": 0.10,
        }.get(status, 0.22)

        retention = _clamp01(
            continuity
            * (0.74 + 0.26 * reserve)
            * (1.0 - 0.38 * demographic_stress)
        )
        transfer_gain = _clamp01(
            exchange * (0.38 + 0.62 * continuity)
        )
        loss_pressure = _clamp01(
            0.44 * demographic_stress
            + 0.32 * dependence * (1.0 - system_redundancy)
            + 0.24 * (1.0 - archive_capacity)
        )
        technical_balance = _clamp01(
            retention + 0.42 * transfer_gain - 0.58 * loss_pressure
        )

        agriculture_strategy = _agriculture_strategy(open_ag, controlled_ag)
        settlement_style = _settlement_style(
            _clamp01(population.get("settlement_intensity", 0.0)),
            infrastructure,
        )
        recovering = status in {"bottleneck", "decline"} and demo.get("recovery_fraction", 0.0) > 0.12

        society = {
            "lineage_id": lineage_id,
            "lineage_name": population.get("lineage_name", lineage_id),
            "refuge_name": population["refuge_name"],
            "population_alias": _alias_for(population["refuge_name"], lineage_id),
            "alias_rule": "stable narrative label only; not an inferred ethnonym",
            "dominant_pressure": _dominant_pressure(population, demo),
            "settlement_style": settlement_style,
            "agriculture_strategy": agriculture_strategy,
            "contact_state": _contact_state(exchange, differentiation),
            "knowledge_state": _knowledge_state(retention, loss_pressure, recovering),
            "technology_portfolio": {
                "water_management": water,
                "thermal_protection": thermal,
                "open_agriculture": open_ag,
                "controlled_agriculture": controlled_ag,
                "mobility": mobility,
                "infrastructure": infrastructure,
                "archives_and_knowledge": archive_capacity,
            },
            "knowledge_retention": retention,
            "knowledge_transfer": transfer_gain,
            "knowledge_loss_pressure": loss_pressure,
            "technical_balance": technical_balance,
            "system_redundancy": system_redundancy,
            "technology_dependence": dependence,
            "cultural_exchange": exchange,
            "cultural_differentiation": differentiation,
            "demographic_status": status,
            "population_index": demo.get("population_index", 0.0),
            "carrying_capacity_index": demo.get("carrying_capacity_index", 0.0),
        }
        societies.append(society)

        if loss_pressure >= 0.55:
            events.append({
                "type": "knowledge-loss-pressure",
                "lineage_id": lineage_id,
                "label": f"{society['population_alias']}: elevated knowledge-loss pressure",
            })
        if transfer_gain >= 0.40:
            events.append({
                "type": "knowledge-transfer",
                "lineage_id": lineage_id,
                "label": f"{society['population_alias']}: strong exchange channel",
            })
        if food_redundancy >= 0.50:
            events.append({
                "type": "food-redundancy",
                "lineage_id": lineage_id,
                "label": f"{society['population_alias']}: diversified food strategy",
            })

    def mean(key: str) -> float:
        if not societies:
            return 0.0
        return sum(float(s[key]) for s in societies) / len(societies)

    return {
        "model": "functional_astroanthropology_v0.1",
        "epistemic_level": "MODELED",
        "inputs": {
            "years": years,
            "exchange_strength": exchange_strength,
        },
        "societies": societies,
        "events": events,
        "summary": {
            "population_count": len(societies),
            "mean_knowledge_retention": mean("knowledge_retention"),
            "mean_knowledge_transfer": mean("knowledge_transfer"),
            "mean_knowledge_loss_pressure": mean("knowledge_loss_pressure"),
            "mean_system_redundancy": mean("system_redundancy"),
            "mean_technology_dependence": mean("technology_dependence"),
            "mean_cultural_exchange": mean("cultural_exchange"),
        },
        "limitations": [
            "functional strategy proxies, not predictions of real cultures",
            "population aliases are UI labels, not inferred ethnonyms",
            "no society is ranked as more advanced, superior or desirable",
            "technology can be retained, exchanged, lost or rebuilt; no linear progress ladder is assumed",
            "language, religion, political ideology and moral values are not inferred",
            "institutions, conflict and economics are not yet explicitly modeled",
        ],
        "next_model": "interplanetary settlement, founder effects, off-world isolation and technology transfer between worlds",
    }
