import unittest

from engine.evolution.offworld import simulate_offworld_divergence


INTERPLANETARY = {
    "worlds": [
        {
            "world_id": "OBS-1",
            "gravity_earth": 1.25,
        }
    ],
    "attempts": [
        {
            "lineage_id": "L1",
            "destination_id": "OBS-1",
            "effective_founders": 220,
            "gene_flow": 0.08,
            "founder_effect_pressure": 0.55,
        }
    ],
}

NETWORK = {
    "colonies": [
        {
            "active": True,
            "lineage_id": "L1",
            "population_alias": "Aster-1",
            "destination_id": "OBS-1",
            "destination_name": "World B",
            "population": 2200,
            "resource_margin": 0.62,
            "post_settlement_contact": 0.10,
            "resupply_strength": 0.12,
            "settlement_burden": 0.62,
            "habitat_capacity": 0.66,
            "infrastructure_integrity": 0.58,
            "self_sufficiency": 0.72,
            "supply_dependency": 0.30,
        }
    ]
}


class OffworldDivergenceTests(unittest.TestCase):
    def test_no_species_claim_is_created(self):
        result = simulate_offworld_divergence(
            INTERPLANETARY, NETWORK, years=50_000
        )
        self.assertEqual(len(result["branches"]), 1)
        branch = result["branches"][0]
        self.assertFalse(branch["species_claim"])
        self.assertFalse(branch["anatomical_change_inferred"])

    def test_divergence_remains_bounded(self):
        result = simulate_offworld_divergence(
            INTERPLANETARY, NETWORK, years=50_000
        )
        branch = result["branches"][0]
        self.assertGreaterEqual(branch["divergence_proxy"], 0.0)
        self.assertLessEqual(branch["divergence_proxy"], 1.0)

    def test_more_contact_reduces_drift_pressure(self):
        isolated = simulate_offworld_divergence(
            INTERPLANETARY, NETWORK, years=50_000
        )
        connected_network = {
            "colonies": [
                {
                    **NETWORK["colonies"][0],
                    "post_settlement_contact": 0.95,
                    "resupply_strength": 0.90,
                }
            ]
        }
        connected = simulate_offworld_divergence(
            INTERPLANETARY, connected_network, years=50_000
        )
        self.assertLess(
            connected["branches"][0]["drift_pressure"],
            isolated["branches"][0]["drift_pressure"],
        )


if __name__ == "__main__":
    unittest.main()
