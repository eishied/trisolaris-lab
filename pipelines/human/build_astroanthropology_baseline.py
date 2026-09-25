#!/usr/bin/env python3
"""Build the public Phase 8 astroanthropology baseline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.human.astroanthropology import simulate_astroanthropology

HISTORY = ROOT / "frontend/data/planetary-history-baseline.json"
DEMOGRAPHY = ROOT / "frontend/data/demography-baseline.json"
OUTPUTS = [
    ROOT / "frontend/data/astroanthropology-baseline.json",
    ROOT / "docs/data/astroanthropology-baseline.json",
]


def main() -> None:
    history = json.loads(HISTORY.read_text(encoding="utf-8"))
    demography = json.loads(DEMOGRAPHY.read_text(encoding="utf-8"))
    result = simulate_astroanthropology(
        history,
        demography,
        years=float(history.get("inputs", {}).get("years", 50_000)),
        exchange_strength=1.0,
    )
    encoded = json.dumps(result, indent=2)
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
