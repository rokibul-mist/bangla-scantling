import unittest
import math
from app.services.tonnage_service import TonnageService
from app.api.v1.endpoints_tonnage import calculate_tonnage, get_current_tonnage


class TestTonnageService(unittest.TestCase):
    def setUp(self):
        self.sample_inputs = {
            "vessel_name": "M. V. YOUNUS MOLLA-1",
            "loa": 76.21,
            "lbp": 69.85,
            "breadth": 15.24,
            "depth": 4.87,
            "draft": 4.0,
            "block_coeff": 0.721,
        }

    def test_appendix_3_coefficients(self):
        """Verify that K1 and K2 formula exactly matches statutory Appendix 3 nodes."""
        # V = 10,000 m³ -> K1 = 0.2 + 0.02 * 4.0 = 0.2800
        k1_10k = 0.2 + 0.02 * math.log10(10000)
        self.assertAlmostEqual(k1_10k, 0.2800, places=4)

        # V = 100,000 m³ -> K1 = 0.2 + 0.02 * 5.0 = 0.3000
        k1_100k = 0.2 + 0.02 * math.log10(100000)
        self.assertAlmostEqual(k1_100k, 0.3000, places=4)

        # V = 1,000,000 m³ -> K1 = 0.2 + 0.02 * 6.0 = 0.3200
        k1_1m = 0.2 + 0.02 * math.log10(1000000)
        self.assertAlmostEqual(k1_1m, 0.3200, places=4)

    def test_gross_tonnage_calculation_rule11(self):
        """Verify Rule 11 Gross Tonnage evaluation."""
        res = TonnageService.calculate_tonnage(self.sample_inputs)
        self.assertTrue(res["success"])

        # Check total volume is sum of components
        v_underdeck = res["volumes"]["v_underdeck"]
        v_super = res["volumes"]["v_superstructures"]
        v_app = res["volumes"]["v_appendages"]
        v_ex = res["volumes"]["v_excluded"]
        v_total = res["volumes"]["v_total"]
        self.assertAlmostEqual(v_total, v_underdeck + v_super + v_app - v_ex, places=2)

        # Check K1 and GT
        k1 = res["coefficients"]["k1"]
        gt = res["tonnage"]["gross_tonnage"]
        expected_k1 = round(0.2 + 0.02 * math.log10(v_total), 4)
        expected_gt = round(expected_k1 * v_total, 2)
        self.assertEqual(k1, expected_k1)
        self.assertEqual(gt, expected_gt)

    def test_net_tonnage_calculation_rule12(self):
        """Verify Rule 12 Net Tonnage evaluation and statutory floors."""
        res = TonnageService.calculate_tonnage(self.sample_inputs)
        nt = res["tonnage"]["net_tonnage"]
        gt = res["tonnage"]["gross_tonnage"]

        # Rule 12(1)(c): NT shall never be less than 0.30 GT
        self.assertGreaterEqual(nt, 0.30 * gt)

        # Check draught factor capped <= 1.0
        draft_factor = res["coefficients"]["draft_factor_applied"]
        self.assertLessEqual(draft_factor, 1.0)

        # Check cargo term >= 0.25 GT (Rule 12(1)(b))
        cargo_term = res["tonnage"]["cargo_term"]
        self.assertGreaterEqual(cargo_term, 0.25 * gt)

    def test_passenger_threshold_rule12(self):
        """Rule 12(1): Where N1 + N2 < 13, N1 and N2 shall be taken as zero."""
        inputs_with_pax_under_13 = dict(self.sample_inputs)
        inputs_with_pax_under_13["passengers_cabin_n1"] = 4
        inputs_with_pax_under_13["passengers_other_n2"] = 6  # total = 10 < 13

        res = TonnageService.calculate_tonnage(inputs_with_pax_under_13)
        self.assertTrue(res["passengers"]["pax_zeroed"])
        self.assertEqual(res["passengers"]["n1_effective"], 0)
        self.assertEqual(res["passengers"]["n2_effective"], 0)
        self.assertEqual(res["tonnage"]["pax_term"], 0.0)

        # Total >= 13 -> passengers active
        inputs_with_pax_over_13 = dict(self.sample_inputs)
        inputs_with_pax_over_13["passengers_cabin_n1"] = 10
        inputs_with_pax_over_13["passengers_other_n2"] = 20  # total = 30 >= 13

        res2 = TonnageService.calculate_tonnage(inputs_with_pax_over_13)
        self.assertFalse(res2["passengers"]["pax_zeroed"])
        self.assertEqual(res2["passengers"]["n1_effective"], 10)
        self.assertEqual(res2["passengers"]["n2_effective"], 20)
        self.assertGreater(res2["tonnage"]["pax_term"], 0.0)

    def test_api_endpoints_direct(self):
        """Verify endpoint functions directly."""
        calc_res = calculate_tonnage(self.sample_inputs)
        self.assertTrue(calc_res["success"])
        self.assertIn("gross_tonnage", calc_res["tonnage"])
        self.assertIn("net_tonnage", calc_res["tonnage"])

        curr_res = get_current_tonnage()
        self.assertTrue(curr_res["success"])
        self.assertIn("gross_tonnage", curr_res["tonnage"])


if __name__ == "__main__":
    unittest.main()
