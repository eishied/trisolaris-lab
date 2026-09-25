#!/usr/bin/env python3
"""Build the public LTT 1445 dataset from official NASA records plus cited literature metadata."""

from __future__ import annotations

import csv
import datetime as dt
import io
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "data/catalog/systems/ltt1445.json"
OUTPUTS = [
    ROOT / "frontend/data/ltt1445.json",
    ROOT / "docs/data/ltt1445.json",
]
TAP = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"

QUERY = """
select hostname,pl_name,default_flag,pl_orbper,pl_orbsmax,pl_orbeccen,
       pl_rade,pl_bmasse,pl_eqt,st_teff,st_rad,st_mass,sy_dist,disc_year
from ps
where hostname='LTT 1445 A' and default_flag=1
""".strip()


def number(value: str):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return value


def fetch_csv() -> str:
    url = TAP + "?" + urlencode({"query": QUERY, "format": "csv"})
    request = Request(url, headers={"User-Agent": "trisolaris-lab/0.1"})
    with urlopen(request, timeout=90) as response:
        return response.read().decode("utf-8")


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    raw = fetch_csv()
    reader = csv.DictReader(io.StringIO(raw))
    planets = []

    for row in reader:
        planets.append({
            "name": row.get("pl_name"),
            "host": row.get("hostname"),
            "period_days": number(row.get("pl_orbper")),
            "semi_major_axis_au": number(row.get("pl_orbsmax")),
            "eccentricity": number(row.get("pl_orbeccen")),
            "radius_earth": number(row.get("pl_rade")),
            "mass_earth": number(row.get("pl_bmasse")),
            "equilibrium_temperature_k": number(row.get("pl_eqt")),
            "discovery_year": number(row.get("disc_year")),
            "epistemic_level": "OBSERVED",
            "source": "NASA Exoplanet Archive / ps"
        })

    payload = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "official-nasa-plus-literature",
        "system": catalog["system"],
        "stars": catalog["stars"],
        "hierarchy": catalog["hierarchy"],
        "observed_planets": planets,
        "hypothetical_experiment": catalog["hypothetical_experiment"],
        "literature": catalog["literature"],
        "provenance": {
            "nasa_query": QUERY,
            "nasa_endpoint": TAP,
            "observed_planet_count": len(planets),
            "epistemic_rule": "NASA planet rows are OBSERVED; triple-star properties are LITERATURE; H-01 is SPECULATIVE."
        }
    }

    encoded = json.dumps(payload, indent=2)
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
        print(f"Wrote {output} with {len(planets)} observed planets.")


if __name__ == "__main__":
    main()
