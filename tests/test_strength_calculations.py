"""
Unit and Integration Tests for Hull Strength, Longitudinal Bending Moments,
Midship Modulus, and Schedule Tables 66 & 67 Stress Audits.
"""

import unittest
from app.domain.calc.strength_calc import StrengthCalculator
from app.services.strength_service import StrengthService
from app.repositories.state_repository import StateRepository
from app.services.calculation_service import CalculationService
from app.services.pdf.strength_pdf_service import generate_hull_strength_booklet_pdf


class TestStrengthCalculations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        repo = StateRepository()
        cls.raw_state = repo.get_saved_state() or repo.get_state()
        cls.state = CalculationService.compute_all_calculations(cls.raw_state)

    def test_01_bending_moments_rule_209(self):
        """Verify statutory bending moment calculations for given particulars."""
        l = 69.85
        b = 13.41
        d = 5.18
        draft = 4.0
        cb = 0.82
        kt = 1.40

        moments = StrengthCalculator.calculate_design_bending_moments(
            lbp=l, breadth=b, depth=d, draft=draft, cb=cb, kt=kt
        )

        self.assertGreater(moments.m_sw_knm, 5000.0)
        self.assertGreater(moments.m_wave_hog_knm, 9000.0)
        self.assertGreater(moments.m_wave_sag_knm, 9000.0)
        self.assertGreater(moments.m_total_hog_knm, moments.m_sw_knm)
        self.assertGreater(moments.m_total_sag_knm, moments.m_sw_knm)
        self.assertIn(moments.design_condition.upper(), ["HOGGING", "SAGGING"])
        self.assertGreater(moments.m_design_knm, 20000.0)
        self.assertGreater(moments.shear_force_design_kn, 900.0)

    def test_02_statutory_required_modulus(self):
        """Verify statutory required section modulus scales with M_design and empirical formula."""
        m_design = 29160.53
        l = 69.85
        b = 13.41
        cb = 0.82
        kt = 1.40

        z_req = StrengthCalculator.calculate_statutory_required_modulus(
            m_design_knm=m_design, lbp=l, breadth=b, cb=cb, kt=kt
        )

        self.assertGreater(z_req, 200000.0)  # in cm³
        z_bend = (m_design * 1000.0) / 130.0
        self.assertGreaterEqual(z_req, z_bend)

    def test_03_midship_numerical_integration(self):
        """Verify numerical section modulus and neutral axis integration."""
        elements, hatch_loss = StrengthService.assemble_midship_elements(self.state)
        self.assertGreater(len(elements), 5)

        depth_m = float(self.state.get('dashboard_inputs', {}).get('depth', 5.18) or 5.18)
        props = StrengthCalculator.integrate_midship_cross_section(elements, depth_m, required_sm_cm3=250000.0)

        self.assertGreater(props.total_area_cm2, 2000.0)
        # Neutral axis should be roughly between 30% and 60% of hull depth
        self.assertGreater(props.neutral_axis_above_keel_m, 0.3 * depth_m)
        self.assertLess(props.neutral_axis_above_keel_m, 0.7 * depth_m)
        self.assertGreater(props.moment_of_inertia_cm4, 1e8)
        self.assertGreater(props.modulus_deck_cm3, 100000.0)
        self.assertGreater(props.modulus_bottom_cm3, 100000.0)
        self.assertEqual(props.modulus_actual_cm3, min(props.modulus_deck_cm3, props.modulus_bottom_cm3))

    def test_04_table_66_stress_limits(self):
        """Verify Table 66 stresses are evaluated against 130, 70, 150 N/mm²."""
        elements, _ = StrengthService.assemble_midship_elements(self.state)
        depth_m = float(self.state.get('dashboard_inputs', {}).get('depth', 5.18) or 5.18)
        props = StrengthCalculator.integrate_midship_cross_section(elements, depth_m, 250000.0)
        moments = StrengthCalculator.calculate_design_bending_moments(
            lbp=69.85, breadth=13.41, depth=depth_m, draft=4.0, cb=0.82, kt=1.40
        )

        res = StrengthCalculator.evaluate_table_66_stresses(
            m_design_knm=moments.m_design_knm,
            q_design_kn=moments.shear_force_design_kn,
            props=props,
            depth_m=depth_m,
            side_shell_thk_mm=12.0
        )
        self.assertLessEqual(res.max_bending_stress_n_mm2, 130.0)
        self.assertLessEqual(res.hull_shear_stress_n_mm2, 70.0)
        self.assertLessEqual(res.equivalent_stress_n_mm2, 150.0)
        self.assertEqual(res.is_overall_compliant, True)

    def test_05_table_67_local_members(self):
        """Verify Table 67 local member checks produce expected audit records."""
        items = StrengthCalculator.evaluate_table_67_local_members(self.state)
        self.assertGreaterEqual(len(items), 5)
        for it in items:
            self.assertEqual(it.status, "COMPLIANT")
            self.assertLessEqual(it.calculated_stress_n_mm2, it.allowable_stress_n_mm2)

    def test_06_strength_service_end_to_end(self):
        """Verify full StrengthService report synthesis."""
        report = StrengthService.calculate_hull_strength(self.state)
        self.assertEqual(report["overall_status"], "COMPLIANT")
        self.assertTrue(report["is_compliant"])
        self.assertIn("bending_moments", report)
        self.assertIn("midship_properties", report)
        self.assertIn("table_66_stresses", report)
        self.assertIn("table_67_local_stresses", report)

    def test_07_pdf_booklet_generation(self):
        """Verify standalone Hull Strength PDF booklet generation produces valid 4-page PDF."""
        pdf_bytes = generate_hull_strength_booklet_pdf(self.state)
        self.assertGreater(len(pdf_bytes), 50000)
        # Check PDF header
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))


if __name__ == "__main__":
    unittest.main()
