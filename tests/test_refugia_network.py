import unittest

from engine.climate.latitudinal_ebm import solve_latitudinal_climate
from engine.planetary.surface_systems import solve_surface_systems
from engine.ecology.food_web import evaluate_food_web
from engine.human.settlement import evaluate_settlement_support
from engine.human.refugia import build_refugia_network


class RefugiaNetworkTests(unittest.TestCase):
    def setUp(self):
        climate = solve_latitudinal_climate(
            stellar_flux_earth=1.0,
            albedo=0.30,
            greenhouse_k=33.0,
        )
        surface = solve_surface_systems(
            climate,
            pressure_bar=1.0,
            water_inventory_earth_oceans=1.0,
            stellar_flux_earth=1.0,
        )
        foodweb = evaluate_food_web(
            surface,
            oxygen_fraction=0.21,
            nutrient_availability=1.0,
        )
        self.settlement = evaluate_settlement_support(
            surface,
            foodweb,
            pressure_bar=1.0,
            oxygen_fraction=0.21,
            technology_support=0.40,
        )

    def test_refugia_have_names(self):
        network = build_refugia_network(self.settlement, mobility=0.45)
        for refuge in network["refugia"]:
            self.assertTrue(refuge["name"])

    def test_higher_mobility_reduces_isolation_when_multiple_refugia_exist(self):
        low = build_refugia_network(self.settlement, mobility=0.10)
        high = build_refugia_network(self.settlement, mobility=0.90)
        if len(low["refugia"]) > 1 and len(high["refugia"]) > 1:
            self.assertLessEqual(
                high["summary"]["maximum_isolation_potential"],
                low["summary"]["maximum_isolation_potential"],
            )

    def test_population_shares_sum_to_one_when_refugia_exist(self):
        network = build_refugia_network(self.settlement, mobility=0.45)
        if network["refugia"]:
            self.assertAlmostEqual(
                sum(r["relative_population_share_if_settled"] for r in network["refugia"]),
                1.0,
                places=8,
            )


if __name__ == "__main__":
    unittest.main()
