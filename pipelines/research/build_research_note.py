#!/usr/bin/env python3
"""Build the Phase 11.1 reproducible research-note package."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.research.note_builder import build_research_note

RELEASE = ROOT / "frontend/data/research-release-baseline.json"
REPLAY = ROOT / "frontend/data/evolutionary-replay-baseline.json"
COUNTERFACTUAL = ROOT / "frontend/data/counterfactual-replay-baseline.json"
SYSTEM = ROOT / "frontend/data/ltt1445.json"

NOTE_DIR = ROOT / "publications/research-notes/RN-TRISOLARIS-0001"
PUBLIC_SUMMARIES = [
    ROOT / "frontend/data/research-note-baseline.json",
    ROOT / "docs/data/research-note-baseline.json",
]


def main() -> None:
    release = json.loads(RELEASE.read_text(encoding="utf-8"))
    replay = json.loads(REPLAY.read_text(encoding="utf-8"))
    counterfactual = json.loads(COUNTERFACTUAL.read_text(encoding="utf-8"))
    system = json.loads(SYSTEM.read_text(encoding="utf-8"))

    package = build_research_note(release, replay, counterfactual, system)
    for relative, text_content in package.items():
        output = NOTE_DIR / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text_content, encoding="utf-8")
        print(f"Wrote {output}")

    summary = package["summary.json"]
    for output in PUBLIC_SUMMARIES:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(summary, encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
