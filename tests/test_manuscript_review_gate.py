import unittest

from engine.research.review_gate import evaluate_manuscript_review_gate


METADATA = {
    "status": "RESEARCH_NOTE",
    "arxiv_ready": False,
    "human_review_required": True,
}
EVIDENCE = [{"evidence_id": "EV-1"}]
EXPERIMENTS = {"release_id": "REL-1", "experiment_id": "EXP-1"}
REFERENCES = """@misc{source,
  title = {Example},
  url = {https://example.test}
}
"""
ARTIFACTS = {
    "figures/replay-outcomes.svg": "<svg></svg>",
    "figures/counterfactual-deltas.svg": "<svg></svg>",
    "tables/outcome-frequencies.tsv": "a\tb\n",
    "tables/counterfactual-deltas.tsv": "a\tb\n",
}


class ManuscriptReviewGateTests(unittest.TestCase):
    def test_machine_checks_can_pass_while_human_checks_remain_open(self):
        result = evaluate_manuscript_review_gate(
            METADATA,
            EVIDENCE,
            EXPERIMENTS,
            REFERENCES,
            ARTIFACTS,
            {},
        )
        self.assertEqual(
            result["summary"]["automatic_checks_passed"],
            result["summary"]["automatic_checks_total"],
        )
        self.assertEqual(result["summary"]["human_checks_passed"], 0)
        self.assertFalse(
            result["summary"]["promotion_eligible_for_working_paper"]
        )
        self.assertFalse(result["summary"]["status_changed_automatically"])

    def test_complete_human_review_only_makes_promotion_eligible(self):
        review = {
            "reviewer": "Human Reviewer",
            "claim_review_completed": True,
            "references_review_completed": True,
            "figures_review_completed": True,
            "independent_replication_completed": True,
            "review_notes": "Reviewed.",
        }
        result = evaluate_manuscript_review_gate(
            METADATA,
            EVIDENCE,
            EXPERIMENTS,
            REFERENCES,
            ARTIFACTS,
            review,
        )
        self.assertTrue(
            result["summary"]["promotion_eligible_for_working_paper"]
        )
        self.assertEqual(result["publication_state"], "RESEARCH_NOTE")
        self.assertFalse(result["summary"]["status_changed_automatically"])

    def test_missing_artifact_blocks_promotion(self):
        broken = dict(ARTIFACTS)
        broken.pop("figures/replay-outcomes.svg")
        review = {
            "reviewer": "Human Reviewer",
            "claim_review_completed": True,
            "references_review_completed": True,
            "figures_review_completed": True,
            "independent_replication_completed": True,
        }
        result = evaluate_manuscript_review_gate(
            METADATA,
            EVIDENCE,
            EXPERIMENTS,
            REFERENCES,
            broken,
            review,
        )
        self.assertFalse(
            result["summary"]["promotion_eligible_for_working_paper"]
        )

    def test_checksums_are_stable(self):
        first = evaluate_manuscript_review_gate(
            METADATA, EVIDENCE, EXPERIMENTS, REFERENCES, ARTIFACTS, {}
        )
        second = evaluate_manuscript_review_gate(
            METADATA, EVIDENCE, EXPERIMENTS, REFERENCES, ARTIFACTS, {}
        )
        self.assertEqual(
            first["artifact_checksums_sha256"],
            second["artifact_checksums_sha256"],
        )


if __name__ == "__main__":
    unittest.main()
