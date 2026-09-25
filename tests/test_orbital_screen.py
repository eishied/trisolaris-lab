import json
import math
import unittest
from pathlib import Path

from engine.orbital.screen import (
    HILL_STABILITY_THRESHOLD,
    kepler_period_days,
    mutual_hill_separation,
    screen_candidate,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "frontend/data/ltt1445.json"


class OrbitalScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = json.loads(DATA.read_text(encoding="utf-8"))

    def test_kepler_period_grows_with_semimajor_axis(self):
        p1 = kepler_period_days(0.05, 0.257, 1.0)
        p2 = kepler_period_days(0.10, 0.257, 1.0)
        self.assertGreater(p2, p1)

    def test_mutual_hill_separation_is_symmetric(self):
        a = mutual_hill_separation(0.04, 0.09, 2.73, 1.0, 0.257)
        b = mutual_hill_separation(0.09, 0.04, 1.0, 2.73, 0.257)
        self.assertAlmostEqual(a, b, places=12)

    def test_default_h01_passes_pairwise_screen(self):
        result = screen_candidate(self.dataset, 0.09, 1.0)
        self.assertTrue(result["passes_pairwise_screen"])
        self.assertGreater(
            result["minimum_delta_mutual_hill"],
            HILL_STABILITY_THRESHOLD,
        )

    def test_candidate_too_close_to_planet_b_fails(self):
        result = screen_candidate(self.dataset, 0.040, 1.0)
        self.assertFalse(result["passes_pairwise_screen"])
        self.assertLess(
            result["minimum_delta_mutual_hill"],
            HILL_STABILITY_THRESHOLD,
        )


if __name__ == "__main__":
    unittest.main()
