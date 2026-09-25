#!/usr/bin/env python3
"""Manuscript review gate for TRISOLARIS LAB Phase 11.2."""

from __future__ import annotations

import hashlib
import re
from typing import Any


HUMAN_FIELDS = (
    "claim_review_completed",
    "references_review_completed",
    "figures_review_completed",
    "independent_replication_completed",
)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _reference_structure_ok(text: str) -> bool:
    if "@misc{" not in text and "@article{" not in text and "@inproceedings{" not in text:
        return False
    return bool(
        re.search(r"\bdoi\s*=", text, re.IGNORECASE)
        or re.search(r"\beprint\s*=", text, re.IGNORECASE)
        or re.search(r"\burl\s*=", text, re.IGNORECASE)
    )


def evaluate_manuscript_review_gate(
    metadata: dict[str, Any],
    evidence: list[dict[str, Any]],
    experiments: dict[str, Any],
    references_text: str,
    artifacts: dict[str, str],
    review_input: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate machine-verifiable and explicitly human manuscript checks."""

    automatic_checks = [
        {
            "check": "research_note_status",
            "passed": metadata.get("status") == "RESEARCH_NOTE",
            "detail": str(metadata.get("status")),
        },
        {
            "check": "arxiv_not_auto_promoted",
            "passed": metadata.get("arxiv_ready") is False,
            "detail": f"arxiv_ready={metadata.get('arxiv_ready')}",
        },
        {
            "check": "human_review_flag_present",
            "passed": metadata.get("human_review_required") is True,
            "detail": f"human_review_required={metadata.get('human_review_required')}",
        },
        {
            "check": "evidence_map_present",
            "passed": bool(evidence),
            "detail": f"{len(evidence)} evidence items",
        },
        {
            "check": "experiment_identity_present",
            "passed": bool(
                experiments.get("release_id")
                and experiments.get("experiment_id")
            ),
            "detail": (
                f"{experiments.get('release_id')} / "
                f"{experiments.get('experiment_id')}"
            ),
        },
        {
            "check": "reference_structure_present",
            "passed": _reference_structure_ok(references_text),
            "detail": "BibTeX contains a DOI, eprint or URL field",
        },
        {
            "check": "figures_and_tables_present",
            "passed": all(
                key in artifacts and bool(artifacts[key].strip())
                for key in (
                    "figures/replay-outcomes.svg",
                    "figures/counterfactual-deltas.svg",
                    "tables/outcome-frequencies.tsv",
                    "tables/counterfactual-deltas.tsv",
                )
            ),
            "detail": "required reproducible figures and tables",
        },
    ]

    checksums = {
        name: _sha256(text)
        for name, text in sorted(artifacts.items())
        if text.strip()
    }
    automatic_checks.append({
        "check": "artifact_checksums_created",
        "passed": len(checksums) >= 4,
        "detail": f"{len(checksums)} checksums",
    })

    human_checks = []
    for field in HUMAN_FIELDS:
        human_checks.append({
            "check": field,
            "passed": review_input.get(field) is True,
            "detail": (
                "human certified"
                if review_input.get(field) is True
                else "awaiting human certification"
            ),
        })

    reviewer = review_input.get("reviewer")
    reviewer_check = {
        "check": "reviewer_identified",
        "passed": bool(reviewer),
        "detail": reviewer or "awaiting reviewer identity",
    }
    human_checks.append(reviewer_check)

    automatic_passed = all(row["passed"] for row in automatic_checks)
    human_passed = all(row["passed"] for row in human_checks)
    promotion_eligible = automatic_passed and human_passed

    return {
        "model": "manuscript_review_gate_v0.1",
        "publication_state": metadata.get("status"),
        "automatic_checks": automatic_checks,
        "human_checks": human_checks,
        "artifact_checksums_sha256": checksums,
        "review_input": {
            "reviewer": reviewer,
            "review_notes": review_input.get("review_notes", ""),
            **{
                field: bool(review_input.get(field))
                for field in HUMAN_FIELDS
            },
        },
        "summary": {
            "automatic_checks_passed": sum(
                1 for row in automatic_checks if row["passed"]
            ),
            "automatic_checks_total": len(automatic_checks),
            "human_checks_passed": sum(
                1 for row in human_checks if row["passed"]
            ),
            "human_checks_total": len(human_checks),
            "promotion_eligible_for_working_paper": promotion_eligible,
            "status_changed_automatically": False,
        },
        "limitations": [
            "reference structure validation does not prove bibliographic correctness",
            "checksums prove artifact identity, not scientific validity",
            "human review fields cannot be certified by the automated pipeline",
            "promotion eligibility does not itself change publication state",
            "independent replication requires a separate human-attested replication record",
        ],
    }
