#!/usr/bin/env python3
"""Build baseline refugia and migration network from settlement support."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.human.refugia import build_refugia_network

SETTLEMENT = ROOT / "frontend/data/settlement-baseline.json"
OUTPUTS = [
    ROOT / "frontend/data/refugia-baseline.json",
    ROOT / "docs/data/refugia-baseline.json",
]


def main() -> None:
    settlement = json.loads(SETTLEMENT.read_text(encoding="utf-8"))
    result = build_refugia_network(settlement, mobility=0.45)

    encoded = json.dumps(result, indent=2)
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
