# Phase 11.2 — Manuscript Review Gate

Phase 11.2 separates machine-verifiable publication checks from checks that
require a human scientific reviewer.

## Automatic checks

The pipeline may verify:

- research-note status
- that arXiv readiness has not been granted automatically
- presence of the human-review requirement
- evidence-map presence
- release and experiment identity
- structural reference fields
- required figures and tables
- SHA-256 checksums for publication artifacts

## Human checks

The automated pipeline must not certify:

- claim-by-claim scientific review
- bibliographic correctness
- figure interpretation review
- independent replication
- reviewer identity

Those fields live in review-input.json and start as false or null.

## Promotion rule

When every automatic and human check passes, the gate may report:

promotion_eligible_for_working_paper = true

This does not change the manuscript status. Promotion remains a deliberate
human editorial action.

The system therefore cannot move a manuscript automatically from
RESEARCH_NOTE to WORKING_PAPER, ARXIV_CANDIDATE, ARXIV_READY, SUBMITTED or
PUBLISHED.

## Artifact integrity

The gate stores SHA-256 checksums for the manuscript, metadata, evidence,
experiments, figures and exact result tables. Checksums establish artifact
identity, not scientific validity.
