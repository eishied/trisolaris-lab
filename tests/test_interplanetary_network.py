import unittest

from engine.human.interplanetary_network import simulate_interplanetary_network


PERSISTENT = {
    "worlds": [
        {"world_id": "H-01", "role": "origin"},
        {
            "world_id": "OBS-1",
            "role": "destination",
            "gravity_earth": 1.15,
            "controlled_habitat_required": True,
        },
    ],
    "attempts": [
        {
            "population_alias": "Aster-1",
            "lineage_id": "L1",
            "destination_id": "OBS-1",
            "destination_name": "World B",
            "settlement_persists": True,
            "arrival_survivors": 640,
            "habitat_capacity": 0.72,
            "settlement_burden": 0.58,
            "technology_continuity": 0.78,
            "post_settlement_contact": 0.42,
            "transfer_days": 5.4,
        }
    ],
}

FAILED = {
    "worlds": [{"world_id": "H-01", "role": "origin"}],
    "attempts": [
        {
            "population_alias": "Nival-2",
            "lineage_id": "L2",
            "destination_id": "OBS-2",
            "destination_name": "World C",
            "settlement_persists": False,
            "arrival_survivors": 0,
        }
    ],
}


class InterplanetaryNetworkTests(unittest.TestCase):
    def test_failed_attempt_does_not_create_colony(self):
        result = simulate_interplanetary_network(FAILED, years=20_000)
        self.assertEqual(result["summary"]["colony_count"], 0)
        self.assertEqual(result["summary"]["active_colony_count"], 0)

    def test_persistent_settlement_gets_own_demography(self):
        result = simulate_interplanetary_network(
            PERSISTENT, years=20_000, resupply_strength=0.50
        )
        self.assertEqual(result["summary"]["colony_count"], 1)
        colony = result["colonies"][0]
        self.assertGreaterEqual(colony["carrying_capacity"], colony["initial_population"])
        self.assertGreaterEqual(colony["population"], 0)
        self.assertEqual(len(colony["timeline"]), 6)

    def test_infrastructure_shock_can_reduce_integrity(self):
        calm = simulate_interplanetary_network(
            PERSISTENT, years=10_000, infrastructure_shock=0.0
        )
        shock = simulate_interplanetary_network(
            PERSISTENT, years=10_000, infrastructure_shock=0.9
        )
        self.assertLess(
            shock["colonies"][0]["infrastructure_integrity"],
            calm["colonies"][0]["infrastructure_integrity"],
        )

    def test_return_migration_is_conditional(self):
        enabled = simulate_interplanetary_network(
            PERSISTENT, years=20_000, enable_return_migration=True
        )
        disabled = simulate_interplanetary_network(
            PERSISTENT, years=20_000, enable_return_migration=False
        )
        self.assertGreaterEqual(enabled["summary"]["return_migrants"], 0)
        self.assertEqual(disabled["summary"]["return_migrants"], 0)


if __name__ == "__main__":
    unittest.main()
