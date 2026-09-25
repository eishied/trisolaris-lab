import json
import unittest

from engine.research.note_builder import build_research_note


RELEASE = {
    "release_id": "REL-1",
    "experiment_id": "EXP-1",
    "publication_state": "RESEARCH_NOTE",
    "git_commit": "abc123",
    "research_question": "Would the same modeled outcome recur?",
    "summary": {"research_note_ready": True, "evidence_item_count": 2},
    "datasets": [
        {
            "name": "evolutionary_replay",
            "path": "replay.json",
            "model": "replay_v1",
            "limitations": ["replay limitation"],
        },
        {
            "name": "counterfactual_replay",
            "path": "cf.json",
            "model": "cf_v1",
            "limitations": ["counterfactual limitation"],
        },
    ],
    "evidence_ledger": [
        {"evidence_id": "EV-1", "epistemic_level": "MODELED"},
        {"evidence_id": "EV-2", "epistemic_level": "OBSERVED"},
    ],
    "claims": [
        {
            "claim_id": "CLM-1",
            "evidence_ids": ["EV-1"],
            "qualifier": "model conditional",
        }
    ],
    "limitations": ["not peer reviewed"],
}
REPLAY = {
    "model": "replay_v1",
    "inputs": {
        "runs": 8,
        "seed": 1445,
        "uncertainty": 0.25,
        "founder_size": 500,
        "exchange_strength": 0.3,
        "resupply_strength": 0.35,
        "infrastructure_shock": 0.0,
    },
    "outcomes": {
        "counts": {
            "no-launch": 8,
            "settlement-failure": 0,
            "colony-collapse": 0,
            "connected-colony": 0,
            "divergent-lineage": 0,
        },
        "frequencies": {
            "no-launch": 1.0,
            "settlement-failure": 0.0,
            "colony-collapse": 0.0,
            "connected-colony": 0.0,
            "divergent-lineage": 0.0,
        },
    },
    "summary": {
        "runs": 8,
        "dominant_outcome": "no-launch",
        "dominant_frequency": 1.0,
    },
}
COUNTER = {
    "model": "cf_v1",
    "inputs": {
        "parameter": "capability",
        "intervention_fraction": 0.2,
        "seed": 1445,
    },
    "reference": {"frequencies": REPLAY["outcomes"]["frequencies"]},
    "intervention": {"frequencies": REPLAY["outcomes"]["frequencies"]},
    "frequency_deltas": {
        key: 0.0 for key in REPLAY["outcomes"]["frequencies"]
    },
    "summary": {
        "outcome_flip_fraction": 0.0,
        "mean_outcome_score_delta": 0.0,
        "mean_divergence_delta": 0.0,
    },
}
SYSTEM = {
    "observed_planets": [{"name": "b"}],
    "hypothetical_experiment": {"id": "H-01"},
    "literature": [{"title": "Paper", "doi": "10.1234/example"}],
}


class ResearchNoteBuilderTests(unittest.TestCase):
    def test_builds_complete_package(self):
        package = build_research_note(RELEASE, REPLAY, COUNTER, SYSTEM)
        expected = {
            "paper.md",
            "metadata.json",
            "evidence.json",
            "experiments.json",
            "references.bib",
            "REPRODUCE.md",
            "tables/outcome-frequencies.tsv",
            "tables/counterfactual-deltas.tsv",
            "figures/replay-outcomes.svg",
            "figures/counterfactual-deltas.svg",
            "summary.json",
        }
        self.assertEqual(set(package), expected)

    def test_note_never_auto_marks_arxiv_ready(self):
        package = build_research_note(RELEASE, REPLAY, COUNTER, SYSTEM)
        metadata = json.loads(package["metadata.json"])
        self.assertFalse(metadata["arxiv_ready"])
        self.assertTrue(metadata["human_review_required"])
        self.assertIn("RESEARCH_NOTE", package["paper.md"])

    def test_claims_must_resolve_to_evidence(self):
        broken = dict(RELEASE)
        broken["claims"] = [{
            "claim_id": "CLM-X",
            "evidence_ids": ["EV-MISSING"],
            "qualifier": "test",
        }]
        with self.assertRaises(ValueError):
            build_research_note(broken, REPLAY, COUNTER, SYSTEM)

    def test_non_ready_release_is_rejected(self):
        broken = dict(RELEASE)
        broken["publication_state"] = "IDEA"
        with self.assertRaises(ValueError):
            build_research_note(broken, REPLAY, COUNTER, SYSTEM)

    def test_figures_and_tables_are_deterministic_text(self):
        package = build_research_note(RELEASE, REPLAY, COUNTER, SYSTEM)
        self.assertTrue(package["figures/replay-outcomes.svg"].startswith("<svg"))
        self.assertIn(
            "no-launch\t8\t1.000000",
            package["tables/outcome-frequencies.tsv"],
        )


if __name__ == "__main__":
    unittest.main()
