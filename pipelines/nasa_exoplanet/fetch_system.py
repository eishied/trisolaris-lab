#!/usr/bin/env python3
"""Fetch a named host system from the NASA Exoplanet Archive TAP service.

Raw responses and manifests are intended to be immutable provenance inputs.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

TAP_SYNC = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"

COLUMNS = [
    "hostname", "pl_name", "default_flag", "sy_snum", "sy_pnum",
    "pl_orbper", "pl_orbsmax", "pl_orbeccen", "pl_rade", "pl_bmasse",
    "st_teff", "st_rad", "st_mass", "st_met", "sy_dist", "ra", "dec",
]


def fetch(host: str, output_dir: Path) -> tuple[Path, Path]:
    safe_host = host.replace(" ", "_").replace("/", "_")
    query = (
        f"select {','.join(COLUMNS)} from ps "
        f"where hostname='{host.replace(chr(39), chr(39)*2)}' and default_flag=1"
    )
    params = urlencode({"query": query, "format": "csv"})
    url = f"{TAP_SYNC}?{params}"

    request = Request(url, headers={"User-Agent": "trisolaris-lab/0.0.1"})
    with urlopen(request, timeout=60) as response:
        payload = response.read()

    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    csv_path = output_dir / f"{safe_host}-{timestamp}.csv"
    csv_path.write_bytes(payload)

    digest = hashlib.sha256(payload).hexdigest()
    manifest = {
        "dataset_id": f"nasa-exoplanet-ps-{safe_host}-{timestamp}",
        "epistemic_level": "OBSERVED",
        "source": {
            "authority": "NASA/IPAC",
            "service": "NASA Exoplanet Archive",
            "protocol": "TAP",
            "endpoint": TAP_SYNC,
            "table": "ps",
        },
        "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "query": query,
        "format": "csv",
        "sha256": digest,
        "raw_file": str(csv_path),
        "citation_required": True,
        "transformations": [],
    }
    manifest_path = output_dir / f"{safe_host}-{timestamp}.manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return csv_path, manifest_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="Exact NASA Exoplanet Archive hostname")
    parser.add_argument(
        "--output-dir",
        default="data/raw/nasa_exoplanet",
        type=Path,
    )
    args = parser.parse_args()
    csv_path, manifest_path = fetch(args.host, args.output_dir)
    print(csv_path)
    print(manifest_path)


if __name__ == "__main__":
    main()
