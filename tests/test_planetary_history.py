import unittest

from engine.human.planetary_history import simulate_planetary_history


REFUGIA = {
    "refugia": [
        {
            "id": "R1",
            "name": "Borealis-1",
            "center_latitude_deg": 55.0,
            "latitude_min_deg": 40.0,
            "latitude_max_deg": 70.0,
            "natural_support": 0.58,
            "assisted_support": 0.76,
            "agriculture_potential": 0.42,
            "relative_population_share_if_settled": 0.55,
            "stress_components": {"thermal": 0.65, "water": 0.30},
        },
        {
            "id": "R2",
            "name": "Equatoria-2",
            "center_latitude_deg": 5.0,
            "latitude_min_deg": -15.0,
            "latitude_max_deg": 20.0,
            "natural_support": 0.72,
            "assisted_support": 0.84,
            "agriculture_potential": 0.70,
            "relative_population_share_if_settled": 0.45,
            "stress_components": {"thermal": 0.20, "water": 0.25},
        },
    ],
    "links": [
        {"source": "R1", "target": "R2", "migration_flow_potential": 0.22},
    ],
}

LINEAGES = {
    "lineages": [
        {
            "id": "L1",
            "name": "Linaje Borealis-1",
            "refuge_id": "R1",
            "isolation_potential": 0.72,
            "gene_flow_proxy": 0.18,
        },
        {
            "id": "L2",
            "name": "Linaje Equatoria-2",
            "refuge_id": "R2",
            "isolation_potential": 0.58,
            "gene_flow_proxy": 0.22,
        },
    ]
}


class PlanetaryHistoryTests(unittest.TestCase):
    def test_generates_population_regions(self):
        result = simulate_planetary_history(REFUGIA, LINEAGES)
        self.assertEqual(result["summary"]["population_regions"], 2)

    def test_technology_increases_infrastructure(self):
        low = simulate_planetary_history(
            REFUGIA, LINEAGES, technology_support=0.1
        )
        high = simulate_planetary_history(
            REFUGIA, LINEAGES, technology_support=0.9
        )
        self.assertGreater(
            high["summary"]["mean_infrastructure"],
            low["summary"]["mean_infrastructure"],
        )

    def test_mobility_changes_realized_links(self):
        low = simulate_planetary_history(REFUGIA, LINEAGES, mobility=0.1)
        high = simulate_planetary_history(REFUGIA, LINEAGES, mobility=0.9)
        self.assertGreater(
            high["migration_links"][0]["migration_flow_proxy"],
            low["migration_links"][0]["migration_flow_proxy"],
        )

    def test_culture_is_not_ranked(self):
        result = simulate_planetary_history(REFUGIA, LINEAGES)
        self.assertIn("cultural_differentiation_proxy", result["populations"][0])
        self.assertNotIn("culture_score", result["populations"][0])


if __name__ == "__main__":
    unittest.main()
