import os
import sys
import unittest

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.domain.calc.section_modulus import calc_stiffener_section
from app.domain.calc.weight_calc import calc_plate_weight, calc_angle_weight, calc_lightship_allowances
from app.domain.rules.factors import evaluate_statutory_factors
from app.domain.rules.limits import evaluate_frame_spacing_limit, evaluate_collision_bulkhead_limit
from app.domain.catalog.structural_catalog import STRUCTURAL_MEMBERS, get_active_members
from app.services.calculation_service import CalculationService
from app.services.state_service import StateService
from app.services.pdf.app_form_pdf_service import generate_application_form_pdf
from app.services.pdf.detail_calc_pdf_service import generate_detail_calculation_pdf
from app.services.pdf.lightship_pdf_service import generate_lightship_pdf

class TestModularNavalArchitecture(unittest.TestCase):

    def test_section_modulus_with_attached_plate(self):
        # Stiffener with bp=550, tp=12, hw=150, tw=10, bf=100, tf=10
        res = calc_stiffener_section(bp=550, tp=12, hw=150, tw=10, bf=100, tf=10)
        self.assertGreater(res['z_cm3'], 100.0)
        self.assertGreater(res['ina'], 1e6)
        self.assertGreater(res['yna'], 12.0)
        
        # When plate thickness tp increases to 16mm, section modulus Z must increase
        res_thicker = calc_stiffener_section(bp=550, tp=16, hw=150, tw=10, bf=100, tf=10)
        self.assertGreater(res_thicker['z_cm3'], res['z_cm3'])

    def test_weight_calc_and_allowances(self):
        # 10m x 2m x 12mm plate
        p_res = calc_plate_weight(l_dim=10000, b_dim=2000, t=12, density=7850, qty=1)
        self.assertAlmostEqual(p_res['vol'], 0.24, places=4)
        self.assertAlmostEqual(p_res['weight_kg'], 1884.0, places=1)
        self.assertAlmostEqual(p_res['weight_tonne'], 1.884, places=3)

        # Allowances for 100 tonnes net steel
        allowances = calc_lightship_allowances(100.0)
        self.assertEqual(allowances['allowance_tonne'], 20.0) # 20%
        self.assertEqual(allowances['outfit_tonne'], 15.0)    # 15%
        self.assertEqual(allowances['piping_tonne'], 10.0)    # 10%
        self.assertEqual(allowances['electrical_tonne'], 3.0) # 3%
        self.assertEqual(allowances['accom_tonne'], 1.0)      # 1%
        self.assertEqual(allowances['misc_tonne'], 7.0)       # 7%
        self.assertEqual(allowances['total_lightship_tonne'], 156.0) # 1.56x Net Steel

    def test_factors_steel_old_1_40(self):
        kt, kz, desc = evaluate_statutory_factors({'hull_material': 'Steel (Old)', 'route': 'Inland & bay crossing'})
        self.assertEqual(kt, 1.40)
        self.assertEqual(kz, 1.40)
        self.assertIn("Steel (Old)", desc)

    def test_factors_bay_crossing(self):
        kt, kz, desc = evaluate_statutory_factors({'hull_material': 'Steel (Mild)', 'route': 'Inland & bay crossing'})
        self.assertEqual(kt, 1.20)
        self.assertEqual(kz, 1.25)

    def test_structural_catalog_dynamic_members(self):
        db_members = get_active_members('Double Bottom')
        dh_members = get_active_members('Double Hull')
        sh_members = get_active_members('Single Hull')

        self.assertEqual(len(db_members), 88)
        self.assertEqual(len(dh_members), 93)
        self.assertEqual(len(sh_members), 77)

    def test_all_3_pdf_generators(self):
        ss = StateService()
        state = ss.get_initial_state()

        pdf_app = generate_application_form_pdf(state)
        self.assertGreater(len(pdf_app), 50000)

        pdf_detail = generate_detail_calculation_pdf(state)
        self.assertGreater(len(pdf_detail), 150000)

        pdf_light = generate_lightship_pdf(state)
        self.assertGreater(len(pdf_light), 150000)

if __name__ == '__main__':
    unittest.main()
