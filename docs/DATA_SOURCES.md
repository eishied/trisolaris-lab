# Official Data Sources

## Tier 1 — primary authoritative sources

### NASA Exoplanet Archive
Use: confirmed planets, planetary systems, stellar hosts and orbital parameters.

Preferred interface: TAP/ADQL.

Primary TAP service:
`https://exoplanetarchive.ipac.caltech.edu/TAP`

Initial tables:
- `ps` — Planetary Systems
- `pscomppars` — Planetary Systems Composite Parameters
- `toi` — TESS Project Candidates

Archive citation/DOI requirements must be preserved in dataset manifests.

### ESA Gaia Archive
Use: astrometry, parallaxes, proper motions, photometry, radial velocities, stellar parameters, multiplicity and cross-matching.

Access: Gaia Archive / TAP+.

### MAST / TESS
Use: light curves, full-frame products, target pixel products, sector metadata and time-domain stellar variability.

Access: MAST APIs and official TESS products.

### NASA GISS / ROCKE-3D
Use: planetary climate benchmarking, validation cases and comparison datasets.

TRISOLARIS fast climate models must not be presented as ROCKE-3D unless ROCKE-3D was actually run.

### NASA ADS
Use: literature search, bibliography construction, DOI/bibcode resolution and state-of-the-art tracking.

## Tier 2 — scientific model sources

Candidate engines and validation tools:
- REBOUND
- VPLanet
- ExoPlaSim
- ROCKE-3D
- SLiM
- Mesa

Each integration must document:
- software version
- license
- citation requirements
- model limitations
- exact inputs/outputs used

## Source hierarchy

When multiple values disagree, TRISOLARIS must retain all source records and explicitly select a working value rather than silently overwrite history.
