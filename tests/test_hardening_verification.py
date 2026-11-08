"""
Test suite for Worker 2 hardening & edge-case robustness fixes:
1. Safe numerical conversions & zero/negative dimension fallbacks in LightshipService
2. Payload type guards in /api/save-state and /api/calculate (400 Bad Request)
3. StateService non-dict saved state resilience
4. RFC 6266 / RFC 5987 Content-Disposition non-ASCII header compliance
5. Project deliverable verification
"""

import os
import sys
import json
import unittest
import requests
import pymupdf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

BASE_URL = os.environ.get("TEST_BASE_URL", "http://127.0.0.1:8055")


class TestHardeningVerification(unittest.TestCase):

    def test_01_payload_type_guards_reject_non_dict(self):
        """Endpoints /api/calculate and /api/save-state must return 400 on non-dict bodies."""
        non_dict_payloads = [
            [1, 2, 3],
            "raw-string-body",
            12345,
            True,
        ]
        for p in non_dict_payloads:
            r_calc = requests.post(f"{BASE_URL}/api/calculate", json=p)
            self.assertEqual(r_calc.status_code, 400, f"/api/calculate failed to reject {p}")
            self.assertIn("Calculation payload must be a JSON object", r_calc.json().get("detail", ""))

            r_save = requests.post(f"{BASE_URL}/api/save-state", json=p)
            self.assertEqual(r_save.status_code, 400, f"/api/save-state failed to reject {p}")
            self.assertIn("State payload must be a JSON object", r_save.json().get("detail", ""))

    def test_02_lightship_safe_float_and_dimension_guards(self):
        """LightshipService handles null, empty string, unit strings, and negative dimensions without crash."""
        from app.services.lightship_service import LightshipService, _safe_float, _safe_int

        # Unit tests on helpers
        self.assertEqual(_safe_float(None, 12.0), 12.0)
        self.assertEqual(_safe_float("", 12.0), 12.0)
        self.assertEqual(_safe_float("invalid", 12.0), 12.0)
        self.assertEqual(_safe_float("14.5", 12.0), 14.5)
        self.assertEqual(_safe_float(14.5, 12.0), 14.5)

        self.assertEqual(_safe_int(None, 5), 5)
        self.assertEqual(_safe_int("", 5), 5)
        self.assertEqual(_safe_int("invalid", 5), 5)
        self.assertEqual(_safe_int("8", 5), 8)
        self.assertEqual(_safe_int(8.0, 5), 8)

        # Negative & zero dimensions in calculate_lightship
        poisoned_state = {
            "dashboard_inputs": {
                "loa": -100.0,
                "breadth": 0.0,
                "depth": -5.0,
                "t_keel": "",
                "t_bottom": None,
                "t_side": "12.0mm" # invalid float string
            },
            "calculation_brain": [],
            "lightship_plates": [
                {"sn": 1, "l": -50.0, "b": 0.0, "qty": -3}
            ],
            "lightship_angles": [
                {"sn": 1, "length": -10.0, "qty": -1}
            ]
        }
        res = LightshipService.calculate_lightship(poisoned_state, {}, False)
        self.assertIn("plates", res)
        self.assertIn("angles", res)
        self.assertIn("summary", res)
        self.assertGreater(res["summary"]["total_steel_tonne"], 0.0)
        self.assertGreater(res["summary"]["total_lightship_tonne"], 0.0)

    def test_03_state_service_non_dict_saved_resilience(self):
        """StateService.get_initial_state gracefully handles corrupted non-dict saved states."""
        from app.services.state_service import StateService

        class MockRepo:
            def get_raw_data(self):
                with open("app/saved_state.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            def get_saved_state(self):
                return ["corrupt", "list", "instead", "of", "dict"]

        svc = StateService(MockRepo())
        master = svc.get_initial_state()
        self.assertIsInstance(master, dict)
        self.assertIn("dashboard_inputs", master)

    def test_04_rfc_6266_content_disposition_bengali_vessel_name(self):
        """Non-ASCII Bengali vessel names must generate RFC 6266 / RFC 5987 headers without latin-1 crash."""
        with open("app/saved_state.json", "r", encoding="utf-8") as f:
            state = json.load(f)
        state["dashboard_inputs"]["vessel_name"] = "বাংলা জাহাজ এমভি-০১"

        endpoints = [
            "/api/v1/pdf/detail-calc",
            "/api/v1/pdf/lightship",
            "/api/v1/pdf/application-form"
        ]
        for ep in endpoints:
            r = requests.post(f"{BASE_URL}{ep}", json=state)
            self.assertEqual(r.status_code, 200, f"{ep} failed with Bengali vessel name")
            cd = r.headers.get("content-disposition", "")
            self.assertIn("filename*=", cd)
            self.assertIn("UTF-8''", cd)
            # Ensure header is strictly ASCII encodable
            cd.encode("ascii")

    def test_05_project_root_deliverables_integrity(self):
        """Verify all 4 deliverable files in root exist with correct page counts and dimensions."""
        root_dir = os.path.dirname(os.path.dirname(__file__))

        # 1. Detail Calculation Booklet
        detail_path = os.path.join(root_dir, "Detail_Calculation_Booklet.pdf")
        self.assertTrue(os.path.exists(detail_path))
        doc1 = pymupdf.open(detail_path)
        self.assertEqual(len(doc1), 10, "Detail_Calculation_Booklet.pdf must be exactly 10 pages")
        doc1.close()

        # 2. Lightship Booklet
        ls_path = os.path.join(root_dir, "Lightship.pdf")
        self.assertTrue(os.path.exists(ls_path))
        doc2 = pymupdf.open(ls_path)
        self.assertEqual(len(doc2), 2, "Lightship.pdf must be exactly 2 pages")
        doc2.close()

        # 3. Application Form Booklet
        app_path = os.path.join(root_dir, "Application_Form_Booklet.pdf")
        self.assertTrue(os.path.exists(app_path))
        doc3 = pymupdf.open(app_path)
        self.assertEqual(len(doc3), 25, "Application_Form_Booklet.pdf must be exactly 25 pages")
        doc3.close()

        # 4. Lightship Preview PNG
        png_path = os.path.join(root_dir, "lightship_preview.png")
        self.assertTrue(os.path.exists(png_path))
        self.assertGreater(os.path.getsize(png_path), 100000)


if __name__ == "__main__":
    unittest.main()
