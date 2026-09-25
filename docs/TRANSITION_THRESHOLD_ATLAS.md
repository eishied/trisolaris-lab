# Phase 12.0 — Transition Threshold Atlas

The current baseline Evolutionary Replay is dominated by no-launch outcomes.
Phase 12 asks a more diagnostic question:

> Which modeled controls can actually move the system out of the launch
> bottleneck, and where do those transitions begin within the scanned range?

## One-dimensional scans

The first atlas varies one control family at a time while keeping a common
Evolutionary Replay seed and perturbation envelope:

- functional capability multiplier
- founder cohort size
- post-settlement exchange
- resupply strength
- infrastructure shock

For each grid point the model records:

- non-no-launch ensemble frequency
- persistent-colony frequency
- divergent-lineage frequency
- dominant outcome and its frequency

## Threshold definition

A threshold is reported when the non-no-launch frequency reaches the declared
target frequency, initially 50%.

The reported value is the first scanned grid point crossing the target. It is
a bracket value, not an exact mathematical threshold.

## Stage-specific interpretation

Some controls act only after launch or arrival. Founder cohort, exchange,
resupply and infrastructure shock therefore cannot necessarily solve a
pre-launch capability bottleneck.

A parameter that fails to reach the target is not declared irrelevant in
general. It means only that it did not resolve the current bottleneck inside
the scanned range and current model.

## Epistemic limit

Thresholds are properties of the current reduced-order simulator. They are not
real engineering requirements, probabilities or prescriptions.

## Next

Phase 12.1 can refine detected crossings with adaptive local searches and then
run paired counterfactual ensembles immediately below and above each bracket.
