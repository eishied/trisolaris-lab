# Scientific Model

## Goal

TRISOLARIS LAB is a coupled model framework, not a single monolithic simulator.

## Layer A — astrophysics
Inputs: stellar masses, luminosities, temperatures, positions, velocities and planetary initial conditions.

Outputs:
- positions/velocities
- orbital stability
- encounters
- ejections/collisions
- time-dependent distances
- stellar flux by source

### Phase 2 — analytic orbital pre-screen

Before long N-body integrations, TRISOLARIS applies a transparent pairwise spacing screen to H-01.

For two low-mass planets around the same host:

```
R_H,m = ((m1 + m2) / (3 M★))^(1/3) × (a1 + a2)/2
Δ = |a2 - a1| / R_H,m
```

The classic idealized two-planet Hill threshold is:

```
Δ > 2√3
```

TRISOLARIS uses this only as a **rejection / spacing screen**. It must never be described as proof of long-term stability.

The screen also reports a Keplerian period:

```
P² = a³ / (M★ + Mp)
```

in canonical AU / solar-mass / year units.

Current assumptions:
- H-01 mass defaults to 1 Earth mass,
- nearly circular and coplanar pairwise comparison,
- observed planet masses and semimajor axes from the current NASA snapshot,
- outer B+C forcing shown only as an approximate scale based on projected separation.

Not yet included:
- full N-body integration,
- stellar A–BC orbital solution,
- mean-motion resonances,
- parameter uncertainties,
- inclinations,
- eccentricity distributions,
- secular dynamics.

Therefore the allowed output language is **fails screen**, **passes screen**, or **well separated in the analytic screen** — never simply **stable**.

## Layer B — radiation
For each surface cell, the local stellar contribution is evaluated separately and then combined.

Conceptually:

```
F_local = Σ_i [ L_i / (4π r_i²) × max(0, cos θ_i) ]
```

Spectral and UV contributions must remain star-specific where data/model fidelity permits.

## Layer C — regional planet
Initial target grid: 72 × 36 = 2,592 surface cells.

Candidate cell state:
- temperature
- pressure
- precipitation
- humidity
- winds
- snow/ice
- topography
- land/ocean
- soil moisture
- freshwater
- vegetation/productivity
- population
- agriculture
- infrastructure

A planet must never be represented by one global temperature alone.

## Layer D — biosphere
Dynamic biomass and ecological constraints connect physical conditions to food availability and ecosystem stress.

## Layer E — humans
Separate:
1. immediate physiology,
2. behavior,
3. technology,
4. demography,
5. heritable population change.

Environmental change must not automatically create anatomical evolution.

## Layer F — populations and genetics
Mechanisms:
- mutation
- selection
- drift
- recombination
- gene flow
- founder effects
- bottlenecks
- isolation

Speciation is an emergent classification, not a timer.

## Layer G — culture and technology
Populations maintain independent histories of:
- settlement
- food production
- infrastructure
- knowledge
- communication
- social organization
- mobility
- technological capabilities

Technology can reduce or redirect biological selection.

## Layer H — multiplanetary dispersal
Migration to another planet introduces founder effects, altered gravity, atmosphere, radiation, ecology and isolation.

## Deep-time rule

The further the simulation projects into the future, the wider the uncertainty envelope must become. Deep-time societal or anatomical outcomes are ensembles of plausible histories, not predictions.
