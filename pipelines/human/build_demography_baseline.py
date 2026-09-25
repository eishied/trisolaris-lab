#!/usr/bin/env python3
"""Build a no-disturbance baseline demographic history."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.human.demography import simulate_demography

HISTORY = ROOT / "frontend/data/planetary-history-baseline.json"
OUTPUTS = [
    ROOT / "frontend/data/demography-baseline.json",
    ROOT / "docs/data/demography-baseline.json",
]


def main() -> None:
    history = json.loads(HISTORY.read_text(encoding="utf-8"))
    result = simulate_demography(
        history,
        total_years=50_000.0,
        view_years=50_000.0,
        disturbance="none",
        severity=0.0,
    )
    encoded = json.dumps(result, indent=2)
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
