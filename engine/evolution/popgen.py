#!/usr/bin/env python3
"""Population-genetics scaffold for TRISOLARIS LAB.

This layer introduces explicit allele-frequency distributions for a small set
of abstract physiological loci. It is still a teaching/research scaffold, not
a genome simulator.

Processes represented:
- directional selection from environmental stress,
- symmetric mutation,
- migration/gene flow,
- founder shifts,
- genetic drift scaled by effective population size.

No taxonomic category is assigned from these values alone.
"""

from __future__ import annotations

import hashlib
import math
from typing import Any

LOCI = {
    "THERM-A": {"stress_key": "thermal", "label": "Resiliencia térmica"},
    "WATER-A": {"stress_key": "water", "label": "Conservación de agua"},
    "OXY-A": {"stress_key": "oxygen", "label": "Eficiencia de oxígeno"},
    "DIET-A": {"stress_key": "food", "label": "Flexibilidad dietaria"},
}


def _clamp(v: float, lo: float = 1e-4, hi: float = 1 - 1e-4) -> float:
    return max(lo, min(hi, v))


def _signed(key: str) -> float:
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    unit = int.from_bytes(digest[:8], "big") / float(2**64 - 1)
    return 2.0 * unit - 1.0


def simulate_population_genetics(
    refugia_network: dict[str, Any],
    *,
    years: float = 50_000.0,
    generation_years: float = 28.0,
    technology_buffer: float = 0.40,
    selection_scale: float = 0.002,
    mutation_rate: float = 1e-5,
) -> dict[str, Any]:
    if years < 0:
        raise ValueError("years cannot be negative")
    generations = years / generation_years
    refugia = refugia_network.get("refugia", [])
    links = refugia_network.get("links", [])

    if not refugia:
        return {
            "model": "population_genetics_v0.1",
            "epistemic_level": "MODELED",
            "inputs": {"years": years, "generations": generations},
            "populations": [],
            "summary": {"mean_fst_proxy": 0.0, "mean_heterozygosity": 0.0},
            "limitations": ["no viable refugia"],
        }

    ids = [r["id"] for r in refugia]
    max_flow = {rid: 0.0 for rid in ids}
    for link in links:
        flow = float(link["migration_flow_potential"])
        max_flow[link["source"]] = max(max_flow[link["source"]], flow)
        max_flow[link["target"]] = max(max_flow[link["target"]], flow)

    state: dict[str, dict[str, float]] = {}
    for refuge in refugia:
        rid = refuge["id"]
        isolation = float(refuge.get("isolation_potential", 1.0))
        state[rid] = {}
        for locus in LOCI:
            founder = 0.5 + 0.08 * isolation * _signed(f"founder:{rid}:{locus}")
            state[rid][locus] = _clamp(founder)

    # Aggregate in chunks for speed and determinism.
    chunks = max(1, min(400, math.ceil(generations / 25.0)))
    chunk_generations = generations / chunks if chunks else 0.0

    refugia_by_id = {r["id"]: r for r in refugia}

    for step in range(chunks):
        means = {
            locus: sum(state[rid][locus] for rid in ids) / len(ids)
            for locus in LOCI
        }
        next_state = {rid: dict(values) for rid, values in state.items()}

        for rid in ids:
            refuge = refugia_by_id[rid]
            share = max(1e-6, float(refuge.get("relative_population_share_if_settled", 0.0)))
            ne = max(500.0, 50_000.0 * share)
            isolation = float(refuge.get("isolation_potential", 1.0))
            flow = max_flow.get(rid, 0.0)
            stress = refuge.get("stress_components", {})
            exposure = max(0.0, min(1.0, (1.0 - 0.72 * technology_buffer) * isolation))

            for locus, spec in LOCI.items():
                p = state[rid][locus]
                env = max(0.0, min(1.0, float(stress.get(spec["stress_key"], 0.3))))
                s = selection_scale * env * exposure

                # Directional selection for the modeled adaptive allele.
                if chunk_generations > 0:
                    selected = p
                    for _ in range(max(1, min(25, math.ceil(chunk_generations)))):
                        selected = selected * (1.0 + s) / (1.0 + s * selected)
                    p = selected

                # Symmetric mutation gently pulls extreme frequencies inward.
                mu = min(0.05, mutation_rate * chunk_generations)
                p = p * (1.0 - 2.0 * mu) + mu

                # Migration toward the population mean.
                migration = min(0.35, flow * 0.06 * chunk_generations)
                p = p + migration * (means[locus] - p)

                # Deterministic scenario drift with population-size scaling.
                variance = max(0.0, p * (1.0 - p) * chunk_generations / (2.0 * ne))
                drift = math.sqrt(variance) * _signed(f"drift:{step}:{rid}:{locus}")
                p = _clamp(p + drift)
                next_state[rid][locus] = p

        state = next_state

    populations = []
    heterozygosities = []
    for refuge in refugia:
        rid = refuge["id"]
        freqs = state[rid]
        hetero = {
            locus: 2.0 * p * (1.0 - p)
            for locus, p in freqs.items()
        }
        heterozygosities.extend(hetero.values())
        populations.append({
            "refuge_id": rid,
            "refuge_name": refuge["name"],
            "allele_frequencies": freqs,
            "heterozygosity": hetero,
            "mean_heterozygosity": sum(hetero.values()) / len(hetero),
            "gene_flow_proxy": max_flow.get(rid, 0.0),
            "isolation_potential": float(refuge.get("isolation_potential", 0.0)),
        })

    fst_by_locus = {}
    for locus in LOCI:
        values = [p["allele_frequencies"][locus] for p in populations]
        mean_p = sum(values) / len(values)
        variance = sum((v - mean_p) ** 2 for v in values) / len(values)
        denom = max(1e-8, mean_p * (1.0 - mean_p))
        fst_by_locus[locus] = max(0.0, min(1.0, variance / denom))

    return {
        "model": "population_genetics_v0.1",
        "epistemic_level": "MODELED",
        "loci": LOCI,
        "inputs": {
            "years": years,
            "generation_years": generation_years,
            "generations": generations,
            "technology_buffer": technology_buffer,
            "selection_scale": selection_scale,
            "mutation_rate": mutation_rate,
        },
        "populations": populations,
        "summary": {
            "mean_fst_proxy": sum(fst_by_locus.values()) / len(fst_by_locus),
            "fst_by_locus": fst_by_locus,
            "mean_heterozygosity": (
                sum(heterozygosities) / len(heterozygosities)
                if heterozygosities else 0.0
            ),
        },
        "limitations": [
            "four abstract biallelic loci only",
            "selection coefficients are environmental proxies",
            "deterministic drift is used for reproducible scenarios",
            "no recombination map, dominance, epistasis or developmental genetics",
            "FST is a simple frequency-variance proxy",
            "no species assignment follows automatically from allele frequencies",
        ],
        "next_model": "multi-locus recombination, bottlenecks, admixture events and persistent lineage genomes",
    }
