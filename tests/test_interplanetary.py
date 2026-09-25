import unittest

from engine.human.interplanetary import (
    build_world_catalog,
    simulate_interplanetary_settlement,
)


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
            "name": "LTT 1445 A b",
            "host": "LTT 1445 A",
            "semi_major_axis_au": 0.0381,
            "mass_earth": 2.73,
            "radius_earth": 1.34,
            "equilibrium_temperature_k": 431,
            "epistemic_level": "OBSERVED",
            "source": "NASA Exoplanet Archive / ps",
        },
        {
            "name": "LTT 1445 A c",
            "host": "LTT 1445 A",
            "semi_major_axis_au": 0.02661,
            "mass_earth": 1.54,
            "radius_earth": 1.147,
            "equilibrium_temperature_k": 508,
            "epistemic_level": "OBSERVED",
            "source": "NASA Exoplanet Archive / ps",
        },
    ],
}

STRONG_ASTRO = {
    "societies": [{
        "lineage_id": "L1",
        "population_alias": "Aster-1",
        "technical_balance": 0.86,
        "knowledge_retention": 0.88,
        "system_redundancy": 0.82,
        "technology_portfolio": {
            "infrastructure": 0.88,
            "mobility": 0.80,
        },
    }]
}

WEAK_ASTRO = {
    "societies": [{
        "lineage_id": "L2",
        "population_alias": "Nival-2",
        "technical_balance": 0.16,
        "knowledge_retention": 0.24,
        "system_redundancy": 0.18,
        "technology_portfolio": {
            "infrastructure": 0.20,
            "mobility": 0.12,
        },
    }]
}


class InterplanetarySettlementTests(unittest.TestCase):
    def test_world_catalog_preserves_observed_vs_speculative(self):
        worlds = build_world_catalog(SYSTEM)
        by_name = {world["name"]: world for world in worlds}
        self.assertEqual(by_name["TRISOLARIS H-01"]["epistemic_level"], "SPECULATIVE")
        self.assertEqual(by_name["LTT 1445 A b"]["epistemic_level"], "OBSERVED")
        self.assertTrue(by_name["LTT 1445 A b"]["controlled_habitat_required"])

    def test_same_system_transfer_is_finite_and_positive(self):
        worlds = build_world_catalog(SYSTEM)
        destinations = [world for world in worlds if world["role"] == "destination"]
        for world in destinations:
            self.assertGreater(world["transfer_days_from_h01"], 0.0)
            self.assertLess(world["transfer_days_from_h01"], 30.0)

    def test_weak_population_is_not_forced_to_launch(self):
        result = simulate_interplanetary_settlement(
            SYSTEM, WEAK_ASTRO, years=50_000, founder_size=500, launch_active=True
        )
        self.assertTrue(result["attempts"])
        self.assertTrue(all(not attempt["launch_feasible"] for attempt in result["attempts"]))
        self.assertTrue(all(attempt["arrival_survivors"] == 0 for attempt in result["attempts"]))

    def test_strong_population_can_persist_but_branch_is_conditional(self):
        result = simulate_interplanetary_settlement(
            SYSTEM,
            STRONG_ASTRO,
            years=50_000,
            founder_size=800,
            exchange_strength=0.15,
            launch_active=True,
        )
        self.assertTrue(any(attempt["settlement_persists"] for attempt in result["attempts"]))
        for attempt in result["attempts"]:
            self.assertGreaterEqual(attempt["divergence_proxy"], 0.0)
            self.assertLessEqual(attempt["divergence_proxy"], 1.0)
            if attempt["offworld_branch_emerges"]:
                self.assertTrue(attempt["settlement_persists"])
                self.assertIsNotNone(attempt["offworld_branch_id"])

    def test_assessment_mode_never_creates_settlement(self):
        result = simulate_interplanetary_settlement(
            SYSTEM, STRONG_ASTRO, years=50_000, founder_size=800, launch_active=False
        )
        self.assertTrue(all(attempt["status"] == "assessment-only" for attempt in result["attempts"]))
        self.assertEqual(result["summary"]["persistent_settlement_count"], 0)

    def test_founder_size_is_explicit_not_population_index(self):
        result = simulate_interplanetary_settlement(
            SYSTEM, STRONG_ASTRO, years=10_000, founder_size=321, launch_active=True
        )
        self.assertTrue(all(attempt["founder_size"] == 321 for attempt in result["attempts"]))


if __name__ == "__main__":
    unittest.main()
