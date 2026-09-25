#!/usr/bin/env python3
"""Build the baseline H-01 analytic orbital screen for the public explorer."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.orbital.screen import screen_candidate
DATASET = ROOT / "frontend/data/ltt1445.json"
OUTPUTS = [
    ROOT / "frontend/data/orbital-screen.json",
    ROOT / "docs/data/orbital-screen.json",
]


def main() -> None:
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    h01 = dataset["hypothetical_experiment"]
    result = screen_candidate(
        dataset,
        candidate_a_au=float(h01["semi_major_axis_au"]),
        candidate_mass_earth=1.0,
    )
    encoded = json.dumps(result, indent=2)

    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
