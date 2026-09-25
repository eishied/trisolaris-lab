# Phase 12.1 — Adaptive Threshold Refinement

Phase 12.0 identifies coarse grid crossings. Phase 12.1 refines those
crossings without pretending the coarse grid point is an exact threshold.

The current refinement tracks three separate transitions:

1. leaving the no-launch state;
2. reaching a persistent off-world colony;
3. reaching the divergent-lineage outcome class.

## Method

For each stage, the coarse capability curve is searched for two adjacent grid
points that bracket the target ensemble frequency.

A fixed-seed bisection then evaluates the midpoint repeatedly and narrows the
interval. The baseline uses:

- target ensemble frequency: 50%
- 32 replay runs per evaluation
- seed 1445
- uncertainty envelope 10%
- 8 refinement iterations

## Why three thresholds?

Leaving H-01, maintaining a colony and generating a persistent divergent
lineage are different causal stages. A population can therefore cross the
launch threshold and still fail later.

## Limits

The refinement assumes a locally monotonic crossing inside the coarse bracket.
The resulting interval is a model threshold, not a real engineering
requirement. Higher-fidelity models can shift, broaden or eliminate it.
