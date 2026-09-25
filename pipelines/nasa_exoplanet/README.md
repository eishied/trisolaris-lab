# NASA Exoplanet Archive ingestion

Initial official-source ingestion pipeline.

## Example

```bash
python pipelines/nasa_exoplanet/fetch_system.py "LTT 1445 A"
```

The script queries the NASA Exoplanet Archive `ps` table through TAP and produces:

- immutable raw CSV,
- JSON provenance manifest,
- SHA-256 checksum,
- exact ADQL query.

Raw datasets are intentionally ignored by Git by default; publication-grade snapshots should be promoted through the provenance process rather than committed casually.
