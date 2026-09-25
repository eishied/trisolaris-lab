#!/usr/bin/env python3
"""Planetary population-history and anthropogenic-footprint scaffold.

The model links named refugia and biological lineages to settlement,
agriculture, infrastructure, mobility and knowledge-continuity proxies.

It does not rank cultures or assume a universal ladder of progress.
Technology is treated as a functional system that can buffer environmental
stress while creating maintenance and resource dependencies.
"""

from __future__ import annotations

import math
from typing import Any


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _maturation(years: float, timescale: float) -> float:
    if years <= 0:
        return 0.0
    return 1.0 - math.exp(-years / max(1.0, timescale))


def simulate_planetary_history(
    refugia_network: dict[str, Any],
    lineage_model: dict[str, Any],
    *,
    years: float = 50_000.0,
    technology_support: float = 0.40,
    mobility: float = 0.45,
) -> dict[str, Any]:
    technology_support = _clamp01(technology_support)
    mobility = _clamp01(mobility)
    refugia = {r["id"]: r for r in refugia_network.get("refugia", [])}
    lineages = lineage_model.get("lineages", [])

    populations = []
    for lineage in lineages:
        refuge = refugia.get(lineage["refuge_id"])
        if refuge is None:
            continue

        support = _clamp01(float(refuge.get("assisted_support", 0.0)))
        natural = _clamp01(float(refuge.get("natural_support", 0.0)))
        agriculture = _clamp01(float(refuge.get("agriculture_potential", 0.0)))
        isolation = _clamp01(float(lineage.get("isolation_potential", 0.0)))
        gene_flow = _clamp01(float(lineage.get("gene_flow_proxy", 0.0)))
        share = _clamp01(float(refuge.get("relative_population_share_if_settled", 0.0)))
        stresses = refuge.get("stress_components", {})

        settlement = _clamp01(
            support
            * (0.30 + 0.70 * _maturation(years, 2_000.0))
            * (0.62 + 0.38 * technology_support)
        )
        open_agriculture = _clamp01(
            agriculture * settlement * (0.55 + 0.45 * natural)
        )
        controlled_agriculture = _clamp01(
            settlement
            * technology_support
            * (0.35 + 0.65 * (1.0 - agriculture))
        )
        infrastructure = _clamp01(
            settlement
            * technology_support
            * (0.55 + 0.45 * mobility)
            * (0.70 + 0.30 * _maturation(years, 5_000.0))
        )
        water_recycling = _clamp01(
            technology_support
            * float(stresses.get("water", 0.0))
            * (0.45 + 0.55 * settlement)
        )
        thermal_shelter = _clamp01(
            technology_support
            * float(stresses.get("thermal", 0.0))
            * (0.45 + 0.55 * settlement)
        )
        mobility_network = _clamp01(
            mobility
            * (0.45 + 0.55 * gene_flow)
            * (0.55 + 0.45 * infrastructure)
        )

        # "Knowledge continuity" is a resilience proxy for storage,
        # transmission and institutional persistence. It is not a measure of
        # intelligence, worth or cultural superiority.
        knowledge_continuity = _clamp01(
            0.30
            + 0.34 * technology_support
            + 0.18 * mobility_network
            + 0.18 * settlement
            - 0.16 * isolation
        )

        # Cultural differentiation is a separation proxy, not a quality score.
        cultural_differentiation = _clamp01(
            _maturation(years, 8_000.0)
            * isolation
            * (1.0 - 0.72 * gene_flow)
        )

        footprint = _clamp01(
            0.34 * settlement
            + 0.24 * max(open_agriculture, controlled_agriculture)
            + 0.24 * infrastructure
            + 0.18 * mobility_network
        )

        if infrastructure >= 0.65:
            settlement_pattern = "connected infrastructure network"
        elif controlled_agriculture >= 0.55:
            settlement_pattern = "protected settlement network"
        elif settlement >= 0.55:
            settlement_pattern = "regional permanent settlements"
        elif settlement >= 0.25:
            settlement_pattern = "dispersed settlement"
        else:
            settlement_pattern = "low-density presence"

        populations.append({
            "lineage_id": lineage["id"],
            "lineage_name": lineage["name"],
            "refuge_id": refuge["id"],
            "refuge_name": refuge["name"],
            "center_latitude_deg": float(refuge["center_latitude_deg"]),
            "latitude_min_deg": float(refuge["latitude_min_deg"]),
            "latitude_max_deg": float(refuge["latitude_max_deg"]),
            "relative_capacity_share": share,
            "settlement_intensity": settlement,
            "settlement_pattern": settlement_pattern,
            "open_agriculture": open_agriculture,
            "controlled_agriculture": controlled_agriculture,
            "infrastructure": infrastructure,
            "water_recycling": water_recycling,
            "thermal_shelter": thermal_shelter,
            "mobility_network": mobility_network,
            "knowledge_continuity": knowledge_continuity,
            "cultural_differentiation_proxy": cultural_differentiation,
            "anthropogenic_footprint_proxy": footprint,
        })

    total_weight = sum(max(1e-9, p["relative_capacity_share"]) for p in populations) or 1.0
    weighted = lambda key: sum(
        p[key] * max(1e-9, p["relative_capacity_share"]) for p in populations
    ) / total_weight

    links = []
    lineage_by_refuge = {p["refuge_id"]: p for p in populations}
    for link in refugia_network.get("links", []):
        source = lineage_by_refuge.get(link["source"])
        target = lineage_by_refuge.get(link["target"])
        if not source or not target:
            continue
        base_flow = _clamp01(float(link.get("migration_flow_potential", 0.0)))
        realized = _clamp01(
            base_flow
            * mobility
            * (0.55 + 0.45 * min(source["settlement_intensity"], target["settlement_intensity"]))
        )
        links.append({
            "source_lineage_id": source["lineage_id"],
            "target_lineage_id": target["lineage_id"],
            "source_refuge_id": source["refuge_id"],
            "target_refuge_id": target["refuge_id"],
            "migration_flow_proxy": realized,
        })

    events = []
    for p in populations:
        if p["settlement_intensity"] >= 0.25:
            events.append({
                "type": "settlement",
                "lineage_id": p["lineage_id"],
                "label": f"{p['refuge_name']}: persistent settlement",
            })
        if p["open_agriculture"] >= 0.35:
            events.append({
                "type": "agriculture",
                "lineage_id": p["lineage_id"],
                "label": f"{p['refuge_name']}: open agriculture becomes viable",
            })
        if p["controlled_agriculture"] >= 0.45:
            events.append({
                "type": "controlled_agriculture",
                "lineage_id": p["lineage_id"],
                "label": f"{p['refuge_name']}: controlled agriculture becomes important",
            })
        if p["infrastructure"] >= 0.50:
            events.append({
                "type": "infrastructure",
                "lineage_id": p["lineage_id"],
                "label": f"{p['refuge_name']}: infrastructure network intensifies",
            })

    return {
        "model": "planetary_population_history_v0.1",
        "epistemic_level": "MODELED",
        "inputs": {
            "years": years,
            "technology_support": technology_support,
            "mobility": mobility,
        },
        "populations": populations,
        "migration_links": links,
        "events": events,
        "summary": {
            "population_regions": len(populations),
            "mean_settlement_intensity": weighted("settlement_intensity") if populations else 0.0,
            "mean_agriculture_intensity": weighted("open_agriculture") if populations else 0.0,
            "mean_controlled_agriculture": weighted("controlled_agriculture") if populations else 0.0,
            "mean_infrastructure": weighted("infrastructure") if populations else 0.0,
            "mean_knowledge_continuity": weighted("knowledge_continuity") if populations else 0.0,
            "mean_cultural_differentiation_proxy": weighted("cultural_differentiation_proxy") if populations else 0.0,
            "mean_anthropogenic_footprint_proxy": weighted("anthropogenic_footprint_proxy") if populations else 0.0,
        },
        "limitations": [
            "normalized population capacity rather than census counts",
            "latitude-resolved refugia only; longitude is not physically modeled",
            "technology is a functional buffering proxy, not a progress ranking",
            "cultural differentiation is a separation proxy, not a value judgment",
            "no warfare, political system or social hierarchy is inferred",
            "no deterministic historical trajectory is claimed",
        ],
        "next_model": "persistent events, demographic shocks, migration histories, land-use feedback and off-world settlement",
    }
