#!/usr/bin/env python3
"""Reproducible research-note builder for TRISOLARIS LAB Phase 11.1."""

from __future__ import annotations

import json
from typing import Any

OUTCOMES = (
    "no-launch",
    "settlement-failure",
    "colony-collapse",
    "connected-colony",
    "divergent-lineage",
)

LABELS = {
    "no-launch": "No launch",
    "settlement-failure": "Settlement failure",
    "colony-collapse": "Colony collapse",
    "connected-colony": "Connected colony",
    "divergent-lineage": "Divergent lineage",
}


def _pct(value: float) -> str:
    return f"{100.0 * float(value):.1f}%"


def _validate_release(release: dict[str, Any]) -> None:
    if release.get("publication_state") != "RESEARCH_NOTE":
        raise ValueError("research note builder requires a RESEARCH_NOTE release")
    if not release.get("summary", {}).get("research_note_ready"):
        raise ValueError("research release has not passed its reproducibility gate")

    evidence_ids = {
        row.get("evidence_id")
        for row in release.get("evidence_ledger", [])
        if row.get("evidence_id")
    }
    for claim in release.get("claims", []):
        missing = [
            item for item in claim.get("evidence_ids", [])
            if item not in evidence_ids
        ]
        if missing:
            raise ValueError(
                f"claim {claim.get('claim_id')} references missing evidence: {missing}"
            )


def _svg_bars(title: str, rows: list[tuple[str, float]], signed: bool = False) -> str:
    width = 960
    top = 82
    row_h = 52
    height = top + 46 + row_h * len(rows)
    plot_x = 285
    plot_w = 610
    axis_x = plot_x + plot_w / 2 if signed else plot_x
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#080d12"/>',
        f'<text x="28" y="40" fill="#e4ecef" font-family="system-ui,sans-serif" font-size="23" font-weight="700">{title}</text>',
        '<text x="28" y="62" fill="#7f8d96" font-family="system-ui,sans-serif" font-size="12">Generated from committed TRISOLARIS baseline data</text>',
    ]
    if signed:
        parts.append(
            f'<line x1="{axis_x:.1f}" y1="{top-18}" x2="{axis_x:.1f}" y2="{height-34}" stroke="#46545d"/>'
        )
    for index, (label, raw) in enumerate(rows):
        y = top + index * row_h
        parts.append(
            f'<text x="28" y="{y+19}" fill="#a8b4bb" font-family="system-ui,sans-serif" font-size="13">{label}</text>'
        )
        if signed:
            value = max(-1.0, min(1.0, float(raw)))
            bar_w = abs(value) * plot_w / 2
            x = axis_x if value >= 0 else axis_x - bar_w
            text = f"{value*100:+.1f} pp"
        else:
            value = max(0.0, min(1.0, float(raw)))
            parts.append(
                f'<rect x="{plot_x}" y="{y+5}" width="{plot_w}" height="18" rx="3" fill="#142028"/>'
            )
            bar_w = value * plot_w
            x = plot_x
            text = _pct(value)
        parts.append(
            f'<rect x="{x:.1f}" y="{y+5}" width="{bar_w:.1f}" height="18" rx="3" fill="#77bfd9" opacity="0.82"/>'
        )
        parts.append(
            f'<text x="925" y="{y+19}" text-anchor="end" fill="#dce4e8" font-family="system-ui,sans-serif" font-size="13">{text}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts)


def _bibliography(system_data: dict[str, Any]) -> str:
    entries = [
        "@misc{nasa_exoplanet_archive,\n"
        "  title = {NASA Exoplanet Archive},\n"
        "  howpublished = {TAP service},\n"
        "  url = {https://exoplanetarchive.ipac.caltech.edu/TAP/sync},\n"
        "  note = {Observed planet rows used by the TRISOLARIS data pipeline}\n"
        "}"
    ]
    for index, item in enumerate(system_data.get("literature", []), start=1):
        fields = [f"  title = {{{item.get('title', 'Untitled literature source')}}}"]
        if item.get("doi"):
            fields.append(f"  doi = {{{item['doi']}}}")
        if item.get("arxiv"):
            fields.append(f"  eprint = {{{item['arxiv']}}}")
            fields.append("  archivePrefix = {arXiv}")
        entries.append(
            "@misc{trisolaris_literature_%02d,\n%s\n}"
            % (index, ",\n".join(fields))
        )
    return "\n\n".join(entries) + "\n"


def build_research_note(
    release: dict[str, Any],
    replay: dict[str, Any],
    counterfactual: dict[str, Any],
    system_data: dict[str, Any],
    *,
    note_id: str = "RN-TRISOLARIS-0001",
) -> dict[str, str]:
    _validate_release(release)

    replay_inputs = replay.get("inputs", {})
    replay_summary = replay.get("summary", {})
    replay_outcomes = replay.get("outcomes", {})
    frequencies = replay_outcomes.get("frequencies", {})
    counts = replay_outcomes.get("counts", {})

    counter_inputs = counterfactual.get("inputs", {})
    counter_summary = counterfactual.get("summary", {})
    deltas = counterfactual.get("frequency_deltas", {})
    reference = counterfactual.get("reference", {}).get("frequencies", {})
    intervention = counterfactual.get("intervention", {}).get("frequencies", {})

    runs = int(replay_inputs.get("runs", replay_summary.get("runs", 0)))
    dominant = replay_summary.get("dominant_outcome", "unknown")
    dominant_frequency = float(replay_summary.get("dominant_frequency", 0.0))
    flip_fraction = float(counter_summary.get("outcome_flip_fraction", 0.0))
    parameter = counter_inputs.get("parameter", "unknown")
    intervention_fraction = float(counter_inputs.get("intervention_fraction", 0.0))

    outcome_table = "outcome\tcount\tfrequency\n"
    delta_table = "outcome\treference_frequency\tintervention_frequency\tdelta\n"
    outcome_rows = []
    delta_rows = []
    for code in OUTCOMES:
        freq = float(frequencies.get(code, 0.0))
        delta = float(deltas.get(code, 0.0))
        outcome_rows.append((LABELS[code], freq))
        delta_rows.append((LABELS[code], delta))
        outcome_table += f"{code}\t{int(counts.get(code, 0))}\t{freq:.6f}\n"
        delta_table += (
            f"{code}\t{float(reference.get(code, 0.0)):.6f}\t"
            f"{float(intervention.get(code, 0.0)):.6f}\t{delta:.6f}\n"
        )

    model_lines = "\n".join(
        f"- {row.get('model')} — {row.get('path')}"
        for row in release.get("datasets", [])
    )
    claim_lines = "\n".join(
        f"- {claim.get('claim_id')} -> {', '.join(claim.get('evidence_ids', []))}: {claim.get('qualifier')}"
        for claim in release.get("claims", [])
    )
    limitation_lines = "\n".join(
        f"- {item}" for item in release.get("limitations", [])
    )
    upstream_lines = "\n".join(
        f"- {row.get('name')}: {(row.get('limitations') or ['No limitation text'])[0]}"
        for row in release.get("datasets", [])
    )

    title = "Robustness of a modeled multiplanetary transition in the TRISOLARIS LTT 1445 scenario"
    abstract = (
        f"We evaluated whether the baseline TRISOLARIS multiplanetary trajectory is robust "
        f"to declared scenario uncertainty. A seeded Evolutionary Replay ensemble of {runs} "
        f"runs was propagated through settlement, colony-network and off-world divergence "
        f"layers. The dominant modeled outcome was {dominant} in {_pct(dominant_frequency)} "
        f"of runs. A paired same-seed counterfactual changing {parameter} by "
        f"{intervention_fraction:+.0%} changed outcome class in {_pct(flip_fraction)} of "
        f"paired histories. These frequencies are conditional on the declared model and "
        f"perturbation envelope and are not real-world probabilities."
    )

    paper = f"""---
paper_id: {note_id}
release_id: {release.get('release_id')}
experiment_id: {release.get('experiment_id')}
title: "{title}"
status: RESEARCH_NOTE
git_commit: {release.get('git_commit')}
replay_seed: {replay_inputs.get('seed')}
counterfactual_seed: {counter_inputs.get('seed')}
arxiv_ready: false
---

# {title}

## Abstract

{abstract}

## Research question

{release.get('research_question')}

## Hypothesis

The baseline outcome is treated as robust within the declared model envelope when one outcome class dominates the replay ensemble and modest paired interventions do not frequently change run-level outcome classes.

This is a hypothesis about simulator behavior, not about the real LTT 1445 system or real human futures.

## Background

TRISOLARIS combines observed system data, literature parameters and an explicitly speculative world, H-01, in a causal modeling chain. Observed planets are imported from the NASA Exoplanet Archive. H-01 remains a scenario object and is never promoted to an observed planet.

## Data and epistemic scope

- Observed planet rows: {len(system_data.get('observed_planets', []))}
- Experimental world: {system_data.get('hypothetical_experiment', {}).get('id', 'H-01')} — SPECULATIVE
- Release: {release.get('release_id')}
- Git commit: {release.get('git_commit')}
- Evidence items: {release.get('summary', {}).get('evidence_item_count', 0)}

## Methods

### Model stack

{model_lines}

### Evolutionary Replay

The baseline replay used {runs} runs, random seed {replay_inputs.get('seed')}, an uncertainty envelope of {_pct(replay_inputs.get('uncertainty', 0.0))}, founder size {replay_inputs.get('founder_size')}, exchange strength {replay_inputs.get('exchange_strength')}, resupply strength {replay_inputs.get('resupply_strength')} and infrastructure shock {replay_inputs.get('infrastructure_shock')}.

### Paired counterfactual

The counterfactual uses the same random seed and pairs each reference run with the corresponding intervention run. The baseline intervention changes {parameter} by {intervention_fraction:+.0%}.

## Results

### Replay ensemble

The dominant modeled outcome was **{LABELS.get(dominant, dominant)}**, occurring in **{_pct(dominant_frequency)}** of {runs} replay runs.

![Replay outcome frequencies](figures/replay-outcomes.svg)

Exact values are in tables/outcome-frequencies.tsv.

### Counterfactual intervention

The paired intervention changed outcome class in **{_pct(flip_fraction)}** of runs. Mean outcome-score delta was {float(counter_summary.get('mean_outcome_score_delta', 0.0)):+.3f}; mean divergence-proxy delta was {float(counter_summary.get('mean_divergence_delta', 0.0)):+.6f}.

![Counterfactual frequency deltas](figures/counterfactual-deltas.svg)

Exact values are in tables/counterfactual-deltas.tsv.

## Sensitivity and interpretation

A dominant replay frequency indicates robustness only within this model and perturbation envelope. A small counterfactual response does not establish real-world insensitivity; it shows that the current simulator did not cross its modeled thresholds under the declared intervention.

## Claim-to-evidence map

{claim_lines}

## Limitations

{limitation_lines}

Selected upstream limitations:

{upstream_lines}

## Discussion

The baseline result remains useful when negative. If all or nearly all runs remain in the same pre-expansion state, the current model is indicating that the baseline population is not merely fluctuating around a multiplanetary threshold. This motivates threshold-search experiments rather than a stronger real-world claim.

## Conclusions

The current baseline is reproducible and internally traceable. Its ensemble and counterfactual results support a narrow claim about the current TRISOLARIS model only. They do not establish real-world probability, feasibility or inevitability.

## Reproducibility

- Release: {release.get('release_id')}
- Experiment: {release.get('experiment_id')}
- Git commit: {release.get('git_commit')}
- Evolutionary Replay seed: {replay_inputs.get('seed')}
- Counterfactual seed: {counter_inputs.get('seed')}
- Exact tables: tables/
- Generated figures: figures/
- Evidence ledger: evidence.json
- Experiment parameters: experiments.json

See REPRODUCE.md.

## Data availability

All data used by this note are versioned in the TRISOLARIS repository and enumerated in metadata.json and experiments.json.

## Code availability

The analysis code is versioned at commit {release.get('git_commit')}.

## Publication status

RESEARCH_NOTE. This package is not peer reviewed and is not automatically ARXIV_READY, SUBMITTED or PUBLISHED.

## References

See references.bib.
"""

    metadata = {
        "paper_id": note_id,
        "release_id": release.get("release_id"),
        "experiment_id": release.get("experiment_id"),
        "title": title,
        "status": "RESEARCH_NOTE",
        "git_commit": release.get("git_commit"),
        "arxiv_ready": False,
        "human_review_required": True,
        "models": {
            row.get("name"): row.get("model")
            for row in release.get("datasets", [])
        },
        "dataset_paths": [
            row.get("path") for row in release.get("datasets", [])
        ],
        "replay_seed": replay_inputs.get("seed"),
        "counterfactual_seed": counter_inputs.get("seed"),
    }

    experiments = {
        "release_id": release.get("release_id"),
        "experiment_id": release.get("experiment_id"),
        "replay": {
            "model": replay.get("model"),
            "inputs": replay_inputs,
            "summary": replay_summary,
        },
        "counterfactual": {
            "model": counterfactual.get("model"),
            "inputs": counter_inputs,
            "summary": counter_summary,
        },
    }

    summary = {
        "paper_id": note_id,
        "title": title,
        "status": "RESEARCH_NOTE",
        "git_commit": release.get("git_commit"),
        "release_id": release.get("release_id"),
        "experiment_id": release.get("experiment_id"),
        "dominant_outcome": dominant,
        "dominant_frequency": dominant_frequency,
        "replay_runs": runs,
        "counterfactual_parameter": parameter,
        "counterfactual_intervention_fraction": intervention_fraction,
        "counterfactual_outcome_flip_fraction": flip_fraction,
        "claim_count": len(release.get("claims", [])),
        "evidence_item_count": len(release.get("evidence_ledger", [])),
        "arxiv_ready": False,
        "human_review_required": True,
    }

    reproduce = (
        f"# Reproduce {note_id}\n\n"
        f"1. Checkout Git commit {release.get('git_commit')}.\n"
        "2. Install requirements-science.txt.\n"
        "3. Run python pipelines/evolution/build_evolutionary_replay_baseline.py.\n"
        "4. Run python pipelines/evolution/build_counterfactual_replay_baseline.py.\n"
        "5. Run python pipelines/research/build_research_release_baseline.py.\n"
        "6. Run python pipelines/research/build_research_note.py.\n"
        "7. Compare the generated tables and SVG figures with this package.\n\n"
        f"Replay seed: {replay_inputs.get('seed')}. Counterfactual seed: {counter_inputs.get('seed')}.\n\n"
        "External submission still requires human scientific review.\n"
    )

    return {
        "paper.md": paper,
        "metadata.json": json.dumps(metadata, indent=2) + "\n",
        "evidence.json": json.dumps(release.get("evidence_ledger", []), indent=2) + "\n",
        "experiments.json": json.dumps(experiments, indent=2) + "\n",
        "references.bib": _bibliography(system_data),
        "REPRODUCE.md": reproduce,
        "tables/outcome-frequencies.tsv": outcome_table,
        "tables/counterfactual-deltas.tsv": delta_table,
        "figures/replay-outcomes.svg": _svg_bars(
            "Evolutionary Replay outcome frequencies", outcome_rows
        ),
        "figures/counterfactual-deltas.svg": _svg_bars(
            "Paired counterfactual outcome-frequency deltas", delta_rows, True
        ),
        "summary.json": json.dumps(summary, indent=2) + "\n",
    }
