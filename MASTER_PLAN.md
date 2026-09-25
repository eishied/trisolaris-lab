# TRISOLARIS LAB — Master Plan

## Mission

Build a reproducible computational research platform that connects multi-star astrophysics with planetary habitability, biospheres, human survival, population divergence, culture, technology and multiplanetary dispersal.

## Core causal chain

```
stellar system
→ orbital dynamics
→ radiation
→ atmosphere
→ regional climate
→ water / geology / oceans
→ biosphere
→ food systems
→ physiology
→ behavior
→ technology
→ demography
→ migration
→ isolation / gene flow
→ genetics
→ evolution
→ cultures / civilizations
→ multiplanetary dispersal
```

## Distinctive research functions

### Evolutionary Refugia
Detect locations or habitats that allow populations to survive otherwise catastrophic climatic or irradiation events.

### Causal Why Engine
Trace any major outcome backward through its causal chain.

### Lineage Explorer
Maintain persistent populations and lineages with ancestry, divergence, population size, habitat, traits, culture, agriculture and technology.

### Body Evolution Comparator
Compare ancestor and descendant population-level anatomy and physiology, with uncertainty.

### Planetary Human Footprint
Map settlement, agriculture, migration, infrastructure, refugia and ecological transformation through time.

### Interplanetary Founder Effect
Model the demographic and evolutionary consequences of small founding populations colonizing another world.

### Evolutionary Replay
Re-run a historical branch as an ensemble to estimate whether an observed outcome was robust or contingent.

### Observer Mode
Estimate what a distant observer might infer from the simulated atmosphere, biosphere and technological signatures.

## Scientific architecture

- **Frontend:** TypeScript/WebGL for interactive system, globe, maps and lineage visualizations.
- **API:** Python/FastAPI.
- **Orbital engine:** N-body integration, initially compatible with REBOUND.
- **Planet engine:** fast regional climate model with later benchmarking against ExoPlaSim/ROCKE-3D.
- **Evolution engine:** population genetics interface designed for future SLiM integration.
- **Agent layer:** demographic, cultural and technological agents; future Mesa compatibility.
- **Research layer:** experiments, provenance, evidence ledger and publication pipeline.

## Fidelity by timescale

| Timescale | Primary representation |
|---|---|
| seconds–days | direct physical integration |
| months–centuries | orbital/climate evolution |
| millennia | climate + ecology + demography |
| Myr | population genetics + macroevolution |
| 100 Myr+ | ensembles, aggregated processes and uncertainty |
| Gyr | stellar/planetary evolution with explicit low-confidence biological extrapolation |

## Development phases

1. Research foundation and provenance.
2. Real multi-star system import.
3. N-body and radiation engine.
4. Regional planetary grid.
5. Climate and habitability.
6. Biosphere and food systems.
7. Human physiology and demography.
8. Population genetics and persistent lineages.
9. Culture, agriculture and technology.
10. Multiplanetary migration.
11. Evolutionary Replay and ensembles.
12. Reproducible publications and research releases.

## Definition of success

TRISOLARIS LAB succeeds when a researcher can select a real or hypothetical multi-star configuration, run a reproducible experiment, inspect why the result occurred, trace every value to its source/model, and rebuild every published figure from a versioned experiment.
