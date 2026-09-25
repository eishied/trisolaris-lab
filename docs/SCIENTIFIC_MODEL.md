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
