#!/usr/bin/env python3
"""Research release manifest and evidence ledger for TRISOLARIS LAB Phase 11."""

from __future__ import annotations

from typing import Any


def _dataset_entry(name: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "path": path,
        "model": payload.get("model"),
        "epistemic_level": payload.get("epistemic_level"),
        "inputs": payload.get("inputs", {}),
        "summary": payload.get("summary", {}),
        "limitations": payload.get("limitations", []),
    }


def build_research_release_manifest(
    system_data: dict[str, Any],
    datasets: list[tuple[str, str, dict[str, Any]]],
    *,
    commit_sha: str,
    release_id: str = "REL-TRISOLARIS-0001",
    experiment_id: str = "EXP-TRISOLARIS-0001",
) -> dict[str, Any]:
    """Build an auditable research-note release from committed model outputs."""
    entries = [_dataset_entry(name, path, payload) for name, path, payload in datasets]
    by_name = {entry["name"]: entry for entry in entries}

    replay = by_name.get("evolutionary_replay", {})
    counterfactual = by_name.get("counterfactual_replay", {})
    replay_inputs = replay.get("inputs", {})
    counter_inputs = counterfactual.get("inputs", {})

    provenance = system_data.get("provenance", {})
    h01 = system_data.get("hypothetical_experiment", {})
    observed_planets = system_data.get("observed_planets", [])

    evidence = [
        {
            "evidence_id": "EV-OBS-0001",
            "epistemic_level": "OBSERVED",
            "claim_scope": "confirmed planets around LTT 1445 A",
            "source": provenance.get("nasa_endpoint"),
            "detail": f"{len(observed_planets)} planet rows retained from the official archive snapshot",
        },
        {
            "evidence_id": "EV-LIT-0001",
            "epistemic_level": "LITERATURE",
            "claim_scope": "hierarchical triple-star architecture",
            "source": "repository literature registry",
            "detail": system_data.get("system", {}).get("architecture"),
        },
        {
            "evidence_id": "EV-SPEC-0001",
            "epistemic_level": "SPECULATIVE",
            "claim_scope": "H-01 experimental world",
            "source": "TRISOLARIS scenario definition",
            "detail": h01.get("notes"),
        },
    ]

    for index, entry in enumerate(entries, start=1):
        evidence.append({
            "evidence_id": f"EV-MOD-{index:04d}",
            "epistemic_level": entry.get("epistemic_level") or "MODELED",
            "claim_scope": entry["name"],
            "source": entry["path"],
            "detail": entry.get("model") or "declared dataset without model id",
        })

    all_models_declared = all(entry.get("model") for entry in entries)
    all_limitations_declared = all(bool(entry.get("limitations")) for entry in entries)
    replay_seed = replay_inputs.get("seed")
    counter_seed = counter_inputs.get("seed")

    checks = [
        {
            "check": "official_observed_source",
            "passed": bool(provenance.get("nasa_endpoint") and observed_planets),
            "detail": "NASA source and observed planet rows are present",
        },
        {
            "check": "speculative_world_labeled",
            "passed": h01.get("epistemic_level") == "SPECULATIVE",
            "detail": "H-01 remains explicitly speculative",
        },
        {
            "check": "model_versions_declared",
            "passed": all_models_declared,
            "detail": f"{sum(1 for entry in entries if entry.get('model'))}/{len(entries)} datasets declare a model id",
        },
        {
            "check": "limitations_declared",
            "passed": all_limitations_declared,
            "detail": f"{sum(1 for entry in entries if entry.get('limitations'))}/{len(entries)} datasets declare limitations",
        },
        {
            "check": "replay_seed_declared",
            "passed": replay_seed is not None,
            "detail": f"Evolutionary Replay seed: {replay_seed}",
        },
        {
            "check": "counterfactual_seed_declared",
            "passed": counter_seed is not None,
            "detail": f"Counterfactual Replay seed: {counter_seed}",
        },
        {
            "check": "git_commit_declared",
            "passed": bool(commit_sha and commit_sha != "unknown"),
            "detail": commit_sha,
        },
    ]

    passed = sum(1 for check in checks if check["passed"])
    research_note_ready = passed == len(checks)

    replay_outcomes = replay.get("summary", {})
    counter_summary = counterfactual.get("summary", {})

    claims = []
    if replay_outcomes:
        claims.append({
            "claim_id": "CLM-0001",
            "text": (
                f"Under the declared replay envelope, the dominant modeled outcome is "
                f"{replay_outcomes.get('dominant_outcome')} with ensemble frequency "
                f"{float(replay_outcomes.get('dominant_frequency', 0.0)):.3f}."
            ),
            "evidence_ids": ["EV-MOD-" + f"{list(by_name).index('evolutionary_replay') + 1:04d}"],
            "qualifier": "ensemble frequency is model-conditional and is not a real-world probability",
        })
    if counter_summary:
        claims.append({
            "claim_id": "CLM-0002",
            "text": (
                f"In the paired baseline counterfactual, "
                f"{float(counter_summary.get('outcome_flip_fraction', 0.0)):.3f} of paired runs "
                f"change outcome class."
            ),
            "evidence_ids": ["EV-MOD-" + f"{list(by_name).index('counterfactual_replay') + 1:04d}"],
            "qualifier": "paired differences are causal only within the declared model intervention",
        })

    return {
        "release_id": release_id,
        "experiment_id": experiment_id,
        "publication_state": "RESEARCH_NOTE" if research_note_ready else "IDEA",
        "epistemic_level": "MODELED",
        "title": "TRISOLARIS baseline evolutionary replay and counterfactual release",
        "research_question": (
            "Are modeled multiplanetary outcomes robust to declared uncertainty, and which "
            "single interventions alter the simulated historical trajectory?"
        ),
        "git_commit": commit_sha,
        "datasets": entries,
        "evidence_ledger": evidence,
        "claims": claims,
        "validation_checks": checks,
        "reproducibility": {
            "replay_seed": replay_seed,
            "counterfactual_seed": counter_seed,
            "dataset_count": len(entries),
            "model_count": sum(1 for entry in entries if entry.get("model")),
            "all_limitations_declared": all_limitations_declared,
            "code_and_data_available": True,
        },
        "summary": {
            "checks_passed": passed,
            "checks_total": len(checks),
            "research_note_ready": research_note_ready,
            "claim_count": len(claims),
            "evidence_item_count": len(evidence),
        },
        "limitations": [
            "RESEARCH_NOTE readiness is an internal reproducibility gate, not peer review",
            "the release does not claim ARXIV_READY status",
            "model outputs inherit the limitations of every upstream model in the causal chain",
            "deep-time outcomes remain scenario-dependent and are not forecasts",
            "human review is required before any external scientific submission",
        ],
        "next_state_requirements": [
            "claim-by-claim evidence review",
            "structured uncertainty and sensitivity review",
            "independent replication of key experiments",
            "validated figures and tables tied to experiment ids",
            "complete references and manuscript review",
        ],
    }
