"""
Unit and Integration Tests for Verification Module
"""

import unittest
import copy
from app.services.verification_service import VerificationService
from app.repositories.state_repository import StateRepository


class TestVerificationModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        repo = StateRepository()
        cls.state = repo.get_saved_state() or repo.get_state()

    def test_01_all_checks_pass_on_current_deliverables(self):
        """Current deliverables and state must pass 100% of statutory verification checks."""
        report = VerificationService.run_comprehensive_verification(state=self.state)
        self.assertEqual(report["overall_status"], "PASSED", f"Verification failed: {report['verdict']}")
        self.assertTrue(report["is_valid"])
        self.assertEqual(report["summary"]["failed_checks"], 0, f"Failed checks found: {report['all_checks']}")
        self.assertGreaterEqual(report["summary"]["total_checks"], 80)
        self.assertEqual(report["summary"]["pass_rate_pct"], 100.0)

    def test_02_detects_stiffener_section_modulus_mismatch(self):
        """Engine must immediately catch and fail if a stiffener section modulus is tampered with."""
        tampered_state = copy.deepcopy(self.state)
        # Tamper with web frame in sheet2_results (e.g. set to 999.99 instead of actual required)
        for s in tampered_state.get('sheet2_results', []):
            if s.get('member_id') == 'stiff_web_frame':
                s['rreq'] = 999.99
                break

        checks = VerificationService.verify_stiffeners_alignment(tampered_state)
        failed_checks = [c for c in checks if c.status == "FAIL"]
        self.assertGreater(len(failed_checks), 0, "Tampered web frame must trigger at least one failure")
        self.assertTrue(any("999.99" in c.message for c in failed_checks),
                        "Diagnostic message must explicitly highlight 999.99 mismatch")

    def test_03_detects_plate_thickness_mismatch(self):
        """Engine must detect discrepancy between Dashboard plate thickness input and Calculation Brain."""
        tampered_state = copy.deepcopy(self.state)
        tampered_state['dashboard_inputs']['t_keel'] = 99.0  # Intentional error

        checks = VerificationService.verify_plates_alignment(tampered_state)
        failed_checks = [c for c in checks if c.status == "FAIL"]
        self.assertGreater(len(failed_checks), 0, "Plate mismatch must trigger a failure")
        self.assertTrue(any("Keel Plate" in c.name for c in failed_checks))

    def test_04_detects_outfitting_allowance_distortion(self):
        """Engine must fail if statutory outfitting allowance ratio (1.56) is distorted."""
        tampered_state = copy.deepcopy(self.state)
        # Empty out angles to distort synthesis ratio
        tampered_state['lightship_angles'] = []

        checks = VerificationService.verify_lightship_synthesis(tampered_state)
        warn_or_fail = [c for c in checks if c.status in ("FAIL", "WARN")]
        self.assertGreater(len(warn_or_fail), 0)

    def test_05_detects_missing_deliverable_file(self):
        """Engine must report FAIL when checking a non-existent deliverable path."""
        checks = VerificationService.verify_deliverables_files(self.state, root_dir="/non/existent/path")
        failed = [c for c in checks if c.status == "FAIL"]
        self.assertGreaterEqual(len(failed), 4, "Must fail for all missing deliverable files")


if __name__ == "__main__":
    unittest.main()
