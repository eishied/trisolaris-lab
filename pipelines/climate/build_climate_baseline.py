#!/usr/bin/env python3
"""Build the baseline H-01 latitudinal climate dataset."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engine.climate.latitudinal_ebm import solve_latitudinal_climate

DATASET = ROOT / "frontend/data/ltt1445.json"
OUTPUTS = [
    ROOT / "frontend/data/climate-baseline.json",
    ROOT / "docs/data/climate-baseline.json",
]


def main() -> None:
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    stars = {s["id"]: s for s in dataset["stars"]}
    h01 = dataset["hypothetical_experiment"]

    a = float(h01["semi_major_axis_au"])
    outer_sep_au = (
        float(dataset["hierarchy"]["outer_projected_separation_arcsec_approx"])
        * float(dataset["system"]["distance_pc"])
    )

    flux = (
        float(stars["A"]["luminosity_solar"]) / (a * a)
        + (float(stars["B"]["luminosity_solar"]) + float(stars["C"]["luminosity_solar"]))
        / (outer_sep_au * outer_sep_au)
    )

    result = solve_latitudinal_climate(
        stellar_flux_earth=flux,
        albedo=float(h01["albedo"]),
        greenhouse_k=float(h01["greenhouse_k"]),
    )

    result["candidate"] = {
        "name": h01["name"],
        "semimajor_axis_au": a,
    }

    encoded = json.dumps(result, indent=2)
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
