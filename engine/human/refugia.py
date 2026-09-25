#!/usr/bin/env python3
"""Refugia clustering and migration-network model.

This module groups contiguous latitude bands with sufficient assisted settlement
support into notional regional populations. The result is a spatial-demographic
scaffold for later migration, isolation and evolutionary models.

It does not infer ethnicity, race, culture, species or anatomy.
"""

from __future__ import annotations

import math
from typing import Any


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, v))


def _name_region(center_lat: float, index: int) -> str:
    if center_lat >= 50:
        stem = "Borealis"
    elif center_lat >= 18:
        stem = "Septentria"
    elif center_lat > -18:
        stem = "Equatoria"
    elif center_lat > -50:
        stem = "Australis"
    else:
        stem = "Polaris Sur"
    return f"{stem}-{index}"


def build_refugia_network(
    settlement: dict[str, Any],
    *,
    mobility: float = 0.45,
    viability_threshold: float = 0.50,
) -> dict[str, Any]:
    mobility = _clamp01(mobility)
    rows = settlement["bands"]

    clusters: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []

    for row in rows:
        if float(row["assisted_support"]) >= viability_threshold:
            current.append(row)
        elif current:
            clusters.append(current)
            current = []

    if current:
        clusters.append(current)

    refugia = []
    for idx, cluster in enumerate(clusters, start=1):
        weights = [max(0.0, math.cos(math.radians(float(r["latitude_deg"])))) for r in cluster]
        total_w = sum(weights) or 1.0
        center = sum(float(r["latitude_deg"]) * w for r, w in zip(cluster, weights)) / total_w
        natural = sum(float(r["natural_support"]) * w for r, w in zip(cluster, weights)) / total_w
        assisted = sum(float(r["assisted_support"]) * w for r, w in zip(cluster, weights)) / total_w
        agriculture = sum(float(r["agriculture_potential"]) * w for r, w in zip(cluster, weights)) / total_w
        dependency = sum(float(r["technology_dependency"]) * w for r, w in zip(cluster, weights)) / total_w

        stress_components = {}
        for key in ("thermal", "oxygen", "pressure", "water", "food"):
            stress_components[key] = sum(
                float(r.get("stress_components", {}).get(key, 0.0)) * w
                for r, w in zip(cluster, weights)
            ) / total_w

        refugia.append({
            "id": f"R{idx}",
            "name": _name_region(center, idx),
            "center_latitude_deg": center,
            "latitude_min_deg": float(cluster[0]["latitude_deg"]),
            "latitude_max_deg": float(cluster[-1]["latitude_deg"]),
            "natural_support": natural,
            "assisted_support": assisted,
            "agriculture_potential": agriculture,
            "technology_dependency": dependency,
            "stress_components": stress_components,
            "relative_capacity_weight": total_w * assisted * (0.45 + 0.55 * agriculture),
        })

    links = []
    for i, a in enumerate(refugia):
        for j in range(i + 1, len(refugia)):
            b = refugia[j]
            distance_deg = abs(a["center_latitude_deg"] - b["center_latitude_deg"])
            geographic_connectivity = math.exp(-distance_deg / 42.0)
            support_bridge = math.sqrt(
                max(0.0, a["assisted_support"] * b["assisted_support"])
            )
            flow = _clamp01(mobility * geographic_connectivity * support_bridge)
            links.append({
                "source": a["id"],
                "target": b["id"],
                "latitudinal_distance_deg": distance_deg,
                "migration_flow_potential": flow,
            })

    for refuge in refugia:
        incident = [
            link["migration_flow_potential"]
            for link in links
            if refuge["id"] in {link["source"], link["target"]}
        ]
        max_flow = max(incident, default=0.0)
        refuge["isolation_potential"] = 1.0 - max_flow

    total_capacity = sum(r["relative_capacity_weight"] for r in refugia) or 1.0
    for refuge in refugia:
        refuge["relative_population_share_if_settled"] = (
            refuge["relative_capacity_weight"] / total_capacity
        )

    if not refugia:
        state = "no viable refugia"
    elif len(refugia) == 1:
        state = "single connected refugium"
    elif max((r["isolation_potential"] for r in refugia), default=0.0) >= 0.75:
        state = "multiple refugia with strong isolation potential"
    else:
        state = "multiple refugia with migration connectivity"

    return {
        "model": "refugia_migration_network_v0.1",
        "epistemic_level": "MODELED",
        "inputs": {
            "mobility": mobility,
            "viability_threshold": viability_threshold,
        },
        "summary": {
            "refugia_count": len(refugia),
            "migration_links": len(links),
            "state": state,
            "maximum_isolation_potential": max(
                (r["isolation_potential"] for r in refugia),
                default=0.0,
            ),
        },
        "refugia": refugia,
        "links": links,
        "limitations": [
            "latitude-only geography",
            "no continents, terrain, borders, transport corridors, or oceans",
            "no actual population counts yet",
            "migration potential is not observed migration",
            "isolation potential does not imply genetic divergence",
            "no culture, language, ethnicity, species, or anatomy is inferred",
            "evolution requires explicit generations, heritable variation, selection, drift and gene flow in later phases",
        ],
        "next_model": "time-dependent demography, migration, gene flow, founder effects and named lineage histories",
    }
