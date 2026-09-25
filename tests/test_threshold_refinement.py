import unittest

from engine.evolution.threshold_refinement import refine_capability_thresholds


SYSTEM = {
    "stars": [{"id": "A", "mass_solar": 0.257}],
    "hypothetical_experiment": {
        "id": "H-01",
        "name": "TRISOLARIS H-01",
        "host": "LTT 1445 A",
        "semi_major_axis_au": 0.09,
        "epistemic_level": "SPECULATIVE",
    },
    "observed_planets": [{
        "name": "World B",
        "host": "LTT 1445 A",
        "semi_major_axis_au": 0.0381,
        "mass_earth": 2.73,
        "radius_earth": 1.34,
        "equilibrium_temperature_k": 431,
        "epistemic_level": "OBSERVED",
    }],
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
COARSE = {
    "scans": [{
        "parameter": "capability_multiplier",
        "curve": [
            {
                "value": 2.0,
                "non_no_launch_frequency": 0.0,
                "persistent_colony_frequency": 0.0,
                "divergent_lineage_frequency": 0.0,
            },
            {
                "value": 2.5,
                "non_no_launch_frequency": 1.0,
                "persistent_colony_frequency": 0.0,
                "divergent_lineage_frequency": 0.0,
            },
        ],
    }]
}


class AdaptiveThresholdRefinementTests(unittest.TestCase):
    def test_refines_reproducible_launch_crossing(self):
        result = refine_capability_thresholds(
            SYSTEM,
            ASTRO,
            COARSE,
            years=30_000,
            runs=4,
            seed=12,
            uncertainty=0.05,
            iterations=3,
        )
        launch = next(
            row for row in result["refinements"]
            if row["stage"] == "leave_no_launch"
        )
        self.assertTrue(launch["refinable"])
        self.assertGreater(
            launch["refined_threshold_upper"],
            launch["refined_threshold_lower"],
        )
        self.assertLessEqual(launch["interval_width"], 0.5 / 8)

    def test_missing_crossing_is_not_invented(self):
        result = refine_capability_thresholds(
            SYSTEM,
            ASTRO,
            COARSE,
            years=30_000,
            runs=4,
            seed=12,
            uncertainty=0.05,
            iterations=2,
        )
        persistent = next(
            row for row in result["refinements"]
            if row["stage"] == "persistent_colony"
        )
        self.assertFalse(persistent["refinable"])
        self.assertIsNone(persistent["refined_threshold_upper"])

    def test_invalid_iteration_count_is_rejected(self):
        with self.assertRaises(ValueError):
            refine_capability_thresholds(
                SYSTEM,
                ASTRO,
                COARSE,
                years=10_000,
                runs=4,
                iterations=0,
            )


if __name__ == "__main__":
    unittest.main()
