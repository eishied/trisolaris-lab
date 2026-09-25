import unittest

from engine.evolution.lineages import simulate_lineage_divergence


NETWORK = {
    "refugia": [
        {
            "id": "R1",
            "name": "Borealis-1",
            "relative_population_share_if_settled": 0.5,
            "isolation_potential": 0.85,
            "stress_components": {
                "thermal": 0.7,
                "water": 0.4,
                "oxygen": 0.2,
                "food": 0.3,
            },
        },
        {
            "id": "R2",
            "name": "Australis-2",
            "relative_population_share_if_settled": 0.5,
            "isolation_potential": 0.85,
            "stress_components": {
                "thermal": 0.3,
                "water": 0.7,
                "oxygen": 0.2,
                "food": 0.6,
            },
        },
    ],
    "links": [
        {
            "source": "R1",
            "target": "R2",
            "migration_flow_potential": 0.05,
        }
    ],
}


class LineageDivergenceTests(unittest.TestCase):
    def test_zero_time_produces_little_divergence(self):
        result = simulate_lineage_divergence(NETWORK, years=0)
        self.assertLess(
            result["summary"]["maximum_divergence_index"],
            0.05,
        )

    def test_time_and_isolation_allow_more_divergence(self):
        early = simulate_lineage_divergence(NETWORK, years=1_000)
        late = simulate_lineage_divergence(NETWORK, years=100_000)
        self.assertGreaterEqual(
            late["summary"]["maximum_divergence_index"],
            early["summary"]["maximum_divergence_index"],
        )

    def test_species_are_not_created_automatically(self):
        result = simulate_lineage_divergence(NETWORK, years=500_000)
        self.assertEqual(result["summary"]["species_count"], 0)
        self.assertTrue(all(l["taxonomic_status"] == "not assigned" for l in result["lineages"]))

    def test_pairwise_compatibility_is_reported(self):
        result = simulate_lineage_divergence(NETWORK, years=100_000)
        self.assertEqual(len(result["pairwise_compatibility"]), 1)
        value = result["pairwise_compatibility"][0]["reproductive_compatibility_proxy"]
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)


if __name__ == "__main__":
    unittest.main()
