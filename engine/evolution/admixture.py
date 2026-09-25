#!/usr/bin/env python3
"""Population admixture model for TRISOLARIS LAB.

The model combines allele-frequency distributions from two source populations.
It describes a descendant *population*, not an individual and not a guaranteed
hybrid species.

Outputs:
- weighted allele frequencies,
- expected heterozygosity,
- distance to each parent population,
- a simple admixture-diversity gain metric.

No phenotype, anatomy, ancestry category or taxonomic label is inferred from
admixture alone.
"""

from __future__ import annotations

import math
from typing import Any


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, v))


def _euclidean_frequency_distance(a: dict[str, float], b: dict[str, float]) -> float:
    shared = sorted(set(a) & set(b))
    if not shared:
        return 0.0
    return math.sqrt(
        sum((float(a[k]) - float(b[k])) ** 2 for k in shared) / len(shared)
    )


def mix_populations(
    population_a: dict[str, Any],
    population_b: dict[str, Any],
    *,
    fraction_a: float = 0.50,
) -> dict[str, Any]:
    fraction_a = _clamp01(fraction_a)
    fraction_b = 1.0 - fraction_a

    freq_a = population_a["allele_frequencies"]
    freq_b = population_b["allele_frequencies"]
    shared = sorted(set(freq_a) & set(freq_b))
    if not shared:
        raise ValueError("populations do not share modeled loci")

    mixed = {
        locus: fraction_a * float(freq_a[locus]) + fraction_b * float(freq_b[locus])
        for locus in shared
    }
    heterozygosity = {
        locus: 2.0 * p * (1.0 - p)
        for locus, p in mixed.items()
    }

    parent_h_a = sum(2.0 * float(freq_a[l]) * (1.0 - float(freq_a[l])) for l in shared) / len(shared)
    parent_h_b = sum(2.0 * float(freq_b[l]) * (1.0 - float(freq_b[l])) for l in shared) / len(shared)
    mixed_h = sum(heterozygosity.values()) / len(heterozygosity)

    return {
        "model": "population_admixture_v0.1",
        "epistemic_level": "MODELED",
        "parents": {
            "a": population_a.get("refuge_name", population_a.get("refuge_id", "A")),
            "b": population_b.get("refuge_name", population_b.get("refuge_id", "B")),
        },
        "fractions": {
            "a": fraction_a,
            "b": fraction_b,
        },
        "allele_frequencies": mixed,
        "heterozygosity": heterozygosity,
        "mean_heterozygosity": mixed_h,
        "distance_to_parent_a": _euclidean_frequency_distance(mixed, freq_a),
        "distance_to_parent_b": _euclidean_frequency_distance(mixed, freq_b),
        "diversity_gain_vs_parent_mean": mixed_h - 0.5 * (parent_h_a + parent_h_b),
        "taxonomic_status": "not assigned",
        "limitations": [
            "instantaneous one-generation mixture approximation",
            "no linkage disequilibrium or recombination map",
            "no mate choice, fertility, viability or demographic structure",
            "does not predict an individual's appearance",
            "does not create a hybrid species",
        ],
    }
