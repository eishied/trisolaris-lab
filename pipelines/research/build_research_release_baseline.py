#!/usr/bin/env python3
"""Build the Phase 11 public research release manifest."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.research.release import build_research_release_manifest

SYSTEM = ROOT / "frontend/data/ltt1445.json"
DATASETS = [
    ("climate", "frontend/data/climate-baseline.json"),
    ("surface", "frontend/data/surface-baseline.json"),
    ("foodweb", "frontend/data/foodweb-baseline.json"),
    ("settlement", "frontend/data/settlement-baseline.json"),
    ("lineage", "frontend/data/lineage-baseline.json"),
    ("population_genetics", "frontend/data/popgen-baseline.json"),
    ("demography", "frontend/data/demography-baseline.json"),
    ("astroanthropology", "frontend/data/astroanthropology-baseline.json"),
    ("interplanetary", "frontend/data/interplanetary-baseline.json"),
    ("interplanetary_network", "frontend/data/interplanetary-network-baseline.json"),
    ("offworld_divergence", "frontend/data/offworld-divergence-baseline.json"),
    ("evolutionary_replay", "frontend/data/evolutionary-replay-baseline.json"),
    ("counterfactual_replay", "frontend/data/counterfactual-replay-baseline.json"),
]
OUTPUTS = [
    ROOT / "frontend/data/research-release-baseline.json",
    ROOT / "docs/data/research-release-baseline.json",
    ROOT / "research/evidence/research-release-baseline.json",
]

def commit_sha() -> str:
    if os.environ.get("GITHUB_SHA"):
        return os.environ["GITHUB_SHA"]
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "unknown"

def main() -> None:
    system = json.loads(SYSTEM.read_text(encoding="utf-8"))
    datasets = []
    for name, relative in DATASETS:
        path = ROOT / relative
        datasets.append((name, relative, json.loads(path.read_text(encoding="utf-8"))))
    result = build_research_release_manifest(
        system, datasets, commit_sha=commit_sha()
    )
    encoded = json.dumps(result, indent=2)
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(f"Wrote {output}")

if __name__ == "__main__":
    main()
