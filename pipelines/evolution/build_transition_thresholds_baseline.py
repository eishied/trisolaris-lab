#!/usr/bin/env python3
"""Build the Phase 12 transition-threshold atlas baseline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.evolution.thresholds import scan_transition_thresholds

SYSTEM = ROOT / "frontend/data/ltt1445.json"
ASTRO = ROOT / "frontend/data/astroanthropology-baseline.json"
OUTPUTS = [
    ROOT / "frontend/data/transition-thresholds-baseline.json",
    ROOT / "docs/data/transition-thresholds-baseline.json",
]


def main() -> None:
    system = json.loads(SYSTEM.read_text(encoding="utf-8"))
    astro = json.loads(ASTRO.read_text(encoding="utf-8"))
    years = float(astro.get("inputs", {}).get("years", 50_000))
    result = scan_transition_thresholds(
        system,
        astro,
        years=years,
        runs=16,
        seed=1445,
        uncertainty=0.10,
        target_frequency=0.50,
    )
    encoded = json.dumps(result, indent=2) + "\n"
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
