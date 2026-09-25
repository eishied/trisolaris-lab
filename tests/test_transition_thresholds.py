import unittest

from engine.evolution.thresholds import scan_transition_thresholds


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
        "technical_balance": 0.20,
        "knowledge_retention": 0.25,
        "system_redundancy": 0.20,
        "technology_portfolio": {
            "infrastructure": 0.20,
            "mobility": 0.20,
        },
    }]
}


class TransitionThresholdAtlasTests(unittest.TestCase):
    def test_capability_can_cross_launch_bottleneck(self):
        result = scan_transition_thresholds(
            SYSTEM,
            ASTRO,
            years=30_000,
            runs=4,
            seed=12,
            uncertainty=0.05,
            target_frequency=0.50,
        )
        scans = {row["parameter"]: row for row in result["scans"]}
        self.assertTrue(scans["capability_multiplier"]["threshold_reached"])
        self.assertIsNotNone(
            scans["capability_multiplier"]["first_target_crossing_value"]
        )

    def test_founder_size_cannot_fix_prelaunch_readiness(self):
        result = scan_transition_thresholds(
            SYSTEM,
            ASTRO,
            years=30_000,
            runs=4,
            seed=12,
            uncertainty=0.05,
            target_frequency=0.50,
        )
        scans = {row["parameter"]: row for row in result["scans"]}
        self.assertFalse(scans["founder_size"]["threshold_reached"])

    def test_curve_frequencies_are_bounded(self):
        result = scan_transition_thresholds(
            SYSTEM,
            ASTRO,
            years=10_000,
            runs=4,
            seed=3,
        )
        for scan in result["scans"]:
            for point in scan["curve"]:
                self.assertGreaterEqual(
                    point["non_no_launch_frequency"], 0.0
                )
                self.assertLessEqual(
                    point["non_no_launch_frequency"], 1.0
                )

    def test_invalid_run_count_is_rejected(self):
        with self.assertRaises(ValueError):
            scan_transition_thresholds(
                SYSTEM,
                ASTRO,
                years=10_000,
                runs=1,
            )


if __name__ == "__main__":
    unittest.main()
