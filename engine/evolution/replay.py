#!/usr/bin/env python3
"""Reproducible evolutionary replay ensembles for TRISOLARIS LAB Phase 10."""

from __future__ import annotations

import copy
import math
import random
from typing import Any

from engine.human.interplanetary import simulate_interplanetary_settlement
from engine.human.interplanetary_network import simulate_interplanetary_network
from engine.evolution.offworld import simulate_offworld_divergence


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    denom = math.sqrt(sum(x * x for x in dx) * sum(y * y for y in dy))
    if denom <= 0:
        return 0.0
    return max(-1.0, min(1.0, sum(x * y for x, y in zip(dx, dy)) / denom))


def _scaled_astro(
    astroanthropology: dict[str, Any],
    capability_factor: float,
) -> dict[str, Any]:
    result = copy.deepcopy(astroanthropology)
    for society in result.get("societies", []):
        for key in (
            "technical_balance",
            "knowledge_retention",
            "system_redundancy",
        ):
            society[key] = _clamp01(society.get(key, 0.0) * capability_factor)
        portfolio = society.get("technology_portfolio", {})
        for key in ("infrastructure", "mobility"):
            if key in portfolio:
                portfolio[key] = _clamp01(portfolio.get(key, 0.0) * capability_factor)
    return result


def _outcome_code(
    interplanetary: dict[str, Any],
    network: dict[str, Any],
    divergence: dict[str, Any],
) -> tuple[str, float]:
    if not any(a.get("launch_feasible") for a in interplanetary.get("attempts", [])):
        return "no-launch", 0.0
    if not any(a.get("settlement_persists") for a in interplanetary.get("attempts", [])):
        return "settlement-failure", 1.0
    if network.get("summary", {}).get("active_colony_count", 0) <= 0:
        return "colony-collapse", 2.0
    if divergence.get("summary", {}).get("persistent_lineage_branch_count", 0) > 0:
        return "divergent-lineage", 4.0
    return "connected-colony", 3.0


def run_evolutionary_replay(
    system_data: dict[str, Any],
    astroanthropology: dict[str, Any],
    *,
    years: float,
    runs: int = 64,
    seed: int = 1445,
    uncertainty: float = 0.25,
    founder_size: int = 500,
    exchange_strength: float = 0.30,
    resupply_strength: float = 0.35,
    infrastructure_shock: float = 0.0,
) -> dict[str, Any]:
    """Replay a scenario under explicit, reproducible parameter perturbations."""
    if years < 0:
        raise ValueError("years cannot be negative")
    if runs < 2:
        raise ValueError("runs must be at least 2")
    if founder_size < 2:
        raise ValueError("founder_size must be at least 2")

    uncertainty = _clamp01(uncertainty)
    rng = random.Random(int(seed))
    records: list[dict[str, Any]] = []

    for index in range(runs):
        founder_factor = 1.0 + rng.uniform(-uncertainty, uncertainty)
        capability_factor = 1.0 + rng.uniform(-0.75 * uncertainty, 0.75 * uncertainty)
        founder = max(2, int(round(founder_size * founder_factor)))
        exchange = _clamp01(
            exchange_strength + rng.uniform(-0.50 * uncertainty, 0.50 * uncertainty)
        )
        resupply = _clamp01(
            resupply_strength + rng.uniform(-0.50 * uncertainty, 0.50 * uncertainty)
        )
        shock = _clamp01(
            infrastructure_shock + rng.uniform(0.0, 0.65 * uncertainty)
        )

        perturbed_astro = _scaled_astro(astroanthropology, capability_factor)
        interplanetary = simulate_interplanetary_settlement(
            system_data,
            perturbed_astro,
            years=years,
            founder_size=founder,
            exchange_strength=exchange,
            launch_active=True,
        )
        network = simulate_interplanetary_network(
            interplanetary,
            years=years,
            resupply_strength=resupply,
            infrastructure_shock=shock,
            enable_return_migration=True,
        )
        divergence = simulate_offworld_divergence(
            interplanetary,
            network,
            years=years,
            generation_years=28.0,
        )
        outcome, outcome_score = _outcome_code(
            interplanetary, network, divergence
        )

        records.append({
            "run": index + 1,
            "founder_size": founder,
            "capability_factor": capability_factor,
            "exchange_strength": exchange,
            "resupply_strength": resupply,
            "infrastructure_shock": shock,
            "outcome": outcome,
            "outcome_score": outcome_score,
            "launch_feasible_count": interplanetary.get("summary", {}).get(
                "launch_feasible_count", 0
            ),
            "persistent_settlement_count": interplanetary.get("summary", {}).get(
                "persistent_settlement_count", 0
            ),
            "active_colony_count": network.get("summary", {}).get(
                "active_colony_count", 0
            ),
            "offworld_population": network.get("summary", {}).get(
                "offworld_population", 0.0
            ),
            "persistent_lineage_branch_count": divergence.get("summary", {}).get(
                "persistent_lineage_branch_count", 0
            ),
            "mean_divergence_proxy": divergence.get("summary", {}).get(
                "mean_divergence_proxy", 0.0
            ),
        })

    labels = (
        "no-launch",
        "settlement-failure",
        "colony-collapse",
        "connected-colony",
        "divergent-lineage",
    )
    counts = {label: sum(1 for record in records if record["outcome"] == label) for label in labels}
    frequencies = {label: counts[label] / runs for label in labels}

    outcome_scores = [record["outcome_score"] for record in records]
    divergence_scores = [record["mean_divergence_proxy"] for record in records]
    parameters = {
        "founder_size": [float(record["founder_size"]) for record in records],
        "capability_factor": [record["capability_factor"] for record in records],
        "exchange_strength": [record["exchange_strength"] for record in records],
        "resupply_strength": [record["resupply_strength"] for record in records],
        "infrastructure_shock": [record["infrastructure_shock"] for record in records],
    }

    sensitivity = []
    for name, values in parameters.items():
        sensitivity.append({
            "parameter": name,
            "outcome_correlation": _pearson(values, outcome_scores),
            "divergence_correlation": _pearson(values, divergence_scores),
        })
    sensitivity.sort(
        key=lambda row: abs(row["outcome_correlation"]),
        reverse=True,
    )

    dominant_outcome = max(labels, key=lambda label: counts[label])
    dominant_frequency = frequencies[dominant_outcome]

    return {
        "model": "evolutionary_replay_v0.1",
        "epistemic_level": "MODELED",
        "inputs": {
            "years": years,
            "runs": runs,
            "seed": int(seed),
            "uncertainty": uncertainty,
            "founder_size": founder_size,
            "exchange_strength": exchange_strength,
            "resupply_strength": resupply_strength,
            "infrastructure_shock": infrastructure_shock,
        },
        "outcomes": {
            "counts": counts,
            "frequencies": frequencies,
            "dominant_outcome": dominant_outcome,
            "dominant_frequency": dominant_frequency,
        },
        "sensitivity": sensitivity,
        "runs": records,
        "summary": {
            "runs": runs,
            "dominant_outcome": dominant_outcome,
            "dominant_frequency": dominant_frequency,
            "mean_outcome_score": sum(outcome_scores) / runs,
            "mean_divergence_proxy": sum(divergence_scores) / runs,
            "max_divergence_proxy": max(divergence_scores) if divergence_scores else 0.0,
        },
        "limitations": [
            "ensemble frequencies are conditional on declared perturbation ranges and are not real-world probabilities",
            "parameter perturbations are uniform scenario ranges, not empirically calibrated uncertainty distributions",
            "the replay inherits all limitations of the underlying orbital, settlement, network and divergence models",
            "a dominant ensemble outcome indicates robustness only within this model and perturbation envelope",
            "the fixed random seed makes the baseline reproducible",
        ],
    }
