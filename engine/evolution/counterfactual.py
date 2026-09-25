#!/usr/bin/env python3
"""Paired counterfactual replay for TRISOLARIS LAB Phase 10.1."""

from __future__ import annotations

import copy
from typing import Any

from engine.evolution.replay import run_evolutionary_replay


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _scale_astro(astro: dict[str, Any], factor: float) -> dict[str, Any]:
    result = copy.deepcopy(astro)
    for society in result.get("societies", []):
        for key in ("technical_balance", "knowledge_retention", "system_redundancy"):
            society[key] = _clamp01(float(society.get(key, 0.0)) * factor)
        portfolio = society.get("technology_portfolio", {})
        for key in ("infrastructure", "mobility"):
            if key in portfolio:
                portfolio[key] = _clamp01(float(portfolio.get(key, 0.0)) * factor)
    return result


def compare_counterfactual(
    system_data: dict[str, Any],
    astroanthropology: dict[str, Any],
    *,
    years: float,
    parameter: str,
    intervention_fraction: float,
    runs: int = 64,
    seed: int = 1445,
    uncertainty: float = 0.25,
    founder_size: int = 500,
    exchange_strength: float = 0.30,
    resupply_strength: float = 0.35,
    infrastructure_shock: float = 0.0,
) -> dict[str, Any]:
    """Compare paired ensembles with one changed variable and identical random seed."""
    intervention_fraction = max(-0.8, min(0.8, float(intervention_fraction)))

    base_astro = astroanthropology
    alt_astro = astroanthropology
    base = {
        "founder_size": founder_size,
        "exchange_strength": exchange_strength,
        "resupply_strength": resupply_strength,
        "infrastructure_shock": infrastructure_shock,
    }
    alt = dict(base)

    if parameter == "capability":
        alt_astro = _scale_astro(astroanthropology, 1.0 + intervention_fraction)
    elif parameter == "founder_size":
        alt["founder_size"] = max(2, int(round(founder_size * (1.0 + intervention_fraction))))
    elif parameter == "exchange_strength":
        alt["exchange_strength"] = _clamp01(exchange_strength + 0.5 * intervention_fraction)
    elif parameter == "resupply_strength":
        alt["resupply_strength"] = _clamp01(resupply_strength + 0.5 * intervention_fraction)
    elif parameter == "infrastructure_shock":
        alt["infrastructure_shock"] = _clamp01(infrastructure_shock + 0.5 * intervention_fraction)
    else:
        raise ValueError(f"unsupported counterfactual parameter: {parameter}")

    reference = run_evolutionary_replay(
        system_data, base_astro, years=years, runs=runs, seed=seed,
        uncertainty=uncertainty, **base
    )
    intervention = run_evolutionary_replay(
        system_data, alt_astro, years=years, runs=runs, seed=seed,
        uncertainty=uncertainty, **alt
    )

    paired = []
    changed = 0
    for left, right in zip(reference["runs"], intervention["runs"]):
        flip = left["outcome"] != right["outcome"]
        changed += int(flip)
        paired.append({
            "run": left["run"],
            "reference_outcome": left["outcome"],
            "intervention_outcome": right["outcome"],
            "outcome_changed": flip,
            "outcome_score_delta": right["outcome_score"] - left["outcome_score"],
            "divergence_delta": right["mean_divergence_proxy"] - left["mean_divergence_proxy"],
        })

    labels = reference["outcomes"]["frequencies"].keys()
    deltas = {
        label: intervention["outcomes"]["frequencies"][label]
        - reference["outcomes"]["frequencies"][label]
        for label in labels
    }

    return {
        "model": "counterfactual_replay_v0.1",
        "epistemic_level": "MODELED",
        "inputs": {
            "years": years,
            "parameter": parameter,
            "intervention_fraction": intervention_fraction,
            "runs": runs,
            "seed": seed,
            "uncertainty": uncertainty,
        },
        "reference": reference["outcomes"],
        "intervention": intervention["outcomes"],
        "frequency_deltas": deltas,
        "paired_runs": paired,
        "summary": {
            "paired_run_count": runs,
            "outcome_flip_count": changed,
            "outcome_flip_fraction": changed / runs,
            "mean_outcome_score_delta": sum(p["outcome_score_delta"] for p in paired) / runs,
            "mean_divergence_delta": sum(p["divergence_delta"] for p in paired) / runs,
            "dominant_outcome_changed": (
                reference["outcomes"]["dominant_outcome"]
                != intervention["outcomes"]["dominant_outcome"]
            ),
        },
        "limitations": [
            "the comparison isolates one declared model parameter while holding the replay seed fixed",
            "paired differences are model-conditional effects, not causal estimates for the real world",
            "the intervention range is a scenario choice rather than an empirically calibrated policy effect",
            "all limitations of the underlying Evolutionary Replay and Phase 9 models still apply",
        ],
    }
