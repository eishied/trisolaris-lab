# Phase 11.1 — Research Note Builder

Phase 11.1 converts a validated Phase 11 research release into a complete,
versioned research-note package.

The builder generates:

- paper.md
- metadata.json
- evidence.json
- experiments.json
- references.bib
- REPRODUCE.md
- exact TSV result tables
- SVG figures generated directly from committed baseline data
- summary.json

## Source of truth

The note is generated from the committed research release, Evolutionary Replay,
paired Counterfactual Replay and the LTT 1445 system dataset.

The manuscript is downstream of the evidence ledger rather than a separate
hand-maintained interpretation.

## Editorial gate

The builder accepts only a release that already has state RESEARCH_NOTE and has
passed the Phase 11 reproducibility gate.

It always writes:

- arxiv_ready = false
- human_review_required = true

Generating a complete note does not promote it to WORKING_PAPER,
ARXIV_CANDIDATE, ARXIV_READY, SUBMITTED or PUBLISHED.

## Figures and tables

Figures are deterministic SVG files generated from exact baseline frequencies.
Tables are TSV files with exact machine-readable values. This keeps every
visual result tied to the experiment rather than to manual chart editing.

## Next

Phase 11.2 should add manuscript review gates: reference resolution,
claim-by-claim review status, figure/table checksum manifests and an
independent-replication slot before a note can be promoted to WORKING_PAPER.
