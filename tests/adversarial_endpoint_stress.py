"""
Adversarial API & Endpoint Stress Test Suite for Bangladesh Scantling System.
Validates live endpoints on port 8055 against CORS preflight, malformed/partial/null
payloads, extreme numbers, concurrency, and data synchronization.
"""

import os
import sys
import json
import time
import shutil
import unittest
import requests
import pymupdf as fitz
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = os.environ.get("TEST_BASE_URL", "http://127.0.0.1:8055")
SAVED_STATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "saved_state.json")
BACKUP_STATE_PATH = SAVED_STATE_PATH + ".bak_challenger"


class TestAdversarialEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Verify server liveness
        try:
            r = requests.get(f"{BASE_URL}/api/initial-state", timeout=5)
            assert r.status_code == 200, f"Server returned {r.status_code}"
        except Exception as e:
            raise RuntimeError(f"Server at {BASE_URL} is not responding: {e}")

        # Ensure backup of saved_state.json exists
        if os.path.exists(SAVED_STATE_PATH) and not os.path.exists(BACKUP_STATE_PATH):
            shutil.copyfile(SAVED_STATE_PATH, BACKUP_STATE_PATH)

        # Load baseline valid state
        with open(SAVED_STATE_PATH, "r", encoding="utf-8") as f:
            cls.baseline_state = json.load(f)

    @classmethod
    def tearDownClass(cls):
        # Restore original saved_state.json if backup exists
        if os.path.exists(BACKUP_STATE_PATH):
            shutil.copyfile(BACKUP_STATE_PATH, SAVED_STATE_PATH)
            try:
                os.remove(BACKUP_STATE_PATH)
            except Exception:
                pass

    # =========================================================================
    # SUITE 1: Route Aliases & Canonical PDF Endpoints
    # =========================================================================
    def test_01_pdf_route_aliases_get(self):
        """Verify all required PDF GET endpoints return valid, uncorrupted PDFs."""
        get_endpoints = [
            ("/api/v1/pdf/detail-calc", 10, "Detail_Calculation_Booklet"),
            ("/api/pdf/detail-calc", 10, "Detail_Calculation_Booklet"),
            ("/api/pdf/detail-calculation/preview", 10, "Detail_Calculation_Booklet"),
            ("/api/v1/pdf/lightship", 2, "Lightship_Booklet"),
            ("/api/pdf/lightship", 2, "Lightship_Booklet"),
            ("/api/lightship/pdf", 2, "Lightship_Booklet"),
            ("/api/v1/pdf/application-form", 25, "Application_Form"),
            ("/api/pdf/application-form", 25, "Application_Form"),
            ("/api/application-form/pdf", 25, "Application_Form"),
        ]

        for path, expected_pages, name_key in get_endpoints:
            url = f"{BASE_URL}{path}"
            with self.subTest(url=url):
                r = requests.get(url, timeout=15)
                self.assertEqual(r.status_code, 200, f"Expected 200 for GET {path}, got {r.status_code}")
                self.assertIn("application/pdf", r.headers.get("content-type", ""))
                self.assertTrue(r.content.startswith(b"%PDF-"), f"Response for {path} lacks PDF magic bytes")

                # Parse with PyMuPDF
                doc = fitz.open(stream=r.content, filetype="pdf")
                self.assertEqual(len(doc), expected_pages, f"{path} expected {expected_pages} pages, got {len(doc)}")
                doc.close()

    def test_02_pdf_route_aliases_post(self):
        """Verify all required PDF POST snapshot endpoints return valid, uncorrupted PDFs."""
        post_endpoints = [
            ("/api/v1/pdf/detail-calc", 10),
            ("/api/pdf/detail-calc", 10),
            ("/api/pdf/detail-calculation/generate", 10),
            ("/api/v1/pdf/lightship", 2),
            ("/api/pdf/lightship", 2),
            ("/api/lightship/pdf", 2),
            ("/api/v1/pdf/application-form", 25),
            ("/api/pdf/application-form", 25),
            ("/api/application-form/pdf", 25),
        ]

        for path, expected_pages in post_endpoints:
            url = f"{BASE_URL}{path}"
            with self.subTest(url=url):
                r = requests.post(url, json=self.baseline_state, timeout=15)
                self.assertEqual(r.status_code, 200, f"Expected 200 for POST {path}, got {r.status_code}")
                self.assertIn("application/pdf", r.headers.get("content-type", ""))
                self.assertTrue(r.content.startswith(b"%PDF-"), f"Response for {path} lacks PDF magic bytes")

                doc = fitz.open(stream=r.content, filetype="pdf")
                self.assertEqual(len(doc), expected_pages, f"{path} expected {expected_pages} pages, got {len(doc)}")
                doc.close()

    # =========================================================================
    # SUITE 2: CORS Preflight & Origin Stress Testing
    # =========================================================================
    def test_03_cors_preflight_options(self):
        """Challenge CORS preflight OPTIONS handling across origins and custom headers."""
        test_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:8055",
            "http://127.0.0.1:3000",
            "https://shipyard-cad.internal.org",
            "https://evil-cross-origin.com",
            "null",
        ]
        target_paths = [
            "/api/v1/pdf/detail-calc",
            "/api/v1/pdf/lightship",
            "/api/v1/pdf/application-form",
            "/api/calculate",
            "/api/save-state",
            "/api/initial-state",
            "/api/saved-state",
        ]

        for path in target_paths:
            for origin in test_origins:
                url = f"{BASE_URL}{path}"
                headers = {
                    "Origin": origin,
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type, Authorization, X-Shipyard-Token, Accept",
                }
                r = requests.options(url, headers=headers, timeout=5)
                self.assertEqual(r.status_code, 200, f"OPTIONS {path} failed with status {r.status_code} for origin {origin}")
                allow_origin = r.headers.get("access-control-allow-origin")
                self.assertIsNotNone(allow_origin, f"Missing Access-Control-Allow-Origin header on {path}")
                self.assertTrue(allow_origin == "*" or allow_origin == origin, f"Unexpected allow-origin: {allow_origin}")
                self.assertIn("access-control-allow-methods", r.headers)

    # =========================================================================
    # SUITE 3: Empty JSON Object `{}` Stress Testing
    # =========================================================================
    def test_04_post_empty_json_body(self):
        """Adversarially challenge POST endpoints with empty JSON `{}` to ensure no unhandled 500."""
        endpoints = [
            ("/api/v1/pdf/detail-calc", "pdf"),
            ("/api/v1/pdf/lightship", "pdf"),
            ("/api/v1/pdf/application-form", "pdf"),
            ("/api/pdf/detail-calc", "pdf"),
            ("/api/calculate", "json"),
            ("/api/v1/calculate", "json"),
            ("/api/save-state", "json"),
            ("/api/v1/save-state", "json"),
        ]

        for path, resp_type in endpoints:
            url = f"{BASE_URL}{path}"
            with self.subTest(url=url):
                r = requests.post(url, json={}, timeout=15)
                # Must be 200 OK (graceful fallback to defaults) or a 4xx validation error, NOT an unhandled 500
                self.assertNotEqual(r.status_code, 500, f"Unhandled 500 server crash on {path} with empty JSON body!")
                self.assertEqual(r.status_code, 200, f"Expected graceful 200 with fallback for {path}, got {r.status_code}")

                if resp_type == "pdf":
                    self.assertIn("application/pdf", r.headers.get("content-type", ""))
                    doc = fitz.open(stream=r.content, filetype="pdf")
                    self.assertGreater(len(doc), 0)
                    doc.close()
                elif resp_type == "json":
                    data = r.json()
                    self.assertTrue(isinstance(data, dict))

    # =========================================================================
    # SUITE 4: Partial State & Missing Sections Fuzzing
    # =========================================================================
    def test_05_partial_state_fuzzing(self):
        """Verify server gracefully handles payloads with missing sections without crashing."""
        partial_payloads = [
            # Only dashboard_inputs
            {"dashboard_inputs": {"vessel_name": "Ghost Ship", "loa": 60.0, "breadth": 11.0, "depth": 4.5, "draft": 3.2, "frame_spacing": 500}},
            # Only calculation_brain
            {"calculation_brain": []},
            # Only lightship_plates
            {"lightship_plates": []},
            # Only lightship_angles
            {"lightship_angles": []},
            # Only stiffener_custom_dims
            {"stiffener_custom_dims": {"stiff_main_frame": {"web_depth": 200, "web_thk": 12}}},
            # Minimal single key
            {"vessel_type": "Oil Tanker"},
        ]

        target_endpoints = [
            "/api/v1/pdf/detail-calc",
            "/api/v1/pdf/lightship",
            "/api/v1/pdf/application-form",
            "/api/calculate",
        ]

        for path in target_endpoints:
            for i, payload in enumerate(partial_payloads):
                url = f"{BASE_URL}{path}"
                with self.subTest(url=url, payload_idx=i):
                    r = requests.post(url, json=payload, timeout=15)
                    self.assertNotEqual(r.status_code, 500, f"Unhandled 500 on {path} with partial payload #{i}: {payload}")
                    self.assertEqual(r.status_code, 200, f"Expected 200 OK for {path} with partial payload #{i}")

    # =========================================================================
    # SUITE 5: Null Fields & Type Boundary Fuzzing
    # =========================================================================
    def test_06_null_fields_and_type_boundaries(self):
        """Adversarially inject null and empty strings into numerical fields."""
        poisoned_state = json.loads(json.dumps(self.baseline_state))
        poisoned_state["dashboard_inputs"]["loa"] = None
        poisoned_state["dashboard_inputs"]["lbp"] = ""
        poisoned_state["dashboard_inputs"]["breadth"] = None
        poisoned_state["dashboard_inputs"]["depth"] = None
        poisoned_state["dashboard_inputs"]["draft"] = None
        poisoned_state["dashboard_inputs"]["frame_spacing"] = None
        poisoned_state["dashboard_inputs"]["cb"] = None
        poisoned_state["dashboard_inputs"]["t_bottom"] = None
        poisoned_state["dashboard_inputs"]["t_side"] = ""

        endpoints = [
            "/api/v1/pdf/detail-calc",
            "/api/v1/pdf/lightship",
            "/api/v1/pdf/application-form",
            "/api/calculate",
        ]

        for path in endpoints:
            url = f"{BASE_URL}{path}"
            with self.subTest(url=url):
                r = requests.post(url, json=poisoned_state, timeout=15)
                self.assertNotEqual(r.status_code, 500, f"Unhandled 500 on {path} with null inputs!")
                self.assertEqual(r.status_code, 200, f"Endpoint {path} failed to handle null inputs gracefully (got {r.status_code})")

    # =========================================================================
    # SUITE 6: Extreme Numerical Values (Zero, Negative, Extreme Large)
    # =========================================================================
    def test_07_extreme_numerical_values(self):
        """Stress-test numerical boundaries: zero, negative, extreme large."""
        test_cases = [
            # Zeros
            {"loa": 0.0, "lbp": 0.0, "breadth": 0.0, "depth": 0.0, "draft": 0.0, "frame_spacing": 0.0, "cb": 0.0},
            # Negatives
            {"loa": -50.0, "lbp": -45.0, "breadth": -10.0, "depth": -4.0, "draft": -3.0, "frame_spacing": -500.0, "cb": -0.7},
            # Extremely Large
            {"loa": 100000.0, "lbp": 95000.0, "breadth": 50000.0, "depth": 20000.0, "draft": 15000.0, "frame_spacing": 10000.0, "cb": 0.99},
            # Extremely Small Sub-millimeter
            {"loa": 0.001, "lbp": 0.001, "breadth": 0.001, "depth": 0.001, "draft": 0.001, "frame_spacing": 0.001, "cb": 0.5},
        ]

        endpoints = [
            "/api/v1/pdf/detail-calc",
            "/api/v1/pdf/lightship",
            "/api/v1/pdf/application-form",
            "/api/calculate",
        ]

        for path in endpoints:
            for idx, tc in enumerate(test_cases):
                extreme_state = json.loads(json.dumps(self.baseline_state))
                extreme_state["dashboard_inputs"].update(tc)
                url = f"{BASE_URL}{path}"
                with self.subTest(url=url, case=idx):
                    r = requests.post(url, json=extreme_state, timeout=15)
                    self.assertNotEqual(r.status_code, 500, f"Unhandled 500 on {path} with extreme case #{idx}: {tc}")
                    self.assertEqual(r.status_code, 200, f"Expected 200 OK for {path} with extreme case #{idx}")

    # =========================================================================
    # SUITE 7: State Persistence & Roundtrip Lifecycle
    # =========================================================================
    def test_08_state_persistence_and_sync(self):
        """Verify initial-state, save-state, saved-state, and calculate roundtrips."""
        # 1. Fetch initial state
        r_init = requests.get(f"{BASE_URL}/api/initial-state", timeout=5)
        self.assertEqual(r_init.status_code, 200)
        init_data = r_init.json()
        self.assertIn("dashboard_inputs", init_data)
        self.assertIn("calculation_brain", init_data)
        self.assertIn("lightship_summary", init_data)

        # 2. Call calculate with custom frame spacing
        calc_payload = json.loads(json.dumps(self.baseline_state))
        calc_payload["dashboard_inputs"]["frame_spacing"] = 620.0
        r_calc = requests.post(f"{BASE_URL}/api/calculate", json=calc_payload, timeout=5)
        self.assertEqual(r_calc.status_code, 200)
        calc_res = r_calc.json()
        self.assertEqual(calc_res["dashboard_inputs"]["frame_spacing"], 620.0)
        # Check attached plate width in sheet2_results
        first_sheet = calc_res["sheet2_results"][0]
        self.assertEqual(first_sheet["plate_width"], 620.0)

        # 3. Save state test
        test_save = json.loads(json.dumps(self.baseline_state))
        test_save["dashboard_inputs"]["vessel_name"] = "STRESS TEST SHIP"
        r_save = requests.post(f"{BASE_URL}/api/save-state", json=test_save, timeout=5)
        self.assertEqual(r_save.status_code, 200)

        # 4. Read back saved state
        r_read = requests.get(f"{BASE_URL}/api/saved-state", timeout=5)
        self.assertEqual(r_read.status_code, 200)
        saved_data = r_read.json()
        self.assertTrue(saved_data.get("has_saved"))
        self.assertEqual(saved_data["state"]["dashboard_inputs"]["vessel_name"], "STRESS TEST SHIP")

    # =========================================================================
    # SUITE 8: High Concurrency / Burst Stress Testing
    # =========================================================================
    def test_09_concurrent_burst_stress(self):
        """Fire 30 concurrent asynchronous requests to verify thread safety and responsiveness under burst load."""
        requests_list = [
            ("GET", f"{BASE_URL}/api/v1/pdf/detail-calc", None),
            ("POST", f"{BASE_URL}/api/v1/pdf/detail-calc", self.baseline_state),
            ("GET", f"{BASE_URL}/api/v1/pdf/lightship", None),
            ("POST", f"{BASE_URL}/api/v1/pdf/lightship", self.baseline_state),
            ("GET", f"{BASE_URL}/api/v1/pdf/application-form", None),
            ("POST", f"{BASE_URL}/api/v1/pdf/application-form", self.baseline_state),
            ("GET", f"{BASE_URL}/api/initial-state", None),
            ("POST", f"{BASE_URL}/api/calculate", self.baseline_state),
        ] * 4  # 32 requests in total

        def make_req(req_tuple):
            method, url, payload = req_tuple
            start = time.time()
            if method == "GET":
                res = requests.get(url, timeout=20)
            else:
                res = requests.post(url, json=payload, timeout=20)
            elapsed = time.time() - start
            return method, url, res.status_code, len(res.content), elapsed

        results = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(make_req, r) for r in requests_list]
            for f in as_completed(futures):
                results.append(f.result())

        for method, url, status, content_len, elapsed in results:
            self.assertEqual(status, 200, f"Burst request {method} {url} failed with status {status}")
            self.assertGreater(content_len, 0, f"Empty response on burst request {method} {url}")


if __name__ == "__main__":
    unittest.main()
