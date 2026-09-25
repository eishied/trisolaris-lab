# TRISOLARIS LAB

**Computational Astrobiology & Astroanthropology Simulator**

TRISOLARIS LAB is an open research platform for studying how a biosphere and intelligent populations could survive, adapt, diverge, build culture and technology, and disperse between worlds inside a multi-star system.

The project connects:

**observations → orbital dynamics → stellar radiation → regional climate → biosphere → human physiology → demography → migration → genetics → evolution → culture → technology → multiplanetary settlement**

## Scientific question

> What happens to an intelligent population that attempts to maintain biological, cultural, and technological continuity in a dynamically changing multi-star environment?

TRISOLARIS is designed to answer this through reproducible computational experiments rather than a predetermined evolutionary story.

## Epistemic levels

Every important value must be labeled as one of:

- **OBSERVED** — directly retrieved from an official scientific source.
- **LITERATURE** — adopted from a scientific publication.
- **MODELED** — produced by a declared model.
- **DERIVED** — calculated from observed/literature/model outputs.
- **SPECULATIVE** — hypothesis beyond current empirical support.

See [docs/EPISTEMIC_LEVELS.md](docs/EPISTEMIC_LEVELS.md).

## Research principles

1. Every result must know where it came from.
2. Every figure must know which experiment produced it.
3. Every experiment must know which data and model versions generated it.
4. Observed data must never be silently mixed with hypothetical values.
5. Deep-time biological and cultural outcomes are probabilistic, not predetermined.
6. A result is not considered publication-ready until it is reproducible from the repository.

## Official data sources

Initial Tier-1 sources:

- NASA Exoplanet Archive — planetary and host-star parameters.
- ESA Gaia Archive — astrometry, photometry, stellar parameters and multiplicity.
- MAST / TESS — light curves, time-series products and stellar variability.
- NASA GISS / ROCKE-3D outputs — climate benchmarking and validation.
- NASA ADS — literature discovery and bibliographic evidence.

See [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md).

## Research and publications

The repository includes a research pipeline:

```
question
  ↓
hypothesis
  ↓
experiment
  ↓
finding
  ↓
replication / sensitivity analysis
  ↓
research note
  ↓
working paper
  ↓
human scientific review
  ↓
arXiv-ready package
```

Publication sources are maintained in Markdown and converted to LaTeX/PDF/arXiv-ready packages only when the evidence threshold is met.

See [docs/PUBLICATION_PIPELINE.md](docs/PUBLICATION_PIPELINE.md) and [publications/README.md](publications/README.md).

## Repository map

```
frontend/        visualization and interactive interface
engine/          scientific simulation modules
data/            raw, processed, derived and snapshot data
pipelines/       official-source data ingestion
experiments/     reproducible simulation runs
research/        questions, hypotheses, evidence and findings
publications/    research notes, working papers and arXiv templates
provenance/      dataset/model/experiment traceability
docs/            scientific and technical documentation
.github/         validation and data-ingestion workflows
```

## Current phase

**Phase 0 — Research foundation**

The immediate goals are to establish data provenance, scientific conventions, research workflow, official-source ingestion, and the reproducibility contract before implementing the full simulator.

See [MASTER_PLAN.md](MASTER_PLAN.md) and [docs/ROADMAP.md](docs/ROADMAP.md).

## License

The repository currently uses the MIT License for original TRISOLARIS LAB code. Integrated third-party scientific engines, datasets and publications retain their own licenses and citation requirements. Data and publication licensing will be documented separately as integrations are added.
