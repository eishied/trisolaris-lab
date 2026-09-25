# Phase 10.1 — Paired Counterfactual Replay

Phase 10.1 compares two ensembles that share the same starting scenario,
random seed and perturbation sequence. Exactly one declared parameter changes.

The question is:

> If everything else in the modeled history were held as constant as possible,
> where would the histories begin to separate?

Supported interventions:

- functional capability;
- founder cohort size;
- exchange/contact;
- resupply;
- infrastructure shock.

Because the two ensembles use the same seed, run 17 in the reference ensemble
is paired with run 17 in the intervention ensemble. The model reports outcome
flips, frequency changes, outcome-score changes and divergence changes.

This is a **model counterfactual**, not a causal estimate for the real world.
It helps diagnose the simulator's own causal structure and identify thresholds
that deserve more rigorous experiments.
