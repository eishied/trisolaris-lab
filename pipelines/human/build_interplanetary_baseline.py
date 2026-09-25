#!/usr/bin/env python3
"""Build the public Phase 9 interplanetary-settlement baseline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.human.interplanetary import simulate_interplanetary_settlement

SYSTEM = ROOT / "frontend/data/ltt1445.json"
ASTRO = ROOT / "frontend/data/astroanthropology-baseline.json"
OUTPUTS = [
    ROOT / "frontend/data/interplanetary-baseline.json",
    ROOT / "docs/data/interplanetary-baseline.json",
]


def main() -> None:
    system_data = json.loads(SYSTEM.read_text(encoding="utf-8"))
    astro = json.loads(ASTRO.read_text(encoding="utf-8"))
    years = float(astro.get("inputs", {}).get("years", 50_000))
    result = simulate_interplanetary_settlement(
        system_data,
        astro,
        years=years,
        founder_size=500,
        exchange_strength=0.30,
        launch_active=True,
    )
    encoded = json.dumps(result, indent=2)
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
