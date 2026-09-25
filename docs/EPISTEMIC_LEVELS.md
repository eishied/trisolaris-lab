# Epistemic Levels

TRISOLARIS LAB separates evidence from inference.

## OBSERVED
Direct value retrieved from an official scientific archive or instrument-derived product.

Required metadata:
- authority
- source service/table
- retrieval timestamp
- source identifier
- original units
- raw snapshot

## LITERATURE
Value or assumption taken from a scientific publication.

Required metadata:
- DOI, bibcode or stable citation
- page/table/section when relevant
- interpretation notes

## MODELED
Output produced by a declared computational model.

Required metadata:
- model name/version
- parameters
- numerical method
- commit
- run identifier

## DERIVED
Quantity calculated from observed, literature or modeled inputs.

Required metadata:
- formula/algorithm
- parent variables
- units
- uncertainty propagation where available

## SPECULATIVE
Hypothesis or deep-time extrapolation not directly supported by empirical evidence.

Required metadata:
- assumptions
- mechanism
- uncertainty
- alternatives considered

## Rule

A downstream variable can never inherit a stronger epistemic status than its weakest critical premise without explicit justification.
