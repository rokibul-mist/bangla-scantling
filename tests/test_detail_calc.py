import unittest
from app.services.calculation_service import CalculationService
from app.domain.calc.section_modulus import calc_stiffener_section

class TestDetailCalculation(unittest.TestCase):
    def test_stiffener_section_t_profile(self):
        # Center keelson: 1000x20 web, 350x35 flange (T-profile)
        res = calc_stiffener_section(
            bp=550.0, tp=13.0, hw=1000.0, tw=20.0, bf=350.0, tf=35.0, profile_type='T'
        )
        self.assertEqual(res['profile_type'], 'T')
        self.assertGreater(res['z_cm3'], 10000.0)
        self.assertGreater(res['yna'], 13.0)

    def test_stiffener_section_fb_profile(self):
        # Flat bar: 150x10, bf=0, tf=0
        res = calc_stiffener_section(
            bp=550.0, tp=12.0, hw=150.0, tw=10.0, bf=0.0, tf=0.0, profile_type='FB'
        )
        self.assertEqual(res['profile_type'], 'FB')
        self.assertEqual(res['af'], 0.0)
        # Depth should be tp + hw = 162
        self.assertEqual(res['ymax'], max(res['yna'], 162.0 - res['yna']))

    def test_sheet2_results_preserves_profile_type(self):
        state = {
            'dashboard_inputs': {
                'lbp': 69.85, 'breadth': 13.41, 'depth': 5.18, 'draft': 4.0,
                'frame_spacing': 550.0, 'route': 'Inland & bay crossing',
                'vessel_type': 'Cargo Vessel', 'hull_type': 'Single Hull'
            },
            'stiffener_custom_dims': {
                'stiff_centre_keelson': {
                    'profile_type': 'T', 'web_depth': 1000, 'web_thk': 20, 'flange_width': 350, 'flange_thk': 35
                },
                'stiff_main_frame': {
                    'profile_type': 'L', 'web_depth': 150, 'web_thk': 10, 'flange_width': 90, 'flange_thk': 10
                }
            }
        }
        res_state = CalculationService.compute_all_calculations(state)
        s2 = res_state.get('sheet2_results', [])
        keelson = next((item for item in s2 if item['member_id'] == 'stiff_centre_keelson'), None)
        self.assertIsNotNone(keelson)
        self.assertEqual(keelson['profile_type'], 'T')

        frame = next((item for item in s2 if item['member_id'] == 'stiff_main_frame'), None)
        self.assertIsNotNone(frame)
        self.assertEqual(frame['profile_type'], 'L')

    def test_app_form_mappings_and_pdf_generation(self):
        from app.domain.catalog.app_form_mappings import get_stiffener_app_form_info
        from app.services.pdf.detail_calc_pdf_service import generate_detail_calculation_booklet_pdf

        # Verify exact application form item mappings
        ck_info = get_stiffener_app_form_info('stiff_centre_keelson')
        self.assertEqual(ck_info['item_no'], '31')
        self.assertEqual(ck_info['rule'], 'Rule 23')
        self.assertEqual(ck_info['page'], 11)

        mf_info = get_stiffener_app_form_info('stiff_main_frame')
        self.assertEqual(mf_info['item_no'], '33')
        self.assertEqual(mf_info['rule'], 'Rule 25')
        self.assertEqual(mf_info['page'], 11)

        fl_info = get_stiffener_app_form_info('stiff_floor_single')
        self.assertEqual(fl_info['item_no'], '28')
        self.assertEqual(fl_info['rule'], 'Rule 22')

        db_info = get_stiffener_app_form_info('stiff_solid_floor')
        self.assertEqual(db_info['item_no'], '105')

        # Test PDF generator output
        state = {
            'dashboard_inputs': {
                'vessel_name': 'Test Carrier', 'lbp': 69.85, 'breadth': 13.41,
                'depth': 5.18, 'draft': 4.0, 'frame_spacing': 550.0
            },
            'sheet2_results': [
                {
                    'id': 1, 'member_id': 'stiff_centre_keelson', 'name': 'Centre Keelson',
                    'table_ref': 'Table 16', 'profile_type': 'T', 'plate_width': 550, 'plate_thk': 12,
                    'web_height': 500, 'web_thk': 12, 'flange_width': 500, 'flange_thk': 12,
                    'ap': 6600, 'aw': 6000, 'af': 6000, 'atot': 18600, 'yna': 253.742,
                    'ip': 405161239.54, 'iw': 125409173.78, 'if': 419065947.97, 'ina': 949636361.29,
                    'z_mm3': 3513813, 'z_cm3': 3513.81, 'rreq': 1480.88, 'margin': 2032.93, 'status': 'COMPLIANT'
                }
            ]
        }
        pdf_bytes = generate_detail_calculation_booklet_pdf(state)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 1000)

        import fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = "".join(page.get_text() for page in doc)
        
        # Verify Application Form reference is in the booklet
        self.assertIn("APPLICATION FORM: ITEM 31 (Rule 23)", text)
        self.assertIn("Item 31: Kilsons & Webs (Centre girder)", text)
        self.assertIn("CALCULATED SECTION MODULUS", text)
        # Verify the compliance evaluation header is removed from the sheets
        self.assertNotIn("SECTION MODULUS & COMPLIANCE EVALUATION", text)


    def test_corrected_interpolations_bottom_long_and_deck_web(self):
        state = {
            'dashboard_inputs': {
                'vessel_name': 'M.V. CROWN MARINERS',
                'vessel_type': 'Cargo Vessel',
                'hull_type': 'Double Bottom',
                'lbp': 69.85, 'breadth': 13.41, 'depth': 5.18, 'draft': 4.0,
                'frame_spacing': 550.0, 'route': 'Inland & bay crossing',
                'effective_kz': 1.25
            }
        }
        res_state = CalculationService.compute_all_calculations(state)
        s2 = res_state.get('sheet2_results', [])

        # Bottom Longitudinal must NOT inherit floor plate modulus of 2000+ cm3
        bot_long = next((it for it in s2 if it['member_id'] == 'stiff_bottom_longitudinal'), None)
        self.assertIsNotNone(bot_long)
        self.assertLess(bot_long['rreq'], 250.0)
        self.assertGreater(bot_long['rreq'], 100.0)
        self.assertIn("Table 66", bot_long.get('table_ref', ''))

        # Deck Web Beam must follow Rule 29 (2 x Z_beam)
        deck_beam = next((it for it in s2 if it['member_id'] == 'stiff_deck_beam'), None)
        deck_web = next((it for it in s2 if it['member_id'] == 'stiff_deck_web_beam'), None)
        self.assertIsNotNone(deck_beam)
        self.assertIsNotNone(deck_web)
        self.assertAlmostEqual(deck_web['rreq'], deck_beam['rreq'] * 2.0, places=1)

if __name__ == '__main__':
    unittest.main()
