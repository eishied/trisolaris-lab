import unittest

from engine.evolution.replay import run_evolutionary_replay


SYSTEM = {
    "stars": [{"id": "A", "mass_solar": 0.257}],
    "hypothetical_experiment": {
        "id": "H-01",
        "name": "TRISOLARIS H-01",
        "host": "LTT 1445 A",
        "semi_major_axis_au": 0.09,
        "epistemic_level": "SPECULATIVE",
    },
    "observed_planets": [
        {
            "name": "World B",
            "host": "LTT 1445 A",
            "semi_major_axis_au": 0.0381,
            "mass_earth": 2.73,
            "radius_earth": 1.34,
            "equilibrium_temperature_k": 431,
            "epistemic_level": "OBSERVED",
        }
    ],
}

ASTRO = {
    "societies": [{
        "lineage_id": "L1",
        "population_alias": "Aster-1",
        "technical_balance": 0.82,
        "knowledge_retention": 0.84,
        "system_redundancy": 0.78,
        "technology_portfolio": {
            "infrastructure": 0.82,
            "mobility": 0.76,
        },
    }]
}


class EvolutionaryReplayTests(unittest.TestCase):
    def test_replay_is_reproducible_with_same_seed(self):
        first = run_evolutionary_replay(
            SYSTEM, ASTRO, years=30_000, runs=16, seed=1445
        )
        second = run_evolutionary_replay(
            SYSTEM, ASTRO, years=30_000, runs=16, seed=1445
        )
        self.assertEqual(first["runs"], second["runs"])
        self.assertEqual(first["outcomes"], second["outcomes"])

    def test_frequencies_sum_to_one(self):
        result = run_evolutionary_replay(
            SYSTEM, ASTRO, years=30_000, runs=24, seed=7
        )
        self.assertAlmostEqual(
            sum(result["outcomes"]["frequencies"].values()),
            1.0,
            places=9,
        )

    def test_all_runs_keep_declared_count(self):
        result = run_evolutionary_replay(
            SYSTEM, ASTRO, years=30_000, runs=12, seed=8
        )
        self.assertEqual(len(result["runs"]), 12)
        self.assertEqual(result["summary"]["runs"], 12)

    def test_sensitivity_correlations_are_bounded(self):
        result = run_evolutionary_replay(
            SYSTEM, ASTRO, years=30_000, runs=20, seed=10
        )
        for row in result["sensitivity"]:
            self.assertGreaterEqual(row["outcome_correlation"], -1.0)
            self.assertLessEqual(row["outcome_correlation"], 1.0)
            self.assertGreaterEqual(row["divergence_correlation"], -1.0)
            self.assertLessEqual(row["divergence_correlation"], 1.0)

    def test_frequency_is_not_labeled_probability(self):
        result = run_evolutionary_replay(
            SYSTEM, ASTRO, years=30_000, runs=8, seed=5
        )
        joined = " ".join(result["limitations"]).lower()
        self.assertIn("not real-world probabilities", joined)


if __name__ == "__main__":
    unittest.main()
