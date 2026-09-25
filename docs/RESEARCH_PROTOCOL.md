# Research Protocol

## Research object lifecycle

```
Question → Hypothesis → Experiment → Finding → Evidence review
→ Replication → Sensitivity analysis → Research Note → Working Paper
```

## Question
Stored under `research/questions/`.

Must define:
- question
- scientific motivation
- measurable outcome
- relevant literature
- falsifiable or discriminating criteria

## Hypothesis
Stored under `research/hypotheses/`.

Must define expected mechanism and alternatives.

## Experiment
Stored under `experiments/`.

Every experiment receives a stable ID such as `EXP-000001`.

Required:
- configuration
- datasets
- model versions
- random seeds
- expected outputs
- success/failure criteria

## Finding
A finding is an observation from one or more experiments. It is not automatically a scientific conclusion.

Required:
- supporting experiments
- effect size
- uncertainty
- sensitivity
- alternative explanations

## Publication readiness

A result must be assessed for:
- novelty
- reproducibility
- robustness
- sensitivity
- provenance
- literature comparison
- uncertainty
- model limitations

The system may recommend a research note or working paper, but scientific claims and submission require human review.
