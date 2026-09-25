import unittest

from engine.evolution.popgen import simulate_population_genetics


NETWORK = {
    "refugia": [
        {
            "id": "R1",
            "name": "Borealis-1",
            "relative_population_share_if_settled": 0.5,
            "isolation_potential": 0.9,
            "stress_components": {
                "thermal": 0.7, "water": 0.2, "oxygen": 0.2, "food": 0.4,
            },
        },
        {
            "id": "R2",
            "name": "Australis-2",
            "relative_population_share_if_settled": 0.5,
            "isolation_potential": 0.9,
            "stress_components": {
                "thermal": 0.2, "water": 0.7, "oxygen": 0.2, "food": 0.7,
            },
        },
    ],
    "links": [
        {"source": "R1", "target": "R2", "migration_flow_potential": 0.03},
    ],
}


class PopulationGeneticsTests(unittest.TestCase):
    def test_frequencies_stay_bounded(self):
        result = simulate_population_genetics(NETWORK, years=100_000)
        for population in result["populations"]:
            for p in population["allele_frequencies"].values():
                self.assertGreater(p, 0.0)
                self.assertLess(p, 1.0)

    def test_divergent_environments_create_nonzero_fst(self):
        result = simulate_population_genetics(NETWORK, years=100_000)
        self.assertGreater(result["summary"]["mean_fst_proxy"], 0.0)

    def test_high_technology_reduces_selection_exposure_effect(self):
        low = simulate_population_genetics(NETWORK, years=100_000, technology_buffer=0.0)
        high = simulate_population_genetics(NETWORK, years=100_000, technology_buffer=0.9)
        self.assertLessEqual(
            high["summary"]["mean_fst_proxy"],
            low["summary"]["mean_fst_proxy"] + 0.15,
        )


if __name__ == "__main__":
    unittest.main()
