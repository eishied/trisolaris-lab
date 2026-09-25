#!/usr/bin/env python3
"""Build Phase 10.1 paired counterfactual baseline."""

from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.evolution.counterfactual import compare_counterfactual

SYSTEM = ROOT / "frontend/data/ltt1445.json"
ASTRO = ROOT / "frontend/data/astroanthropology-baseline.json"
OUTPUTS = [
    ROOT / "frontend/data/counterfactual-replay-baseline.json",
    ROOT / "docs/data/counterfactual-replay-baseline.json",
]

def main() -> None:
    system = json.loads(SYSTEM.read_text(encoding="utf-8"))
    astro = json.loads(ASTRO.read_text(encoding="utf-8"))
    years = float(astro.get("inputs", {}).get("years", 50_000))
    result = compare_counterfactual(
        system, astro, years=years, parameter="capability",
        intervention_fraction=0.20, runs=64, seed=1445, uncertainty=0.25,
    )
    encoded = json.dumps(result, indent=2)
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(f"Wrote {output}")

if __name__ == "__main__":
    main()
