import unittest

from engine.human.demography import simulate_demography


HISTORY = {
    "populations": [
        {
            "lineage_id": "L1",
            "lineage_name": "Linaje Borealis-1",
            "refuge_name": "Borealis-1",
            "relative_capacity_share": 0.55,
            "settlement_intensity": 0.72,
            "open_agriculture": 0.42,
            "controlled_agriculture": 0.58,
            "infrastructure": 0.66,
            "water_recycling": 0.55,
            "thermal_shelter": 0.68,
            "mobility_network": 0.45,
            "knowledge_continuity": 0.74,
        },
        {
            "lineage_id": "L2",
            "lineage_name": "Linaje Equatoria-2",
            "refuge_name": "Equatoria-2",
            "relative_capacity_share": 0.45,
            "settlement_intensity": 0.80,
            "open_agriculture": 0.76,
            "controlled_agriculture": 0.31,
            "infrastructure": 0.58,
            "water_recycling": 0.32,
            "thermal_shelter": 0.45,
            "mobility_network": 0.52,
            "knowledge_continuity": 0.70,
        },
    ]
}


class DemographyTests(unittest.TestCase):
    def test_population_stays_within_capacity(self):
        result = simulate_demography(HISTORY, total_years=50_000)
        for population in result["populations"]:
            self.assertLessEqual(
                population["population_index"],
                population["carrying_capacity_index"] + 1e-6,
            )

    def test_explicit_disturbance_can_create_bottleneck(self):
        result = simulate_demography(
            HISTORY,
            total_years=50_000,
            view_years=35_000,
            disturbance="infrastructure",
            severity=1.0,
        )
        self.assertGreaterEqual(result["summary"]["bottleneck_count"], 1)

    def test_no_disturbance_creates_no_bottleneck_events(self):
        result = simulate_demography(
            HISTORY,
            total_years=50_000,
            disturbance="none",
            severity=0.0,
        )
        self.assertEqual(result["summary"]["bottleneck_count"], 0)
        self.assertEqual(result["events"], [])

    def test_view_time_is_clamped(self):
        result = simulate_demography(
            HISTORY,
            total_years=10_000,
            view_years=100_000,
        )
        self.assertEqual(result["inputs"]["view_years"], 10_000)


if __name__ == "__main__":
    unittest.main()
