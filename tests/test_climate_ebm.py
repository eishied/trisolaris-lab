import unittest

from engine.climate.latitudinal_ebm import solve_latitudinal_climate


class LatitudinalEBMTests(unittest.TestCase):
    def test_planet_is_not_single_temperature(self):
        result = solve_latitudinal_climate(
            stellar_flux_earth=1.0,
            albedo=0.30,
            greenhouse_k=33.0,
        )
        summary = result["summary"]
        self.assertGreater(summary["equator_to_pole_contrast_k"], 10.0)

    def test_more_flux_warms_global_mean(self):
        cool = solve_latitudinal_climate(
            stellar_flux_earth=0.8,
            albedo=0.30,
            greenhouse_k=33.0,
        )
        warm = solve_latitudinal_climate(
            stellar_flux_earth=1.1,
            albedo=0.30,
            greenhouse_k=33.0,
        )
        self.assertGreater(
            warm["summary"]["global_mean_temperature_c"],
            cool["summary"]["global_mean_temperature_c"],
        )

    def test_higher_albedo_cools_planet(self):
        dark = solve_latitudinal_climate(
            stellar_flux_earth=1.0,
            albedo=0.20,
            greenhouse_k=33.0,
        )
        bright = solve_latitudinal_climate(
            stellar_flux_earth=1.0,
            albedo=0.50,
            greenhouse_k=33.0,
        )
        self.assertLess(
            bright["summary"]["global_mean_temperature_c"],
            dark["summary"]["global_mean_temperature_c"],
        )


if __name__ == "__main__":
    unittest.main()
