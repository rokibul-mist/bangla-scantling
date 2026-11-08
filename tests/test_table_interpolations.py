"""
Unit tests for statutory rule empirical table interpolations.
Tests bounding nodes, spacing corrections, 1D/2D/3D surface evaluations, and extrapolation.
"""
import unittest
from app.domain.rules.interpolations.registry import TableInterpolationRegistry
from app.domain.rules.interpolations.base_interpolator import BaseTableInterpolator


class TestTableInterpolations(unittest.TestCase):

    def setUp(self):
        self.inputs_standard = {
            "L": 65.0,
            "lbp": 65.0,
            "breadth": 11.5,
            "depth": 4.5,
            "draft": 3.2,
            "frame_spacing": 550.0,
            "effective_kt": 1.20,
            "effective_kz": 1.25,
            "cb": 0.82
        }
        self.inputs_large_extrapolated = {
            "L": 76.21,
            "lbp": 76.21,
            "breadth": 13.41,
            "depth": 5.18,
            "draft": 4.0,
            "frame_spacing": 600.0,
            "effective_kt": 1.40,
            "effective_kz": 1.40,
            "cb": 0.82
        }

    def test_mat_min_hull_rule_08(self):
        res = TableInterpolationRegistry.interpolate_member("mat_min_hull", self.inputs_large_extrapolated)
        self.assertIsNotNone(res)
        self.assertEqual(res.table_no, "Rule 8(1)")
        self.assertEqual(res.baseline, 4.0)
        # kt is 1.40 -> 4.0 * 1.40 = 5.60 mm
        self.assertAlmostEqual(res.rreq, 5.60, places=2)
        self.assertIn("4.0 mm × kt (1.40) = 5.60 mm", res.derivation_text)

    def test_keel_plate_table_01(self):
        res = TableInterpolationRegistry.interpolate_member("plate_keel", self.inputs_standard)
        self.assertIsNotNone(res)
        self.assertEqual(res.table_no, "Table 1")
        # For L=65m, baseline is halfway between 60m (7.5mm) and 70m (8.0mm) -> 7.75 mm
        self.assertAlmostEqual(res.baseline, 7.75, places=2)
        self.assertAlmostEqual(res.rreq, round(7.75 * 1.20, 2), places=2)
        self.assertFalse(res.extrapolated)

    def test_keel_width_table_01(self):
        res = TableInterpolationRegistry.interpolate_member("w_keel", self.inputs_standard)
        self.assertIsNotNone(res)
        # For L=65m, width is halfway between 1050 and 1100 -> 1075 mm
        self.assertAlmostEqual(res.baseline, 1075.0, places=1)
        self.assertAlmostEqual(res.rreq, 1075.0, places=1)

    def test_bottom_shell_table_02(self):
        res = TableInterpolationRegistry.interpolate_member("plate_bottom", self.inputs_standard)
        self.assertIsNotNone(res)
        self.assertEqual(res.table_no, "Table 2")
        # For L=65m, s=550mm, nodes are 60m (7.0mm) and 70m (7.5mm) -> 7.25 mm
        self.assertAlmostEqual(res.baseline, 7.25, places=2)
        self.assertAlmostEqual(res.rreq, round(7.25 * 1.20, 2), places=2)

    def test_spacing_correction_above_550(self):
        res = TableInterpolationRegistry.interpolate_member("plate_bottom", self.inputs_large_extrapolated)
        self.assertIsNotNone(res)
        # s=600mm -> factor = sqrt(600/550) = 1.044466
        self.assertGreater(res.spacing_correction, 1.0)
        self.assertTrue(res.extrapolated)

    def test_floors_3d_interpolation_table_13(self):
        res = TableInterpolationRegistry.interpolate_member("stiff_floor_single", self.inputs_large_extrapolated)
        self.assertIsNotNone(res)
        self.assertEqual(res.table_no, "Table 13")
        self.assertTrue(res.extrapolated)
        # For B=13.41 > 12.0m, Section Modulus extrapolates above 1600 cm3
        self.assertGreater(res.baseline, 1500.0)
        self.assertIn(res.unit, ["cm3", "cm³"])

    def test_side_frames_table_17(self):
        res = TableInterpolationRegistry.interpolate_member("stiff_side_frame", self.inputs_standard)
        self.assertIsNotNone(res)
        self.assertEqual(res.table_no, "Table 17")
        self.assertGreater(res.rreq, 100.0)
        self.assertIn(res.unit, ["cm3", "cm³"])

    def test_deck_beams_table_20(self):
        res = TableInterpolationRegistry.interpolate_member("stiff_deck_beam", self.inputs_standard)
        self.assertIsNotNone(res)
        self.assertEqual(res.table_no, "Table 20")
        self.assertIn(res.unit, ["cm3", "cm³"])

    def test_rudder_stock_dia_table_39(self):
        res = TableInterpolationRegistry.interpolate_member("rudder_stock_dia", self.inputs_standard)
        self.assertIsNotNone(res)
        self.assertIn("Table 39", res.table_no)
        self.assertGreater(res.rreq, 100.0)
        self.assertEqual(res.unit, "mm")

    def test_table_view_structure(self):
        res = TableInterpolationRegistry.interpolate_member("plate_bottom", self.inputs_standard)
        tv = res.table_view
        self.assertIsNotNone(tv)
        self.assertTrue(len(tv.headers) > 0)
        self.assertTrue(len(tv.rows) > 0)
        self.assertTrue(len(tv.active_row_indices) > 0)
        self.assertIsNotNone(tv.active_col_index)
        self.assertTrue(len(tv.bounding_cells) > 0)



    def test_center_keelson_multi_column_table_16(self):
        res = TableInterpolationRegistry.interpolate_member("stiff_centre_keelson", self.inputs_standard)
        self.assertIsNotNone(res)
        self.assertEqual(res.table_no, "Table 16")
        self.assertIn(res.unit, ["cm3", "cm³"])
        self.assertIsNotNone(res.components)
        self.assertEqual(len(res.components), 4)

        names = [c["name"] for c in res.components]
        self.assertIn("Web Plate Thickness", names)
        self.assertIn("Face Plate Sectional Area", names)
        self.assertIn("Face Plate Width", names)
        self.assertIn("Girder Section Modulus", names)

        # Check multi-column visualizer indices
        tv = res.table_view
        self.assertIsNotNone(tv)
        self.assertIsNotNone(tv.active_col_indices)
        self.assertIn(1, tv.active_col_indices)
        self.assertIn(2, tv.active_col_indices)
        self.assertIn(3, tv.active_col_indices)

    def test_side_keelson_multi_column_table_15(self):
        res = TableInterpolationRegistry.interpolate_member("stiff_side_keelson", self.inputs_standard)
        self.assertIsNotNone(res)
        self.assertEqual(res.table_no, "Table 15")
        self.assertIn(res.unit, ["cm3", "cm³"])
        self.assertIsNotNone(res.components)
        self.assertEqual(len(res.components), 3)

        names = [c["name"] for c in res.components]
        self.assertIn("Web Plate Thickness", names)
        self.assertIn("Face Plate Sectional Area", names)
        self.assertIn("Girder Section Modulus", names)

        # Check multi-column visualizer indices
        tv = res.table_view
        self.assertIsNotNone(tv)
        self.assertIsNotNone(tv.active_col_indices)
        self.assertIn(1, tv.active_col_indices)
        self.assertIn(2, tv.active_col_indices)

if __name__ == "__main__":
    unittest.main()
