#!/usr/bin/env python3
"""Build the Phase 12.1 adaptive threshold-refinement baseline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.evolution.threshold_refinement import refine_capability_thresholds

SYSTEM = ROOT / "frontend/data/ltt1445.json"
ASTRO = ROOT / "frontend/data/astroanthropology-baseline.json"
COARSE = ROOT / "frontend/data/transition-thresholds-baseline.json"
OUTPUTS = [
    ROOT / "frontend/data/threshold-refinement-baseline.json",
    ROOT / "docs/data/threshold-refinement-baseline.json",
]


def main() -> None:
    system = json.loads(SYSTEM.read_text(encoding="utf-8"))
    astro = json.loads(ASTRO.read_text(encoding="utf-8"))
    coarse = json.loads(COARSE.read_text(encoding="utf-8"))
    years = float(astro.get("inputs", {}).get("years", 50_000))
    result = refine_capability_thresholds(
        system,
        astro,
        coarse,
        years=years,
        runs=32,
        seed=1445,
        uncertainty=0.10,
        target_frequency=0.50,
        iterations=8,
    )
    encoded = json.dumps(result, indent=2) + "\n"
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
