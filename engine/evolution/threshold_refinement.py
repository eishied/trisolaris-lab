#!/usr/bin/env python3
"""Adaptive threshold refinement for TRISOLARIS LAB Phase 12.1."""

from __future__ import annotations

from typing import Any

from engine.evolution.replay import run_evolutionary_replay
from engine.evolution.thresholds import _scale_capability


def _metric(replay: dict[str, Any], metric: str) -> float:
    frequencies = replay.get("outcomes", {}).get("frequencies", {})
    if metric == "non_no_launch_frequency":
        return 1.0 - float(frequencies.get("no-launch", 0.0))
    if metric == "persistent_colony_frequency":
        return (
            float(frequencies.get("connected-colony", 0.0))
            + float(frequencies.get("divergent-lineage", 0.0))
        )
    if metric == "divergent_lineage_frequency":
        return float(frequencies.get("divergent-lineage", 0.0))
    raise ValueError(f"unsupported metric: {metric}")


def _evaluate(
    system_data: dict[str, Any],
    astroanthropology: dict[str, Any],
    factor: float,
    *,
    years: float,
    runs: int,
    seed: int,
    uncertainty: float,
    metric: str,
) -> dict[str, Any]:
    replay = run_evolutionary_replay(
        system_data,
        _scale_capability(astroanthropology, factor),
        years=years,
        runs=runs,
        seed=seed,
        uncertainty=uncertainty,
        founder_size=500,
        exchange_strength=0.30,
        resupply_strength=0.35,
        infrastructure_shock=0.0,
    )
    return {
        "capability_multiplier": factor,
        "frequency": _metric(replay, metric),
        "dominant_outcome": replay.get("outcomes", {}).get("dominant_outcome"),
        "dominant_frequency": replay.get("outcomes", {}).get("dominant_frequency", 0.0),
    }


def _find_bracket(
    coarse_curve: list[dict[str, Any]],
    metric: str,
    target: float,
) -> tuple[float, float] | None:
    previous = None
    for point in coarse_curve:
        value = float(point["value"])
        frequency = float(point.get(metric, 0.0))
        if previous is not None:
            prev_value, prev_frequency = previous
            if prev_frequency < target <= frequency:
                return prev_value, value
        previous = (value, frequency)
    return None


def refine_capability_thresholds(
    system_data: dict[str, Any],
    astroanthropology: dict[str, Any],
    coarse_atlas: dict[str, Any],
    *,
    years: float,
    runs: int = 32,
    seed: int = 1445,
    uncertainty: float = 0.10,
    target_frequency: float = 0.50,
    iterations: int = 8,
) -> dict[str, Any]:
    """Refine stage-specific capability thresholds inside coarse brackets."""
    if runs < 2:
        raise ValueError("runs must be at least 2")
    if iterations < 1:
        raise ValueError("iterations must be positive")

    capability_scan = next(
        (
            scan for scan in coarse_atlas.get("scans", [])
            if scan.get("parameter") == "capability_multiplier"
        ),
        None,
    )
    if capability_scan is None:
        raise ValueError("coarse atlas has no capability multiplier scan")

    targets = (
        ("leave_no_launch", "non_no_launch_frequency"),
        ("persistent_colony", "persistent_colony_frequency"),
        ("divergent_lineage", "divergent_lineage_frequency"),
    )

    refinements = []
    for stage, metric in targets:
        bracket = _find_bracket(
            capability_scan.get("curve", []),
            metric,
            target_frequency,
        )
        if bracket is None:
            refinements.append({
                "stage": stage,
                "metric": metric,
                "target_frequency": target_frequency,
                "refinable": False,
                "coarse_bracket": None,
                "refined_threshold_upper": None,
                "refined_threshold_lower": None,
                "evaluations": [],
            })
            continue

        low, high = bracket
        evaluations = []
        low_eval = _evaluate(
            system_data,
            astroanthropology,
            low,
            years=years,
            runs=runs,
            seed=seed,
            uncertainty=uncertainty,
            metric=metric,
        )
        high_eval = _evaluate(
            system_data,
            astroanthropology,
            high,
            years=years,
            runs=runs,
            seed=seed,
            uncertainty=uncertainty,
            metric=metric,
        )
        evaluations.extend((low_eval, high_eval))

        if not (
            low_eval["frequency"] < target_frequency
            and high_eval["frequency"] >= target_frequency
        ):
            refinements.append({
                "stage": stage,
                "metric": metric,
                "target_frequency": target_frequency,
                "refinable": False,
                "coarse_bracket": [low, high],
                "refined_threshold_upper": None,
                "refined_threshold_lower": None,
                "evaluations": evaluations,
                "reason": "coarse crossing was not reproduced at refinement settings",
            })
            continue

        for _ in range(iterations):
            midpoint = (low + high) / 2.0
            point = _evaluate(
                system_data,
                astroanthropology,
                midpoint,
                years=years,
                runs=runs,
                seed=seed,
                uncertainty=uncertainty,
                metric=metric,
            )
            evaluations.append(point)
            if point["frequency"] >= target_frequency:
                high = midpoint
            else:
                low = midpoint

        refinements.append({
            "stage": stage,
            "metric": metric,
            "target_frequency": target_frequency,
            "refinable": True,
            "coarse_bracket": list(bracket),
            "refined_threshold_lower": low,
            "refined_threshold_upper": high,
            "interval_width": high - low,
            "evaluations": evaluations,
        })

    return {
        "model": "adaptive_threshold_refinement_v0.1",
        "epistemic_level": "MODELED",
        "inputs": {
            "years": years,
            "runs_per_evaluation": runs,
            "seed": seed,
            "uncertainty": uncertainty,
            "target_frequency": target_frequency,
            "iterations": iterations,
        },
        "refinements": refinements,
        "summary": {
            "stage_count": len(refinements),
            "refined_stage_count": sum(
                1 for row in refinements if row["refinable"]
            ),
            "unrefined_stage_count": sum(
                1 for row in refinements if not row["refinable"]
            ),
        },
        "limitations": [
            "binary refinement assumes a locally monotonic crossing inside the coarse bracket",
            "threshold intervals remain conditional on fixed replay seed and perturbation envelope",
            "refined multipliers are model parameters and are not engineering requirements",
            "persistent colony and divergent lineage remain reduced-order outcome classes",
            "higher-fidelity models may move or remove these thresholds",
        ],
    }
