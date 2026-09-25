# Publication Pipeline

## Source-of-truth format

Research manuscripts are authored in Markdown.

```
paper.md
→ validated citations
→ figures/tables from experiment IDs
→ LaTeX
→ PDF
→ arXiv source package
```

## Publication states

- IDEA
- RESEARCH_NOTE
- WORKING_PAPER
- ARXIV_CANDIDATE
- ARXIV_READY
- SUBMITTED
- PUBLISHED

## ARXIV_READY requirements

A manuscript cannot reach `ARXIV_READY` unless:
- all scientific claims link to evidence,
- datasets are versioned,
- experiments are reproducible,
- figures trace to experiment IDs,
- uncertainty is reported,
- limitations are explicit,
- references resolve,
- LaTeX builds successfully,
- the source archive contains all required files.

## Human gate

TRISOLARIS may build and validate an arXiv-ready source package, but submission is a deliberate author action.

## Manuscript package

```
publications/<paper-id>/
  paper.md
  metadata.yml
  references.bib
  evidence.yml
  experiments.yml
  figures/
  tables/
  arxiv/
    main.tex
    references.bib
    figures/
    main.pdf
    submission.tar.gz
```

## Reproducibility statement

Every paper should expose:
- Git commit
- model versions
- dataset snapshot IDs
- experiment IDs
- random seeds when applicable
- code/data availability
