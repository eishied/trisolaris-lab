#!/usr/bin/env python3
"""Build the public Phase 9.1 dynamic interplanetary-network baseline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.human.interplanetary_network import simulate_interplanetary_network

INPUT = ROOT / "frontend/data/interplanetary-baseline.json"
OUTPUTS = [
    ROOT / "frontend/data/interplanetary-network-baseline.json",
    ROOT / "docs/data/interplanetary-network-baseline.json",
]


def main() -> None:
    interplanetary = json.loads(INPUT.read_text(encoding="utf-8"))
    years = float(interplanetary.get("inputs", {}).get("years", 50_000))
    result = simulate_interplanetary_network(
        interplanetary,
        years=years,
        resupply_strength=0.35,
        infrastructure_shock=0.0,
        enable_return_migration=True,
    )
    encoded = json.dumps(result, indent=2)
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
