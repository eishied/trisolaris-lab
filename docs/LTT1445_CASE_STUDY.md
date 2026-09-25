# Case Study 001 — LTT 1445 ABC

## Why this system

LTT 1445 ABC is a nearby hierarchical triple of M dwarfs. Known planets orbit component A, while B and C form a tighter pair at larger separation from A.

It is useful for TRISOLARIS because it separates two questions:

1. What can be reconstructed from a real observed multi-star system?
2. What happens if we introduce a clearly labeled hypothetical world and test survival conditions?

## Evidence layers

### Literature
Initial stellar masses/radii and hierarchical architecture are stored in:
`data/catalog/systems/ltt1445.json`.

The catalog cites Winters et al. (2019) and the subsequent multi-planet study.

### Official archive
Known planet properties are refreshed from the NASA Exoplanet Archive `ps` table.

### Speculative experiment
`TRISOLARIS H-01` is not an observed planet. It is an interactive experimental world whose orbital distance, albedo and greenhouse offset can be changed.

## Phase-1 model

The public explorer currently computes a deliberately simple diagnostic:

- stellar flux relative to Earth,
- equilibrium temperature,
- greenhouse-adjusted surface proxy,
- qualitative liquid-water window.

This is a **DERIVED heuristic**, not a GCM and not an orbital-stability result.

## Next scientific upgrade

The H-01 orbit must be tested using N-body ensembles (planned REBOUND integration) against:
- LTT 1445 A,
- the B/C pair,
- observed planets,
- uncertainty in orbital parameters.

Only after that should an orbit be labeled dynamically viable.
