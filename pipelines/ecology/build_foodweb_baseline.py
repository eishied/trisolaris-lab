#!/usr/bin/env python3
"""Build baseline ecological-guild support from the current surface model."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.ecology.food_web import evaluate_food_web

SURFACE = ROOT / "frontend/data/surface-baseline.json"
OUTPUTS = [
    ROOT / "frontend/data/foodweb-baseline.json",
    ROOT / "docs/data/foodweb-baseline.json",
]


def main() -> None:
    surface = json.loads(SURFACE.read_text(encoding="utf-8"))
    result = evaluate_food_web(
        surface,
        oxygen_fraction=0.21,
        nutrient_availability=1.0,
        life_seeded=False,
    )

    encoded = json.dumps(result, indent=2)
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
