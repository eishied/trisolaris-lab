#!/usr/bin/env python3
"""Population-level lineage divergence scaffold.

This model is intentionally conservative:
- evolution occurs in populations, not individuals,
- elapsed time alone does not create a new species,
- technology can reduce environmental selection,
- migration/gene flow reduces divergence,
- drift depends on effective population size,
- outputs are lineage differentiation proxies, not taxonomic declarations.

The model operates on abstract physiological trait indices. It does not infer
beauty, ethnicity, race, or deterministic body forms.
"""

from __future__ import annotations

import hashlib
import math
from typing import Any


TRAITS = (
    "thermal_resilience",
    "water_conservation",
    "oxygen_efficiency",
    "dietary_flexibility",
)

ANCESTRAL = {
    "thermal_resilience": 0.35,
    "water_conservation": 0.30,
    "oxygen_efficiency": 0.35,
    "dietary_flexibility": 0.40,
}


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, v))


def _deterministic_signed(refuge_id: str, trait: str) -> float:
    digest = hashlib.sha256(f"{refuge_id}:{trait}".encode("utf-8")).digest()
    unit = int.from_bytes(digest[:8], "big") / float(2**64 - 1)
    return 2.0 * unit - 1.0


def _classification(divergence: float, generations: float, isolation: float) -> str:
    if divergence < 0.05:
        return "regional population"
    if divergence < 0.14:
        return "differentiated lineage"
    if divergence < 0.26:
        return "strongly differentiated lineage"
    if generations >= 2000 and isolation >= 0.75:
        return "incipient reproductive-isolation candidate"
    return "strongly differentiated lineage"


def simulate_lineage_divergence(
    refugia_network: dict[str, Any],
    *,
    years: float = 50_000.0,
    generation_years: float = 28.0,
    selection_rate_per_generation: float = 0.00035,
    technology_buffer: float = 0.40,
) -> dict[str, Any]:
    if years < 0:
        raise ValueError("years cannot be negative")
    if generation_years <= 0:
        raise ValueError("generation_years must be positive")

    generations = years / generation_years
    tech = _clamp01(technology_buffer)
    refugia = refugia_network.get("refugia", [])
    links = refugia_network.get("links", [])

    max_flow_by_id: dict[str, float] = {r["id"]: 0.0 for r in refugia}
    for link in links:
        flow = float(link["migration_flow_potential"])
        max_flow_by_id[link["source"]] = max(max_flow_by_id.get(link["source"], 0.0), flow)
        max_flow_by_id[link["target"]] = max(max_flow_by_id.get(link["target"], 0.0), flow)

    lineages = []
    for idx, refuge in enumerate(refugia, start=1):
        refuge_id = refuge["id"]
        gene_flow = _clamp01(max_flow_by_id.get(refuge_id, 0.0))
        isolation = _clamp01(float(refuge.get("isolation_potential", 1.0 - gene_flow)))
        population_share = max(1e-6, float(refuge.get("relative_population_share_if_settled", 0.0)))

        # Effective population size is a scenario proxy, not a census count.
        effective_population_size = max(500.0, 50_000.0 * population_share)

        stresses = refuge.get("stress_components", {})
        thermal_stress = _clamp01(float(stresses.get("thermal", 0.35)))
        water_stress = _clamp01(float(stresses.get("water", 0.35)))
        oxygen_stress = _clamp01(float(stresses.get("oxygen", 0.20)))
        food_stress = _clamp01(float(stresses.get("food", 0.35)))

        # Technology buffers selection rather than producing adaptation.
        selection_exposure = _clamp01((1.0 - 0.72 * tech) * isolation)
        response = 1.0 - math.exp(
            -selection_rate_per_generation * generations * selection_exposure
        )

        targets = {
            "thermal_resilience": _clamp01(0.30 + 0.62 * thermal_stress),
            "water_conservation": _clamp01(0.28 + 0.66 * water_stress),
            "oxygen_efficiency": _clamp01(0.30 + 0.62 * oxygen_stress),
            "dietary_flexibility": _clamp01(0.32 + 0.58 * food_stress),
        }

        # Drift grows with generations / Ne and is damped by gene flow.
        drift_scale = min(
            0.18,
            0.55 * math.sqrt(max(0.0, generations) / (2.0 * effective_population_size)),
        ) * (1.0 - 0.75 * gene_flow)

        traits = {}
        shifts = {}
        for trait in TRAITS:
            directional = response * (targets[trait] - ANCESTRAL[trait])
            drift = drift_scale * _deterministic_signed(refuge_id, trait)
            value = _clamp01(ANCESTRAL[trait] + directional + drift)
            traits[trait] = value
            shifts[trait] = value - ANCESTRAL[trait]

        divergence = sum(abs(shifts[t]) for t in TRAITS) / len(TRAITS)
        category = _classification(divergence, generations, isolation)

        # A broad compatibility proxy; never interpreted as a clinical or
        # taxonomic test. Gene flow keeps compatibility high.
        compatibility_to_ancestor = _clamp01(
            max(0.45, math.exp(-2.2 * divergence) * (0.88 + 0.12 * gene_flow))
        )

        lineages.append({
            "id": f"L{idx}",
            "name": f"Linaje {refuge['name']}",
            "parent": "P0",
            "refuge_id": refuge_id,
            "refuge_name": refuge["name"],
            "origin_year": 0.0,
            "elapsed_years": years,
            "generations": generations,
            "effective_population_size_proxy": effective_population_size,
            "gene_flow_proxy": gene_flow,
            "isolation_potential": isolation,
            "selection_exposure": selection_exposure,
            "drift_scale": drift_scale,
            "traits": traits,
            "trait_shifts_from_ancestor": shifts,
            "divergence_index": divergence,
            "classification": category,
            "compatibility_to_ancestor_proxy": compatibility_to_ancestor,
            "taxonomic_status": "not assigned",
        })

    pairwise = []
    for i, a in enumerate(lineages):
        for b in lineages[i + 1:]:
            trait_distance = math.sqrt(
                sum((a["traits"][t] - b["traits"][t]) ** 2 for t in TRAITS) / len(TRAITS)
            )

            corresponding_flow = 0.0
            for link in links:
                if {link["source"], link["target"]} == {a["refuge_id"], b["refuge_id"]}:
                    corresponding_flow = float(link["migration_flow_potential"])
                    break

            compatibility = _clamp01(
                max(0.40, math.exp(-2.6 * trait_distance) * (0.86 + 0.14 * corresponding_flow))
            )
            pairwise.append({
                "lineage_a": a["id"],
                "lineage_b": b["id"],
                "trait_distance": trait_distance,
                "gene_flow_proxy": corresponding_flow,
                "reproductive_compatibility_proxy": compatibility,
            })

    max_divergence = max((l["divergence_index"] for l in lineages), default=0.0)
    candidate_count = sum(
        1 for l in lineages
        if l["classification"] == "incipient reproductive-isolation candidate"
    )

    return {
        "model": "population_lineage_divergence_v0.1",
        "epistemic_level": "MODELED",
        "ancestor": {
            "id": "P0",
            "name": "Población fundadora",
            "traits": ANCESTRAL,
        },
        "inputs": {
            "years": years,
            "generation_years": generation_years,
            "generations": generations,
            "selection_rate_per_generation": selection_rate_per_generation,
            "technology_buffer": tech,
        },
        "summary": {
            "lineage_count": len(lineages),
            "maximum_divergence_index": max_divergence,
            "incipient_isolation_candidate_count": candidate_count,
            "species_count": 0,
            "taxonomic_rule": "time alone never creates a species",
        },
        "lineages": lineages,
        "pairwise_compatibility": pairwise,
        "limitations": [
            "abstract physiological trait indices, not a genomic simulation",
            "effective population size is a scenario proxy",
            "selection targets come from broad environmental stress proxies",
            "no explicit loci, recombination, dominance, epistasis or developmental genetics yet",
            "reproductive compatibility is a heuristic proxy, not a biological test",
            "no species is assigned automatically",
            "no culture, language, ethnicity or appearance category is inferred",
        ],
        "next_model": "explicit allele-frequency distributions, mutation, recombination, drift, migration and persistent lineage histories",
    }
