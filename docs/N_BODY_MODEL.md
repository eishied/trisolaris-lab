# Phase 2.1 — Pilot N-body model

TRISOLARIS now includes a first numerical gravitational experiment using **REBOUND**.

## What is integrated

- LTT 1445 A
- confirmed planets around A from the current NASA Exoplanet Archive snapshot
- hypothetical TRISOLARIS H-01
- the combined mass of LTT 1445 B+C as a distant barycentric perturber

## Why B and C are not yet separate

The repository does not yet contain a sufficiently complete orbital solution for the internal B–C binary and the outer A–(BC) orbit. Splitting B and C without those constraints would create false precision.

Phase 2.1 therefore uses the combined B+C mass and samples uncertain orbital phase and eccentricity. This is explicitly a **MODELED** approximation.

## Ensemble

The public baseline uses a small deterministic pilot ensemble:

- 12 runs
- 100 simulated years per run
- random orbital phases from fixed reproducible seeds
- H-01 eccentricity sampled between 0 and 0.08
- outer A–(BC) eccentricity sampled between 0 and 0.45
- REBOUND IAS15 integrator

The pilot records:

- survival through the integration window
- maximum H-01 eccentricity
- minimum pericenter
- maximum apocenter
- maximum semimajor-axis drift

## Interpretation rule

The interface must say **survived the pilot interval**, not **stable**.

A 100-year integration is tiny compared with stellar-system lifetimes. It is useful as an engineering/scientific pipeline milestone and as a detector of obvious short-timescale problems, not as proof of long-term viability.

## Next upgrade

1. Ingest a stronger astrometric/orbital solution for the stellar hierarchy.
2. Resolve B and C separately.
3. Sample measurement uncertainties rather than broad exploratory priors.
4. Expand to thousands of realizations and longer time horizons.
5. Feed time-dependent irradiation and orbital extrema into the climate layer.
