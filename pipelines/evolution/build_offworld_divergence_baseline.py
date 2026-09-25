#!/usr/bin/env python3
"""Build the public Phase 9.2 off-world divergence baseline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.evolution.offworld import simulate_offworld_divergence

INTERPLANETARY = ROOT / "frontend/data/interplanetary-baseline.json"
NETWORK = ROOT / "frontend/data/interplanetary-network-baseline.json"
OUTPUTS = [
    ROOT / "frontend/data/offworld-divergence-baseline.json",
    ROOT / "docs/data/offworld-divergence-baseline.json",
]


def main() -> None:
    interplanetary = json.loads(INTERPLANETARY.read_text(encoding="utf-8"))
    network = json.loads(NETWORK.read_text(encoding="utf-8"))
    years = float(network.get("inputs", {}).get("years", 50_000))
    result = simulate_offworld_divergence(
        interplanetary,
        network,
        years=years,
        generation_years=28.0,
    )
    encoded = json.dumps(result, indent=2)
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
