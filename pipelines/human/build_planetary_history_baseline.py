#!/usr/bin/env python3
"""Build the baseline planetary population-history dataset."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.human.planetary_history import simulate_planetary_history

REFUGIA = ROOT / "frontend/data/refugia-baseline.json"
LINEAGES = ROOT / "frontend/data/lineage-baseline.json"
OUTPUTS = [
    ROOT / "frontend/data/planetary-history-baseline.json",
    ROOT / "docs/data/planetary-history-baseline.json",
]


def main() -> None:
    refugia = json.loads(REFUGIA.read_text(encoding="utf-8"))
    lineages = json.loads(LINEAGES.read_text(encoding="utf-8"))
    result = simulate_planetary_history(
        refugia,
        lineages,
        years=50_000.0,
        technology_support=0.40,
        mobility=0.45,
    )
    encoded = json.dumps(result, indent=2)
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
