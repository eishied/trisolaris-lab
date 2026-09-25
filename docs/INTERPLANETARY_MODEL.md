# Phase 9.0 — Interplanetary settlement

TRISOLARIS now allows persistent populations from H-01 to evaluate and, when
their functional capabilities are sufficient, attempt settlement on the other
known worlds orbiting LTT 1445 A.

## What Phase 9 adds

The causal chain is:

```
H-01 population
  ↓
launch readiness
  ↓
destination burden
  ↓
founder cohort
  ↓
idealized transfer
  ↓
arrival survivors
  ↓
settlement persistence or failure
  ↓
contact / isolation
  ↓
gene flow + founder effect
  ↓
conditional off-world lineage branch
```

None of these transitions is guaranteed.

## Worlds and evidence

H-01 remains a **SPECULATIVE** experimental world.

LTT 1445 A b and LTT 1445 A c retain their **OBSERVED** NASA Exoplanet Archive
parameters. The model does not silently assign either world an Earth-like
atmosphere or biosphere.

Their equilibrium temperatures are used only as a broad thermal screening
variable. Equilibrium temperature is not surface temperature.

## Transfer model

The first transfer-time estimate uses the idealized coplanar circular Hohmann
half-period around LTT 1445 A:

```
t_transfer = 0.5 * sqrt(a_transfer^3 / M_star)
```

with AU, solar masses and years as the unit system.

This is a screening model. It does not yet include launch from the planetary
surface, escape/capture burns, eccentric transfer windows, finite thrust,
radiation exposure, life-support mass, propulsion engineering or N-body
optimization.

## Founder populations

Founder size is explicit. Earlier demographic `population_index` values are
not treated as literal numbers of people.

A small founder cohort increases a modeled founder-effect pressure. A large
cohort can reduce that pressure but does not guarantee persistence.

## Isolation and gene flow

Post-settlement contact depends on retained technical capacity and an explicit
exchange parameter. Strong exchange lowers isolation and increases modeled gene
flow. Weak exchange can allow divergence to accumulate.

## Off-world lineages

The simulator can label a persistent off-world branch only after:

- a launch is feasible;
- enough founders survive the transfer;
- the settlement remains viable;
- enough simulated time passes;
- isolation is substantial;
- the divergence proxy crosses a declared threshold.

An off-world lineage branch is **not a new species**. No anatomical change is
invented merely because a population lives on another planet.

## Failure is a valid result

Phase 9 can return:

- assessment only;
- launch not feasible;
- transfer bottleneck;
- settlement failure;
- persistent settlement;
- persistent off-world lineage branch.

The model therefore does not assume technological progress, successful
colonization, or inevitable biological divergence.

## Next

A later phase can replace the screening transfer model with full trajectory
optimization and N-body transfer windows, then connect extraplanetary
populations back into the genetics, anatomy, ecology and long-term historical
views.
