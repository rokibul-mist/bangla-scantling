import unittest
import json
import os
from app.services.pdf.app_form_pdf_service import generate_application_form_pdf, parse_audit_page_items, get_calc_lookup

class TestApplicationFormLogic(unittest.TestCase):
    def setUp(self):
        with open('app/saved_state.json', 'r', encoding='utf-8') as f:
            self.state = json.load(f)
        if 'dashboard_inputs' not in self.state:
            self.state['dashboard_inputs'] = {}
        self.state['dashboard_inputs']['lbp'] = 69.85
        self.state['dashboard_inputs']['breadth'] = 13.41
        from app.services.calculation_service import CalculationService
        self.state = CalculationService.compute_all_calculations(self.state)

    def test_item_resolution_values(self):
        lookup = get_calc_lookup(self.state)
        pages = self.state.get('application_form_pages', [])
        self.assertGreater(len(pages), 20, "Should have 24+ application form pages")

        all_items = {}
        for p_idx, page in enumerate(pages):
            items = parse_audit_page_items(page.get('content', []), lookup)
            for it in items:
                num = it.get('num')
                if num:
                    all_items[num] = it

        # Verify Item 18 Stern Frame Breadth
        self.assertIn('18', all_items)
        it18 = all_items['18']
        self.assertAlmostEqual(float(it18['lines'][0]['val']), 164.80, places=1)
        self.assertEqual(it18['lines'][0]['unit'], 'mm')

        # Verify Item 19 Stern Frame Thickness
        self.assertIn('19', all_items)
        it19 = all_items['19']
        self.assertAlmostEqual(float(it19['lines'][0]['val']), 44.92, places=1)
        self.assertEqual(it19['lines'][0]['unit'], 'mm')

        # Verify Item 20 Propeller Post Breadth
        self.assertIn('20', all_items)
        it20 = all_items['20']
        self.assertAlmostEqual(float(it20['lines'][0]['val']), 274.60, places=1)

        # Verify Item 21 Propeller Post Radius
        self.assertIn('21', all_items)
        it21 = all_items['21']
        self.assertAlmostEqual(float(it21['lines'][0]['val']), 44.92, places=1)

        # Verify Item 22 Propeller Post Thickness
        self.assertIn('22', all_items)
        it22 = all_items['22']
        self.assertAlmostEqual(float(it22['lines'][0]['val']), 74.83, places=1)

        # Verify Item 23 Rudder Post Bolts
        self.assertIn('23', all_items)
        it23 = all_items['23']
        self.assertEqual(it23['lines'][0]['val'], '4')
        self.assertEqual(it23['lines'][0]['unit'], 'bolts')

        # Verify Item 26 Heel Piece
        self.assertIn('26', all_items)
        it26 = all_items['26']
        self.assertEqual(it26['lines'][0]['val'], '1650')
        self.assertEqual(it26['lines'][0]['unit'], 'mm')

        # Verify Item 29 Keelsons
        self.assertIn('29', all_items)
        it29 = all_items['29']
        self.assertEqual(it29['lines'][0]['val'], '5')
        self.assertEqual(it29['lines'][0]['unit'], '…...Nos')

        # Verify Item 40 Pillar
        self.assertIn('40', all_items)
        it40 = all_items['40']
        self.assertAlmostEqual(float(it40['lines'][0]['val']), 101.60, places=1)
        self.assertEqual(it40['lines'][0]['unit'], 'mm')

        # Verify Item 72 Drainage pipe
        self.assertIn('72', all_items)
        it72 = all_items['72']
        self.assertEqual(it72['lines'][0]['val'], 'Sufficient')
        self.assertAlmostEqual(float(it72['lines'][2]['val']), 3.05, places=2)
        self.assertEqual(it72['lines'][2]['unit'], 'mm')

        # Verify Item 74 Super structure bulkhead
        self.assertIn('74', all_items)
        it74 = all_items['74']
        self.assertAlmostEqual(float(it74['lines'][0]['val']), 5.50, places=2)
        self.assertAlmostEqual(float(it74['lines'][2]['val']), 16.0, places=1)
        self.assertEqual(it74['lines'][2]['unit'], 'cm³')

        # Verify Item 76 Decks
        self.assertIn('76', all_items)
        it76 = all_items['76']
        self.assertIn(round(float(it76['lines'][0]['val']), 2), [5.99, 8.39])
        self.assertGreater(float(it76['lines'][4]['val']), 10.0)
        self.assertEqual(it76['lines'][4]['unit'], 'cm³')
        self.assertGreater(float(it76['lines'][6]['val']), 400.0)
        self.assertEqual(it76['lines'][6]['unit'], 'cm³')

        # Verify Item 86 Steering Chain & Rod
        self.assertIn('86', all_items)
        it86 = all_items['86']
        self.assertAlmostEqual(float(it86['lines'][0]['val']), 16.0, places=1)
        self.assertEqual(it86['lines'][0]['unit'], 'mm')
        self.assertAlmostEqual(float(it86['lines'][2]['val']), 18.2, places=1)
        self.assertEqual(it86['lines'][2]['unit'], 'mm')

        # Verify Item 87 Chain cable & ropes (no junk header rows)
        self.assertIn('87', all_items)
        it87 = all_items['87']
        self.assertTrue(it87['lines'][0]['val'].startswith('2 x '))
        self.assertEqual(it87['lines'][0]['unit'], 'kg')

        # Verify Item 90 Bulwark Plating
        self.assertIn('90', all_items)
        it90 = all_items['90']
        self.assertAlmostEqual(float(it90['lines'][0]['val']), 5.99, places=2)
        self.assertEqual(it90['lines'][0]['unit'], 'mm')

        # Verify Item 91 Chain Lockers
        self.assertIn('91', all_items)
        it91 = all_items['91']
        self.assertAlmostEqual(float(it91['lines'][0]['val']), 6.98, places=2)
        self.assertEqual(it91['lines'][0]['unit'], 'mm')

        # Verify Item 94 Mooring Equipment
        self.assertIn('94', all_items)
        it94 = all_items['94']
        self.assertEqual(it94['lines'][0]['val'], '8')
        self.assertEqual(it94['lines'][0]['unit'], 'Nos')

        # Verify Item 96 Bilge pumps count
        self.assertIn('96', all_items)
        it96 = all_items['96']
        self.assertEqual(it96['lines'][0]['val'], '2')
        self.assertEqual(it96['lines'][0]['unit'], 'nos')

        # Verify Item 103 Coaming Height
        self.assertIn('103', all_items)
        it103 = all_items['103']
        self.assertEqual(it103['lines'][0]['val'], '600')
        self.assertEqual(it103['lines'][0]['unit'], 'mm')

    def test_pdf_generation(self):
        pdf_bytes = generate_application_form_pdf(self.state)
        self.assertIsNotNone(pdf_bytes)
        self.assertGreater(len(pdf_bytes), 100000, "Generated PDF should be at least 100KB for 25 pages")
        self.assertTrue(pdf_bytes.startswith(b'%PDF'), "Should be a valid PDF document")

if __name__ == '__main__':
    unittest.main()
