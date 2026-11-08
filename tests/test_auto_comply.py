"""
Unit tests for Auto-Comply optimization and standard profile catalogs.
"""

import unittest
from app.services.auto_comply.optimizer import ScantlingOptimizer
from app.services.auto_comply.service import AutoComplyService


class TestAutoComply(unittest.TestCase):

    def test_plate_thickness_rounding(self):
        # 5.60 mm required should round to standard commercial 7.0 mm (ensuring positive margin >= 0.4)
        t_opt = ScantlingOptimizer.find_compliant_plate_thickness(5.60)
        self.assertEqual(t_opt, 7.0)
        self.assertGreater(t_opt, 5.60)

        # 7.49 mm required should round to 8.0 mm
        t_opt2 = ScantlingOptimizer.find_compliant_plate_thickness(7.49)
        self.assertEqual(t_opt2, 8.0)

        # 9.49 mm required should round to 10.0 mm
        t_opt3 = ScantlingOptimizer.find_compliant_plate_thickness(9.49)
        self.assertEqual(t_opt3, 10.0)

    def test_stiffener_profile_selection(self):
        # Standard side frame requirement (e.g. Z = 180 cm3)
        res = ScantlingOptimizer.find_compliant_stiffener_profile(
            rreq_z=180.0, spacing=550.0, tp=10.0, preferred_type="L"
        )
        self.assertIsNotNone(res)
        self.assertGreaterEqual(res["prov_z"], 180.0)
        self.assertGreaterEqual(res["margin"], 0.0)
        self.assertIn("L", res["profile_type"])

    def test_heavy_stiffener_auto_upgrade_to_tee(self):
        # Heavy girder requirement (e.g. Z = 1200 cm3)
        res = ScantlingOptimizer.find_compliant_stiffener_profile(
            rreq_z=1200.0, spacing=550.0, tp=12.0, preferred_type="L"
        )
        self.assertIsNotNone(res)
        self.assertGreaterEqual(res["prov_z"], 1200.0)
        self.assertEqual(res["profile_type"], "T")

    def test_auto_comply_service_preview(self):
        dummy_state = {
            "dashboard_inputs": {
                "L": 69.85,
                "lbp": 69.85,
                "breadth": 13.41,
                "depth": 5.18,
                "draft": 4.0,
                "frame_spacing": 550.0,
                "spacing": 550.0,
                "effective_kt": 1.40,
                "effective_kz": 1.40,
                "t_bottom": 6.0,  # Deliberately non-compliant
                "t_side": 6.0     # Deliberately non-compliant
            },
            "custom_brain_dact": {},
            "stiffener_custom_dims": {}
        }
        preview = AutoComplyService.generate_compliance_preview(dummy_state)
        self.assertEqual(preview["status"], "success")
        self.assertGreater(len(preview["changes"]), 0)
        self.assertEqual(preview["new_compliant_count"], preview["total_items"])


if __name__ == "__main__":
    unittest.main()
