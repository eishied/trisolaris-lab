#!/usr/bin/env python3
"""Transition-threshold atlas for TRISOLARIS LAB Phase 12."""

from __future__ import annotations

import copy
from typing import Any

from engine.evolution.replay import run_evolutionary_replay


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _scale_capability(
    astroanthropology: dict[str, Any],
    factor: float,
) -> dict[str, Any]:
    result = copy.deepcopy(astroanthropology)
    for society in result.get("societies", []):
        for key in (
            "technical_balance",
            "knowledge_retention",
            "system_redundancy",
        ):
            society[key] = _clamp01(float(society.get(key, 0.0)) * factor)
        portfolio = society.get("technology_portfolio", {})
        for key in ("infrastructure", "mobility"):
            if key in portfolio:
                portfolio[key] = _clamp01(float(portfolio.get(key, 0.0)) * factor)
    return result


def _curve_point(
    replay: dict[str, Any],
    value: float,
) -> dict[str, Any]:
    frequencies = replay.get("outcomes", {}).get("frequencies", {})
    no_launch = float(frequencies.get("no-launch", 0.0))
    connected = float(frequencies.get("connected-colony", 0.0))
    divergent = float(frequencies.get("divergent-lineage", 0.0))
    return {
        "value": value,
        "non_no_launch_frequency": 1.0 - no_launch,
        "persistent_colony_frequency": connected + divergent,
        "divergent_lineage_frequency": divergent,
        "dominant_outcome": replay.get("outcomes", {}).get("dominant_outcome"),
        "dominant_frequency": replay.get("outcomes", {}).get("dominant_frequency", 0.0),
    }


def scan_transition_thresholds(
    system_data: dict[str, Any],
    astroanthropology: dict[str, Any],
    *,
    years: float,
    runs: int = 16,
    seed: int = 1445,
    uncertainty: float = 0.10,
    target_frequency: float = 0.50,
) -> dict[str, Any]:
    """Scan one-dimensional model thresholds with common replay settings."""
    if runs < 2:
        raise ValueError("runs must be at least 2")
    target_frequency = _clamp01(target_frequency)

    specifications = [
        {
            "parameter": "capability_multiplier",
            "label": "Functional capability multiplier",
            "values": [0.50, 0.75, 1.00, 1.25, 1.50, 1.75, 2.00, 2.25, 2.50, 3.00, 3.50, 4.00],
            "direction": "higher-can-help",
        },
        {
            "parameter": "founder_size",
            "label": "Founder cohort size",
            "values": [50, 100, 250, 500, 1000, 2000, 5000],
            "direction": "higher-can-help-after-launch",
        },
        {
            "parameter": "exchange_strength",
            "label": "Post-settlement exchange strength",
            "values": [0.0, 0.15, 0.30, 0.45, 0.60, 0.80, 1.0],
            "direction": "context-dependent",
        },
        {
            "parameter": "resupply_strength",
            "label": "Resupply strength",
            "values": [0.0, 0.15, 0.35, 0.50, 0.65, 0.80, 1.0],
            "direction": "higher-can-help-after-arrival",
        },
        {
            "parameter": "infrastructure_shock",
            "label": "Infrastructure shock",
            "values": [0.0, 0.10, 0.25, 0.40, 0.60, 0.80, 1.0],
            "direction": "lower-is-favorable-after-arrival",
        },
    ]

    scans = []
    for spec in specifications:
        curve = []
        for raw_value in spec["values"]:
            astro = astroanthropology
            founder_size = 500
            exchange_strength = 0.30
            resupply_strength = 0.35
            infrastructure_shock = 0.0

            if spec["parameter"] == "capability_multiplier":
                astro = _scale_capability(astroanthropology, float(raw_value))
            elif spec["parameter"] == "founder_size":
                founder_size = int(raw_value)
            elif spec["parameter"] == "exchange_strength":
                exchange_strength = float(raw_value)
            elif spec["parameter"] == "resupply_strength":
                resupply_strength = float(raw_value)
            elif spec["parameter"] == "infrastructure_shock":
                infrastructure_shock = float(raw_value)

            replay = run_evolutionary_replay(
                system_data,
                astro,
                years=years,
                runs=runs,
                seed=seed,
                uncertainty=uncertainty,
                founder_size=founder_size,
                exchange_strength=exchange_strength,
                resupply_strength=resupply_strength,
                infrastructure_shock=infrastructure_shock,
            )
            curve.append(_curve_point(replay, float(raw_value)))

        crossings = [
            point for point in curve
            if point["non_no_launch_frequency"] >= target_frequency
        ]
        best = max(
            curve,
            key=lambda point: point["non_no_launch_frequency"],
        )
        scans.append({
            "parameter": spec["parameter"],
            "label": spec["label"],
            "direction": spec["direction"],
            "target_frequency": target_frequency,
            "threshold_reached": bool(crossings),
            "first_target_crossing_value": (
                crossings[0]["value"] if crossings else None
            ),
            "maximum_non_no_launch_frequency": best["non_no_launch_frequency"],
            "best_scanned_value": best["value"],
            "curve": curve,
        })

    reached = [row for row in scans if row["threshold_reached"]]
    return {
        "model": "transition_threshold_atlas_v0.1",
        "epistemic_level": "MODELED",
        "inputs": {
            "years": years,
            "runs_per_point": runs,
            "seed": seed,
            "uncertainty": uncertainty,
            "target_frequency": target_frequency,
        },
        "scans": scans,
        "summary": {
            "parameter_count": len(scans),
            "parameters_reaching_target": len(reached),
            "parameters_not_reaching_target": len(scans) - len(reached),
            "target_frequency": target_frequency,
        },
        "limitations": [
            "thresholds are properties of the current reduced-order model, not real-world engineering requirements",
            "one-dimensional scans vary one baseline control family at a time",
            "the grid is finite, so first crossings are bracket values rather than exact mathematical thresholds",
            "common replay seeds improve comparability but do not remove structural model uncertainty",
            "post-settlement variables cannot solve a launch-stage bottleneck unless the model reaches that stage",
        ],
    }
