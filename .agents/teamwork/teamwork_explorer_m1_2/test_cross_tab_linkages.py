import os
import sys
import json
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.services.calculation_service import CalculationService
from app.services.pdf.app_form_pdf_service import get_calc_lookup, resolve_audit_item_line, ITEM_TO_CALC_ID

class TestCrossTabLinkages(unittest.TestCase):

    def setUp(self):
        with open('app/saved_state.json', 'r', encoding='utf-8') as f:
            self.state = json.load(f)

    def test_dashboard_to_calc_brain_and_limits(self):
        # 1. Base calculations
        res = CalculationService.compute_all_calculations(self.state)
        brain = {m['id']: m for m in res['calculation_brain']}
        
        # Check frame spacing limit: 450 + 2 * lbp = 450 + 2 * 69.85 = 589.70 mm
        fs_limit = brain['frame_spacing_limit']
        self.assertEqual(fs_limit['rreq'], 589.70)
        self.assertEqual(fs_limit['dact'], 550.0)
        self.assertEqual(fs_limit['status'], 'COMPLIANT')

        # 2. Modify LBP to 80.0m -> limit should update to 450 + 2 * 80 = 610.0 mm
        mod_state = json.loads(json.dumps(self.state))
        mod_state['dashboard_inputs']['lbp'] = 80.0
        res_mod = CalculationService.compute_all_calculations(mod_state)
        brain_mod = {m['id']: m for m in res_mod['calculation_brain']}
        self.assertEqual(brain_mod['frame_spacing_limit']['rreq'], 610.0)

    def test_attached_plate_linkage_to_section_modulus(self):
        # 1. Base side frame section modulus
        res1 = CalculationService.compute_all_calculations(self.state)
        sheet2_map1 = {s['member_id']: s for s in res1['sheet2_results']}
        side_frame1 = sheet2_map1['stiff_main_frame']
        
        self.assertEqual(side_frame1['plate_width'], 550.0)
        self.assertEqual(side_frame1['plate_thk'], 12.0) # welded to t_side = 12mm
        z1 = side_frame1['z_cm3']

        # 2. Increase t_side to 16mm in Dashboard inputs -> section modulus must increase
        mod_state = json.loads(json.dumps(self.state))
        mod_state['dashboard_inputs']['t_side'] = 16.0
        mod_state['dashboard_inputs']['plate_side'] = 16.0
        res2 = CalculationService.compute_all_calculations(mod_state)
        sheet2_map2 = {s['member_id']: s for s in res2['sheet2_results']}
        side_frame2 = sheet2_map2['stiff_main_frame']

        self.assertEqual(side_frame2['plate_thk'], 16.0)
        z2 = side_frame2['z_cm3']
        self.assertGreater(z2, z1)

        # 3. Increase frame spacing to 600mm -> plate_width updates and Z increases
        mod_state['dashboard_inputs']['frame_spacing'] = 600.0
        res3 = CalculationService.compute_all_calculations(mod_state)
        sheet2_map3 = {s['member_id']: s for s in res3['sheet2_results']}
        side_frame3 = sheet2_map3['stiff_main_frame']

        self.assertEqual(side_frame3['plate_width'], 600.0)
        z3 = side_frame3['z_cm3']
        self.assertGreater(z3, z2)

    def test_lightship_allowances_and_totals(self):
        res = CalculationService.compute_all_calculations(self.state)
        summary = res['lightship_summary']

        net_steel = summary['total_steel_tonne']
        plate_t = summary['total_plate_tonne']
        angle_t = summary['total_angle_tonne']
        lightship_t = summary['total_lightship_tonne']

        # Check net steel sums: 328.574 + 163.677 = 492.251
        self.assertAlmostEqual(plate_t, 328.574, places=2)
        self.assertAlmostEqual(angle_t, 163.677, places=2)
        self.assertAlmostEqual(net_steel, 492.251, places=2)

        # Check outfitting allowances: 20% + 15% + 10% + 3% + 1% + 7% = 56%
        self.assertAlmostEqual(summary['allowance_tonne'], round(net_steel * 0.20, 3), places=2)
        self.assertAlmostEqual(summary['outfit_tonne'], round(net_steel * 0.15, 3), places=2)
        self.assertAlmostEqual(summary['piping_tonne'], round(net_steel * 0.10, 3), places=2)
        self.assertAlmostEqual(summary['electrical_tonne'], round(net_steel * 0.03, 3), places=2)
        self.assertAlmostEqual(summary['accom_tonne'], round(net_steel * 0.01, 3), places=2)
        self.assertAlmostEqual(summary['misc_tonne'], round(net_steel * 0.07, 3), places=2)

        # Total Lightship = Net Steel * 1.56 = 767.911
        self.assertAlmostEqual(lightship_t, 767.911, places=2)
        self.assertAlmostEqual(lightship_t, net_steel * 1.56, places=1)

    def test_application_form_audit_item_linkages(self):
        res = CalculationService.compute_all_calculations(self.state)
        lookup = get_calc_lookup(res)

        # Item 8: Keel Plate -> plate_keel (12mm)
        req, prov, unit, is_na = resolve_audit_item_line('8', 'Keel Plate', 0, 'As per rule', '', 'mm', lookup)
        self.assertFalse(is_na)
        self.assertEqual(float(prov), 12.0)

        # Item 10: Main Frame -> stiff_main_frame (Section Modulus cm³)
        req10, prov10, unit10, is_na10 = resolve_audit_item_line('10', 'Main Frame', 0, 'As per calculation', '', 'cm³', lookup)
        self.assertFalse(is_na10)
        self.assertEqual(unit10, 'cm³')
        self.assertGreater(float(prov10), 50.0)

        # Item 15: Single Hull -> N/A
        req15, prov15, unit15, is_na15 = resolve_audit_item_line('15', 'Deck Plating Inner Bottom', 0, 'Rule', '', 'mm', lookup)
        self.assertTrue(is_na15)
        self.assertEqual(req15, 'N/A')

        # If Double Bottom: Item 15 is active and displays plate_inner_bottom
        res_db = json.loads(json.dumps(res))
        res_db['dashboard_inputs']['hull_type'] = 'Double Bottom'
        res_db['dashboard_inputs']['t_inner_bottom'] = 14.0
        lookup_db = get_calc_lookup(res_db)
        req15_db, prov15_db, unit15_db, is_na15_db = resolve_audit_item_line('15', 'Deck Plating Inner Bottom', 0, 'Rule', '', 'mm', lookup_db)
        self.assertFalse(is_na15_db)
        self.assertEqual(float(prov15_db), 14.0)

if __name__ == '__main__':
    unittest.main()
