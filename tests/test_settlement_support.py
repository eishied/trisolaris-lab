import unittest

from engine.climate.latitudinal_ebm import solve_latitudinal_climate
from engine.planetary.surface_systems import solve_surface_systems
from engine.ecology.food_web import evaluate_food_web
from engine.human.settlement import evaluate_settlement_support


class SettlementSupportTests(unittest.TestCase):
    def setUp(self):
        climate = solve_latitudinal_climate(
            stellar_flux_earth=1.0,
            albedo=0.30,
            greenhouse_k=33.0,
        )
        self.surface = solve_surface_systems(
            climate,
            pressure_bar=1.0,
            water_inventory_earth_oceans=1.0,
            stellar_flux_earth=1.0,
        )
        self.foodweb = evaluate_food_web(
            self.surface,
            oxygen_fraction=0.21,
            nutrient_availability=1.0,
            life_seeded=False,
        )

    def test_technology_can_improve_support_but_creates_dependency(self):
        low = evaluate_settlement_support(
            self.surface,
            self.foodweb,
            pressure_bar=1.0,
            oxygen_fraction=0.21,
            technology_support=0.0,
        )
        high = evaluate_settlement_support(
            self.surface,
            self.foodweb,
            pressure_bar=1.0,
            oxygen_fraction=0.21,
            technology_support=0.8,
        )
        self.assertGreater(
            high["summary"]["assisted_support_mean"],
            low["summary"]["assisted_support_mean"],
        )
        self.assertGreater(
            high["summary"]["technology_dependency_mean"],
            low["summary"]["technology_dependency_mean"],
        )

    def test_low_oxygen_reduces_natural_support(self):
        low = evaluate_settlement_support(
            self.surface,
            self.foodweb,
            pressure_bar=1.0,
            oxygen_fraction=0.05,
            technology_support=0.0,
        )
        normal = evaluate_settlement_support(
            self.surface,
            self.foodweb,
            pressure_bar=1.0,
            oxygen_fraction=0.21,
            technology_support=0.0,
        )
        self.assertGreater(
            normal["summary"]["natural_support_mean"],
            low["summary"]["natural_support_mean"],
        )

    def test_model_resolves_regional_bands(self):
        result = evaluate_settlement_support(
            self.surface,
            self.foodweb,
            pressure_bar=1.0,
            oxygen_fraction=0.21,
            technology_support=0.4,
        )
        self.assertGreater(len(result["bands"]), 20)


if __name__ == "__main__":
    unittest.main()
