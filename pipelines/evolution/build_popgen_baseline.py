#!/usr/bin/env python3
"""Build baseline population-genetics scenario."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.evolution.popgen import simulate_population_genetics

REFUGIA = ROOT / "frontend/data/refugia-baseline.json"
OUTPUTS = [
    ROOT / "frontend/data/popgen-baseline.json",
    ROOT / "docs/data/popgen-baseline.json",
]


def main() -> None:
    network = json.loads(REFUGIA.read_text(encoding="utf-8"))
    result = simulate_population_genetics(
        network,
        years=50_000.0,
        generation_years=28.0,
        technology_buffer=0.40,
    )
    encoded = json.dumps(result, indent=2)

    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
