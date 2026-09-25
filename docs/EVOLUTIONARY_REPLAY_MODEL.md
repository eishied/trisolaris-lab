# Phase 10.0 — Evolutionary Replay

TRISOLARIS can now replay a multiplanetary history as a reproducible ensemble
instead of presenting a single trajectory as inevitable.

## Purpose

Evolutionary Replay asks:

> If the starting scenario were almost the same, would the same history happen?

Each replay perturbs declared scenario parameters and reruns the existing
causal stack:

```
population capabilities
→ interplanetary attempt
→ founder bottleneck
→ colony network
→ infrastructure / resupply
→ off-world divergence
→ outcome classification
```

## Reproducibility

Every ensemble has an explicit integer random seed. Re-running with the same
inputs, perturbation envelope and seed produces the same run records.

## Perturbed parameters

The first implementation perturbs:

- founder cohort size;
- functional capability factor;
- exchange/contact strength;
- resupply strength;
- infrastructure shock.

The ranges are scenario assumptions. They are not empirically calibrated
uncertainty distributions.

## Outcome classes

A run can end as:

- `no-launch`;
- `settlement-failure`;
- `colony-collapse`;
- `connected-colony`;
- `divergent-lineage`.

These categories preserve failure as a valid outcome.

## Frequencies are not real-world probabilities

The ensemble reports the share of runs in each outcome class **under the
declared model and perturbation envelope**.

A 70% ensemble frequency does not mean a 70% real-world probability.

## Sensitivity

Phase 10 reports simple Pearson correlations between perturbed parameters and:

- ordered outcome persistence;
- mean modeled divergence.

This is a screening sensitivity diagnostic. It does not establish causality by
itself and should later be replaced or complemented by structured global
sensitivity methods such as Sobol analysis.

## Next

Phase 10.1 can add explicit branch comparison and counterfactual intervention:
hold every parameter fixed except one, change that one variable, and show where
the causal histories separate.
