import unittest

from engine.human.astroanthropology import simulate_astroanthropology


HISTORY = {
    "populations": [
        {
            "lineage_id": "L1",
            "lineage_name": "Linaje Equatoria-1",
            "refuge_name": "Equatoria-1",
            "settlement_intensity": 0.72,
            "open_agriculture": 0.42,
            "controlled_agriculture": 0.58,
            "infrastructure": 0.66,
            "water_recycling": 0.55,
            "thermal_shelter": 0.68,
            "mobility_network": 0.45,
            "knowledge_continuity": 0.74,
            "cultural_differentiation_proxy": 0.46,
        },
        {
            "lineage_id": "L2",
            "lineage_name": "Linaje Borealis-2",
            "refuge_name": "Borealis-2",
            "settlement_intensity": 0.56,
            "open_agriculture": 0.20,
            "controlled_agriculture": 0.71,
            "infrastructure": 0.62,
            "water_recycling": 0.70,
            "thermal_shelter": 0.82,
            "mobility_network": 0.34,
            "knowledge_continuity": 0.52,
            "cultural_differentiation_proxy": 0.78,
        },
    ],
    "migration_links": [
        {
            "source_lineage_id": "L1",
            "target_lineage_id": "L2",
            "migration_flow": 0.48,
        }
    ],
}

DEMOGRAPHY = {
    "populations": [
        {
            "lineage_id": "L1",
            "population_index": 400,
            "carrying_capacity_index": 500,
            "reserve_proxy": 0.62,
            "bottleneck": False,
            "recovery_fraction": 1.0,
            "status": "stable",
        },
        {
            "lineage_id": "L2",
            "population_index": 180,
            "carrying_capacity_index": 350,
            "reserve_proxy": 0.35,
            "bottleneck": True,
            "recovery_fraction": 0.22,
            "status": "bottleneck",
        },
    ]
}


class AstroanthropologyTests(unittest.TestCase):
    def test_does_not_create_progress_ranking(self):
        result = simulate_astroanthropology(HISTORY, DEMOGRAPHY, years=50_000)
        for society in result["societies"]:
            self.assertNotIn("rank", society)
            self.assertNotIn("advanced", society)
            self.assertGreaterEqual(society["technical_balance"], 0.0)
            self.assertLessEqual(society["technical_balance"], 1.0)

    def test_bottleneck_reduces_retention(self):
        result = simulate_astroanthropology(HISTORY, DEMOGRAPHY, years=50_000)
        by_id = {s["lineage_id"]: s for s in result["societies"]}
        self.assertLess(
            by_id["L2"]["knowledge_retention"],
            by_id["L1"]["knowledge_retention"],
        )

    def test_alias_is_stable_and_explicitly_narrative(self):
        result = simulate_astroanthropology(HISTORY, DEMOGRAPHY, years=50_000)
        society = result["societies"][0]
        self.assertTrue(society["population_alias"])
        self.assertIn("not an inferred ethnonym", society["alias_rule"])

    def test_exchange_uses_mobility_and_links(self):
        result = simulate_astroanthropology(
            HISTORY,
            DEMOGRAPHY,
            years=50_000,
            exchange_strength=1.0,
        )
        self.assertGreater(result["summary"]["mean_cultural_exchange"], 0.0)


if __name__ == "__main__":
    unittest.main()
