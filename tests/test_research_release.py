import unittest

from engine.research.release import build_research_release_manifest

SYSTEM = {
    "system": {"architecture": "hierarchical triple"},
    "observed_planets": [{"name": "b"}],
    "hypothetical_experiment": {"epistemic_level": "SPECULATIVE", "notes": "test world"},
    "provenance": {"nasa_endpoint": "https://example.test/nasa"},
}

def model(name, seed=None):
    payload = {
        "model": name,
        "epistemic_level": "MODELED",
        "inputs": {},
        "summary": {},
        "limitations": ["declared limitation"],
    }
    if seed is not None:
        payload["inputs"]["seed"] = seed
    return payload

class ResearchReleaseTests(unittest.TestCase):
    def setUp(self):
        self.datasets = [
            ("astroanthropology", "a.json", model("astro_v1")),
            ("evolutionary_replay", "r.json", {
                **model("replay_v1", 1445),
                "summary": {"dominant_outcome": "no-launch", "dominant_frequency": 1.0},
            }),
            ("counterfactual_replay", "c.json", {
                **model("counter_v1", 1445),
                "summary": {"outcome_flip_fraction": 0.0},
            }),
        ]

    def test_ready_release_requires_all_checks(self):
        result = build_research_release_manifest(
            SYSTEM, self.datasets, commit_sha="abc123"
        )
        self.assertEqual(result["publication_state"], "RESEARCH_NOTE")
        self.assertTrue(result["summary"]["research_note_ready"])

    def test_never_auto_promotes_to_arxiv_ready(self):
        result = build_research_release_manifest(
            SYSTEM, self.datasets, commit_sha="abc123"
        )
        self.assertNotEqual(result["publication_state"], "ARXIV_READY")
        self.assertIn("human review", " ".join(result["limitations"]).lower())

    def test_missing_seed_blocks_research_note_gate(self):
        datasets = list(self.datasets)
        datasets[1] = ("evolutionary_replay", "r.json", model("replay_v1"))
        result = build_research_release_manifest(
            SYSTEM, datasets, commit_sha="abc123"
        )
        self.assertEqual(result["publication_state"], "IDEA")
        self.assertFalse(result["summary"]["research_note_ready"])

    def test_evidence_levels_include_observed_and_speculative(self):
        result = build_research_release_manifest(
            SYSTEM, self.datasets, commit_sha="abc123"
        )
        levels = {row["epistemic_level"] for row in result["evidence_ledger"]}
        self.assertIn("OBSERVED", levels)
        self.assertIn("SPECULATIVE", levels)

if __name__ == "__main__":
    unittest.main()
