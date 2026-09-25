# Data Provenance Contract

## Immutable raw layer

`data/raw/` stores source responses as retrieved. Raw files are append-only snapshots and must not be manually edited.

## Processed layer

`data/processed/` contains normalized schemas, unit conversions, cross-matches and quality flags.

## Derived layer

`data/derived/` contains TRISOLARIS-computed quantities such as combined irradiation, habitability metrics, stability diagnostics and regional climate indices.

## Snapshot layer

`data/snapshots/` captures the exact datasets used by a reproducible experiment or publication.

## Dataset manifest

Every dataset snapshot should include:

```yaml
dataset_id: ...
source:
  authority: ...
  service: ...
  table: ...
  endpoint: ...
retrieved_at: ...
query: ...
format: ...
epistemic_level: OBSERVED
checksum: ...
citation:
  required: true
  doi: ...
transformations: []
parents: []
```

## No silent overwrite

If an official archive revises a parameter, both historical values remain discoverable. Experiments retain the snapshot they originally used.

## Reproducibility identity

Every experiment should record:
- git commit
- dataset snapshot IDs
- model versions
- configuration
- random seeds
- run timestamp
- output checksums
