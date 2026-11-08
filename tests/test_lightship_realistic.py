import unittest
import json
from app.services.calculation_service import CalculationService
from app.services.lightship_service import LightshipService


class TestRealisticLightship(unittest.TestCase):
    def setUp(self):
        with open('app/saved_state.json', 'r', encoding='utf-8') as f:
            self.state = json.load(f)

    def test_realistic_weights_and_deadweight(self):
        res = CalculationService.compute_all_calculations(self.state)
        summary = res.get('lightship_summary', {})
        
        plate_t = summary.get('total_plate_tonne', 0)
        angle_t = summary.get('total_angle_tonne', 0)
        steel_t = summary.get('total_steel_tonne', 0)
        lwt_t = summary.get('total_lightship_tonne', 0)

        # Net steel should be between 400t and 650t
        self.assertGreater(steel_t, 400.0)
        self.assertLess(steel_t, 650.0)

        # Lightship should be between 650t and 1000t (realistic for 3000t displacement vessel)
        self.assertGreater(lwt_t, 650.0)
        self.assertLess(lwt_t, 1000.0)

        # Total steel = plate + angle
        self.assertAlmostEqual(steel_t, plate_t + angle_t, places=2)

        # Outfitting should be exactly 56% of net steel
        outfit_total = (
            summary.get('allowance_tonne', 0) +
            summary.get('outfit_tonne', 0) +
            summary.get('piping_tonne', 0) +
            summary.get('electrical_tonne', 0) +
            summary.get('accom_tonne', 0) +
            summary.get('misc_tonne', 0)
        )
        self.assertAlmostEqual(outfit_total, steel_t * 0.56, places=1)
        self.assertAlmostEqual(lwt_t, steel_t * 1.56, places=1)

    def test_clean_element_names(self):
        res = CalculationService.compute_all_calculations(self.state)
        plates = res.get('lightship_plates', [])
        angles = res.get('lightship_angles', [])

        self.assertEqual(len(plates), 19)
        self.assertEqual(len(angles), 21)

        # No dimensions or rule citations embedded in names
        for p in plates:
            name = p.get('name', '')
            self.assertNotIn('mm', name.lower())
            self.assertNotIn('rule', name.lower())
            self.assertNotIn('table', name.lower())

        for a in angles:
            name = a.get('name', '')
            self.assertNotIn('mm', name.lower())
            self.assertNotIn('rule', name.lower())
            self.assertNotIn('table', name.lower())


if __name__ == '__main__':
    unittest.main()
