#!/usr/bin/env python3
"""Build the Phase 11.2 manuscript review-gate manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.research.review_gate import evaluate_manuscript_review_gate

NOTE_DIR = ROOT / "publications/research-notes/RN-TRISOLARIS-0001"
OUTPUTS = [
    NOTE_DIR / "review-gate.json",
    ROOT / "frontend/data/manuscript-review-gate-baseline.json",
    ROOT / "docs/data/manuscript-review-gate-baseline.json",
]


def read_text(relative: str) -> str:
    return (NOTE_DIR / relative).read_text(encoding="utf-8")


def main() -> None:
    metadata = json.loads(read_text("metadata.json"))
    evidence = json.loads(read_text("evidence.json"))
    experiments = json.loads(read_text("experiments.json"))
    review_input = json.loads(read_text("review-input.json"))
    references = read_text("references.bib")

    artifact_names = (
        "figures/replay-outcomes.svg",
        "figures/counterfactual-deltas.svg",
        "tables/outcome-frequencies.tsv",
        "tables/counterfactual-deltas.tsv",
        "paper.md",
        "metadata.json",
        "evidence.json",
        "experiments.json",
    )
    artifacts = {name: read_text(name) for name in artifact_names}

    result = evaluate_manuscript_review_gate(
        metadata,
        evidence,
        experiments,
        references,
        artifacts,
        review_input,
    )
    encoded = json.dumps(result, indent=2) + "\n"
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
