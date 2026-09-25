import unittest

from engine.climate.latitudinal_ebm import solve_latitudinal_climate
from engine.planetary.surface_systems import (
    boiling_point_c_approx,
    solve_surface_systems,
)


class SurfaceSystemsTests(unittest.TestCase):
    def setUp(self):
        self.climate = solve_latitudinal_climate(
            stellar_flux_earth=1.0,
            albedo=0.30,
            greenhouse_k=33.0,
        )

    def test_boiling_point_increases_with_pressure(self):
        self.assertGreater(
            boiling_point_c_approx(2.0),
            boiling_point_c_approx(0.5),
        )

    def test_no_water_means_no_productivity(self):
        result = solve_surface_systems(
            self.climate,
            pressure_bar=1.0,
            water_inventory_earth_oceans=0.0,
            stellar_flux_earth=1.0,
        )
        self.assertEqual(
            result["summary"]["biosphere_productivity_potential"],
            0.0,
        )

    def test_more_water_strengthens_cycle_from_dry_baseline(self):
        dry = solve_surface_systems(
            self.climate,
            pressure_bar=1.0,
            water_inventory_earth_oceans=0.05,
            stellar_flux_earth=1.0,
        )
        wet = solve_surface_systems(
            self.climate,
            pressure_bar=1.0,
            water_inventory_earth_oceans=1.0,
            stellar_flux_earth=1.0,
        )
        self.assertGreater(
            wet["summary"]["hydrological_cycle_strength"],
            dry["summary"]["hydrological_cycle_strength"],
        )

    def test_surface_model_resolves_multiple_latitudes(self):
        result = solve_surface_systems(
            self.climate,
            pressure_bar=1.0,
            water_inventory_earth_oceans=1.0,
            stellar_flux_earth=1.0,
        )
        self.assertGreater(len(result["bands"]), 20)


if __name__ == "__main__":
    unittest.main()
