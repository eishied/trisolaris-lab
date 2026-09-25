#!/usr/bin/env python3
"""Build the baseline atmosphere-water-biosphere-potential dataset."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.planetary.surface_systems import solve_surface_systems

CLIMATE = ROOT / "frontend/data/climate-baseline.json"
DATASET = ROOT / "frontend/data/ltt1445.json"
OUTPUTS = [
    ROOT / "frontend/data/surface-baseline.json",
    ROOT / "docs/data/surface-baseline.json",
]


def main() -> None:
    climate = json.loads(CLIMATE.read_text(encoding="utf-8"))
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))

    result = solve_surface_systems(
        climate,
        pressure_bar=1.0,
        water_inventory_earth_oceans=1.0,
        stellar_flux_earth=float(climate["inputs"]["stellar_flux_earth"]),
        spectral_productivity_factor=0.55,
    )
    result["candidate"] = {
        "name": dataset["hypothetical_experiment"]["name"],
        "pressure_bar_assumption": 1.0,
        "water_inventory_earth_oceans_assumption": 1.0,
    }

    encoded = json.dumps(result, indent=2)
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
