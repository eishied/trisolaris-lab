import unittest

from engine.evolution.counterfactual import compare_counterfactual

SYSTEM = {
    "stars": [{"id": "A", "mass_solar": 0.257}],
    "hypothetical_experiment": {
        "id": "H-01", "name": "TRISOLARIS H-01", "host": "LTT 1445 A",
        "semi_major_axis_au": 0.09, "epistemic_level": "SPECULATIVE",
    },
    "observed_planets": [{
        "name": "World B", "host": "LTT 1445 A", "semi_major_axis_au": 0.0381,
        "mass_earth": 2.73, "radius_earth": 1.34,
        "equilibrium_temperature_k": 431, "epistemic_level": "OBSERVED",
    }],
}
ASTRO = {"societies": [{
    "lineage_id": "L1", "population_alias": "Aster-1",
    "technical_balance": 0.50, "knowledge_retention": 0.58,
    "system_redundancy": 0.54,
    "technology_portfolio": {"infrastructure": 0.56, "mobility": 0.48},
}]}

class CounterfactualReplayTests(unittest.TestCase):
    def test_same_intervention_is_reproducible(self):
        a = compare_counterfactual(SYSTEM, ASTRO, years=30000, parameter="capability",
            intervention_fraction=0.20, runs=16, seed=22)
        b = compare_counterfactual(SYSTEM, ASTRO, years=30000, parameter="capability",
            intervention_fraction=0.20, runs=16, seed=22)
        self.assertEqual(a["paired_runs"], b["paired_runs"])

    def test_zero_intervention_has_no_paired_flips(self):
        result = compare_counterfactual(SYSTEM, ASTRO, years=30000, parameter="founder_size",
            intervention_fraction=0.0, runs=16, seed=9)
        self.assertEqual(result["summary"]["outcome_flip_count"], 0)
        self.assertAlmostEqual(result["summary"]["mean_outcome_score_delta"], 0.0)

    def test_frequency_deltas_balance(self):
        result = compare_counterfactual(SYSTEM, ASTRO, years=30000, parameter="resupply_strength",
            intervention_fraction=0.4, runs=20, seed=2)
        self.assertAlmostEqual(sum(result["frequency_deltas"].values()), 0.0, places=9)

    def test_unsupported_parameter_fails(self):
        with self.assertRaises(ValueError):
            compare_counterfactual(SYSTEM, ASTRO, years=10000, parameter="magic",
                intervention_fraction=0.1, runs=8)

if __name__ == "__main__":
    unittest.main()
