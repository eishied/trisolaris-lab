#!/usr/bin/env python3
"""Build baseline regional human-settlement support."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.human.settlement import evaluate_settlement_support

SURFACE = ROOT / "frontend/data/surface-baseline.json"
FOODWEB = ROOT / "frontend/data/foodweb-baseline.json"
OUTPUTS = [
    ROOT / "frontend/data/settlement-baseline.json",
    ROOT / "docs/data/settlement-baseline.json",
]


def main() -> None:
    surface = json.loads(SURFACE.read_text(encoding="utf-8"))
    foodweb = json.loads(FOODWEB.read_text(encoding="utf-8"))

    result = evaluate_settlement_support(
        surface,
        foodweb,
        pressure_bar=1.0,
        oxygen_fraction=0.21,
        technology_support=0.40,
        nutrient_availability=1.0,
    )

    encoded = json.dumps(result, indent=2)
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
