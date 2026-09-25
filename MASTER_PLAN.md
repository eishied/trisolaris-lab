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



## Cross-cutting Scientific Learning layer

TRISOLARIS LAB includes a scientific-learning layer that accumulates evidence and experimental results without replacing the declared physical, ecological, demographic or evolutionary models with an opaque black box.

The layer is designed around four distinct functions.

### Evidence Translator

Read structured and unstructured scientific material — catalogs, tables, datasets, papers and model outputs — and convert candidate facts into the internal TRISOLARIS schema.

Every extracted fact must preserve:
- source authority,
- stable citation or catalog identifier,
- original value and units,
- uncertainty when available,
- retrieval or publication context,
- epistemic level,
- extraction confidence,
- domain of applicability,
- transferability to the target TRISOLARIS subsystem.

Language models, scientific encoders and embedding models may assist extraction and retrieval, but they must not write unverified values directly into canonical scientific datasets.

### Scientific Memory

Maintain a versioned evidence store of reusable scientific knowledge.

A scientific-memory object should record, at minimum:

```text
KnowledgeObject
├── claim / variable
├── value or probability distribution
├── units
├── uncertainty
├── source authority
├── DOI / bibcode / catalog ID
├── source-system type
├── physical conditions / applicability domain
├── epistemic level
├── transferability score
├── model or extraction version
└── validation status
```

Experimental memory must preserve:

```text
Experiment
├── configuration
├── dataset versions
├── model versions
├── random seeds
├── outputs
├── uncertainty
├── residuals / validation error
└── scientific-memory contributions
```

### Calibration Engine

Compare model outputs against observations, literature constraints, benchmark simulations and higher-fidelity models.

Permitted methods include:
- Bayesian calibration,
- parameter optimization,
- Gaussian processes,
- residual learning,
- neural networks,
- physics-informed machine learning,
- other uncertainty-aware statistical methods.

Machine learning should preferentially learn corrections or uncertain relationships around an explicit scientific model rather than silently replace the model.

Conceptually:

```
prediction_final = prediction_declared_model + learned_residual
```

when that decomposition is scientifically appropriate.

A learned correction must never receive a stronger epistemic status than the evidence and assumptions used to train it.

### Surrogate and Experiment Learner

Expensive simulations may train fast surrogate models that approximate well-defined regions of parameter space.

Surrogates may be used to:
- explore very large parameter spaces,
- rank candidate scenarios,
- estimate sensitivity,
- identify anomalous regions,
- select the next most informative experiments,
- reduce the number of expensive high-fidelity simulations.

When uncertainty is high or a query lies outside the surrogate training domain, TRISOLARIS must fall back to the underlying scientific simulation rather than present the surrogate result as authoritative.

Active learning may propose the next experiments to run, but experiment selection, model promotion and scientific interpretation remain auditable.

## Evidence transfer across planetary systems

TRISOLARIS may learn from systems that are not triple-star systems when the evidence is relevant to a specific subsystem.

Examples include:
- mass-radius-density relationships,
- atmospheric retention,
- stellar irradiation response,
- orbital architecture,
- climate-model benchmarks,
- atmospheric chemistry,
- planetary composition,
- ecological or physiological constraints where scientifically justified.

Transfer is performed by **subsystem and applicability domain**, not by superficial similarity of the complete planetary system.

Every transferred constraint should carry a `transferability_score` or equivalent metadata describing how directly it applies to the target model.

For example, a single-star exoplanet population may strongly constrain a mass-radius relation while providing weak evidence for chaotic three-star orbital dynamics.

Large datasets do not automatically imply high relevance.

## Learning and recalibration governance

TRISOLARIS must never silently modify a production scientific model because new data arrived.

The lifecycle for a recalibration is:

```
new evidence
→ candidate calibration dataset
→ candidate model version
→ benchmark suite
→ comparison with current model
→ sensitivity / uncertainty review
→ human scientific review
→ promoted model version
```

Every candidate must preserve:
- training/calibration dataset snapshot IDs,
- source provenance,
- code commit,
- model architecture and hyperparameters when applicable,
- random seeds,
- benchmark results,
- uncertainty,
- known failure domains,
- comparison against the previous model.

A recalibration that improves one benchmark but degrades another must remain visible rather than being averaged away.

Production engines are immutable by version. Experiments and publications must record the exact engine and learned-model versions used.

External model or dataset hubs such as Hugging Face may be used for model discovery, hosting, versioning or inference, but every external dependency must have a pinned revision, documented license, provenance, model card or equivalent documentation, and an explicit role in the scientific pipeline.

## Scientific-learning causal loop

The learning layer forms an auditable feedback loop:

```
scientific sources
        ↓
Evidence Translator
        ↓
Scientific Memory
        ↓
Calibration / ML
        ↓
candidate models
        ↓
validation suite
        ↓
TRISOLARIS scientific engines
        ↓
reproducible experiments
        └──────────────→ Scientific Memory
```

The loop may improve calibration, experiment prioritization and computational efficiency. It must not erase the distinction between observation, literature, model, derivation and speculation.


## Scientific architecture

- **Frontend:** TypeScript/WebGL for interactive system, globe, maps and lineage visualizations.
- **API:** Python/FastAPI.
- **Orbital engine:** N-body integration, initially compatible with REBOUND.
- **Planet engine:** fast regional climate model with later benchmarking against ExoPlaSim/ROCKE-3D.
- **Evolution engine:** population genetics interface designed for future SLiM integration.
- **Agent layer:** demographic, cultural and technological agents; future Mesa compatibility.
- **Research layer:** experiments, provenance, evidence ledger and publication pipeline.

- **Scientific learning layer:** evidence translation, scientific memory, calibration, surrogate modeling, active learning and uncertainty-aware model comparison.
- **ML infrastructure:** task-appropriate statistical/ML models; external hubs such as Hugging Face are optional infrastructure, never the source of scientific authority.

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



### Cross-cutting workstream — Scientific Learning

Scientific Learning begins during the research-foundation phases and matures alongside every domain engine rather than waiting for a single late project phase.

Milestones:
1. evidence schema and Scientific Memory,
2. literature/catalog extraction with validation gates,
3. transferability metadata and applicability-domain checks,
4. calibration benchmarks for existing engines,
5. surrogate models for expensive simulations,
6. active-learning experiment selection,
7. candidate-model registry and promotion workflow,
8. publication-grade provenance for learned models.


## Definition of success

TRISOLARIS LAB succeeds when a researcher can select a real or hypothetical multi-star configuration, run a reproducible experiment, inspect why the result occurred, trace every value to its source/model, and rebuild every published figure from a versioned experiment. The platform should also be able to accumulate validated evidence and experimental results, propose better-calibrated candidate models and more informative experiments, and accelerate expensive simulations through uncertainty-aware surrogates without silently changing production science or obscuring provenance.
