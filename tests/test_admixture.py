import unittest

from engine.evolution.admixture import mix_populations


A = {
    "refuge_id": "R1",
    "refuge_name": "Borealis-1",
    "allele_frequencies": {
        "THERM-A": 0.75,
        "WATER-A": 0.35,
        "OXY-A": 0.55,
        "DIET-A": 0.40,
    },
}

B = {
    "refuge_id": "R2",
    "refuge_name": "Australis-2",
    "allele_frequencies": {
        "THERM-A": 0.30,
        "WATER-A": 0.72,
        "OXY-A": 0.48,
        "DIET-A": 0.68,
    },
}


class AdmixtureTests(unittest.TestCase):
    def test_equal_mix_is_midpoint(self):
        result = mix_populations(A, B, fraction_a=0.5)
        self.assertAlmostEqual(result["allele_frequencies"]["THERM-A"], 0.525)
        self.assertAlmostEqual(result["allele_frequencies"]["WATER-A"], 0.535)

    def test_parent_weighting_is_respected(self):
        result = mix_populations(A, B, fraction_a=0.8)
        expected = 0.8 * A["allele_frequencies"]["DIET-A"] + 0.2 * B["allele_frequencies"]["DIET-A"]
        self.assertAlmostEqual(result["allele_frequencies"]["DIET-A"], expected)

    def test_admixture_does_not_assign_species(self):
        result = mix_populations(A, B)
        self.assertEqual(result["taxonomic_status"], "not assigned")


if __name__ == "__main__":
    unittest.main()
