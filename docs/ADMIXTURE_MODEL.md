# Phase 6.2 — Population admixture and functional anatomy

The lineage inspector now separates two questions:

1. **What functional changes are supported by the model?**
2. **What visible anatomical changes can actually be justified?**

At the current level, TRISOLARIS supports functional differences in:

- thermoregulation,
- water conservation / renal function,
- oxygen handling,
- metabolic / dietary flexibility.

It deliberately does **not** invent craniofacial or cosmetic changes from those
traits.

## Representative portraits

The interface shows an adult male and adult female representative of the same
lineage. These portraits are visual anchors only.

Their faces do not morph unless a later developmental-genetics model provides
an explicit, biologically plausible basis for doing so.

## Population admixture

Users can compare two lineages and activate a hypothetical admixture scenario.

The first admixture model:

- combines parental allele frequencies using a user-independent 50/50 mixture,
- calculates expected heterozygosity,
- compares the mixed population with both source populations.

This models a descendant population, not a single child.

## Taxonomy

Admixture never creates a species automatically.

A future taxonomic model would require persistent reproductive isolation,
genomic divergence, developmental compatibility and demographic history.
