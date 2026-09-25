import unittest

from engine.climate.latitudinal_ebm import solve_latitudinal_climate
from engine.planetary.surface_systems import solve_surface_systems
from engine.ecology.food_web import evaluate_food_web


class FoodWebSupportTests(unittest.TestCase):
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

    def test_model_does_not_assume_life(self):
        result = evaluate_food_web(
            self.surface,
            oxygen_fraction=0.21,
            nutrient_availability=1.0,
            life_seeded=False,
        )
        self.assertEqual(
            result["summary"]["life_state"],
            "environmental support only; life not assumed",
        )

    def test_low_oxygen_reduces_large_aerobic_support(self):
        low = evaluate_food_web(
            self.surface,
            oxygen_fraction=0.005,
            nutrient_availability=1.0,
        )
        high = evaluate_food_web(
            self.surface,
            oxygen_fraction=0.21,
            nutrient_availability=1.0,
        )
        low_guild = next(g for g in low["guilds"] if g["id"] == "large_aerobic")
        high_guild = next(g for g in high["guilds"] if g["id"] == "large_aerobic")
        self.assertGreater(
            high_guild["support_potential"],
            low_guild["support_potential"],
        )

    def test_nutrients_increase_primary_producer_support(self):
        low = evaluate_food_web(
            self.surface,
            oxygen_fraction=0.21,
            nutrient_availability=0.1,
        )
        high = evaluate_food_web(
            self.surface,
            oxygen_fraction=0.21,
            nutrient_availability=2.0,
        )
        low_guild = next(g for g in low["guilds"] if g["id"] == "primary_producers")
        high_guild = next(g for g in high["guilds"] if g["id"] == "primary_producers")
        self.assertGreater(
            high_guild["support_potential"],
            low_guild["support_potential"],
        )


if __name__ == "__main__":
    unittest.main()
