#!/usr/bin/env python3
"""Build the public Phase 10 evolutionary-replay baseline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.evolution.replay import run_evolutionary_replay

SYSTEM = ROOT / "frontend/data/ltt1445.json"
ASTRO = ROOT / "frontend/data/astroanthropology-baseline.json"
OUTPUTS = [
    ROOT / "frontend/data/evolutionary-replay-baseline.json",
    ROOT / "docs/data/evolutionary-replay-baseline.json",
]


def main() -> None:
    system_data = json.loads(SYSTEM.read_text(encoding="utf-8"))
    astro = json.loads(ASTRO.read_text(encoding="utf-8"))
    years = float(astro.get("inputs", {}).get("years", 50_000))
    result = run_evolutionary_replay(
        system_data,
        astro,
        years=years,
        runs=64,
        seed=1445,
        uncertainty=0.25,
        founder_size=500,
        exchange_strength=0.30,
        resupply_strength=0.35,
        infrastructure_shock=0.0,
    )
    encoded = json.dumps(result, indent=2)
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
