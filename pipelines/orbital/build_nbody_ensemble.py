#!/usr/bin/env python3
"""Generate the public pilot N-body ensemble for H-01."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.orbital.nbody import run_ensemble

DATASET = ROOT / "frontend/data/ltt1445.json"
OUTPUTS = [
    ROOT / "frontend/data/nbody-ensemble.json",
    ROOT / "docs/data/nbody-ensemble.json",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=12)
    parser.add_argument("--years", type=float, default=100.0)
    parser.add_argument("--samples", type=int, default=160)
    args = parser.parse_args()

    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    h01 = dataset["hypothetical_experiment"]
    result = run_ensemble(
        dataset,
        candidate_a_au=float(h01["semi_major_axis_au"]),
        runs=args.runs,
        years=args.years,
        samples=args.samples,
    )
    encoded = json.dumps(result, indent=2)

    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
