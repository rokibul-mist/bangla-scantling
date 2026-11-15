"""
Unit Tests for Lines Plan & Offset Table Module.
Validates parametric generation, hydrostatics integration, CAD DXF and Excel export,
and tabular offset file parsing.
"""

import unittest
from app.services.lines_plan_service import LinesPlanService
from app.domain.models.lines_plan import ReferenceFrame, DesignGrid


class TestLinesPlanModule(unittest.TestCase):

    def test_01_parametric_hull_generation(self):
        """Verify parametric hull generation for inland vessels."""
        data = LinesPlanService.generate_parametric_offsets(
            lbp=69.85,
            beam=13.41,
            depth=5.18,
            draft=4.00,
            cb=0.75,
            cm=0.98,
            preset_type="general_cargo"
        )
        self.assertIsNotNone(data)
        self.assertEqual(len(data.design_grid.stations), 11)
        self.assertGreaterEqual(len(data.design_grid.waterlines), 6)
        self.assertGreaterEqual(len(data.design_grid.buttocks), 3)
        self.assertIn("AP", data.half_breadths)
        self.assertIn("5", data.half_breadths)

    def test_02_hydrostatics_integration(self):
        """Verify Simpson's / composite trapezoidal integration yields realistic hydrostatics."""
        data = LinesPlanService.generate_parametric_offsets(
            lbp=69.85,
            beam=13.41,
            depth=5.18,
            draft=4.00,
            cb=0.75,
            cm=0.98
        )
        hydro = data.hydrostatics
        self.assertIsNotNone(hydro)
        # For a ~70m inland vessel at 4m draft:
        # Block coefficient Cb ~ 0.70 to 0.85
        self.assertGreaterEqual(hydro.block_coefficient_cb, 0.65)
        self.assertLessEqual(hydro.block_coefficient_cb, 0.88)
        # Displacement ~ 2,400 to 3,200 tonnes
        self.assertGreater(hydro.displacement_tonnes, 2000.0)
        self.assertLess(hydro.displacement_tonnes, 3500.0)
        # LCB near midship (~45% to 55% of LBP)
        self.assertGreater(hydro.lcb_percent_lbp, 45.0)
        self.assertLess(hydro.lcb_percent_lbp, 56.0)
        # Transverse KM > draft
        self.assertGreater(hydro.kmt_m, 4.0)

    def test_03_all_preset_types(self):
        """Verify generation across all 4 vessel hull presets."""
        presets = ["general_cargo", "oil_tanker", "passenger_launch", "sand_barge"]
        for p in presets:
            data = LinesPlanService.generate_parametric_offsets(
                lbp=50.0,
                beam=10.0,
                depth=3.5,
                draft=2.5,
                preset_type=p
            )
            self.assertEqual(data.preset_type, p)
            self.assertGreater(data.hydrostatics.displacement_tonnes, 0.0)

    def test_04_dxf_export(self):
        """Verify AutoCAD DXF binary generation."""
        data = LinesPlanService.generate_parametric_offsets(69.85, 13.41, 5.18, 4.00)
        dxf_bytes = LinesPlanService.export_to_dxf(data)
        self.assertGreater(len(dxf_bytes), 5000)
        self.assertTrue(dxf_bytes.startswith(b"999\n") or b"SECTION" in dxf_bytes)

    def test_05_excel_export(self):
        """Verify Excel workbook Table of Offsets generation."""
        data = LinesPlanService.generate_parametric_offsets(69.85, 13.41, 5.18, 4.00)
        xlsx_bytes = LinesPlanService.export_to_excel(data)
        self.assertGreater(len(xlsx_bytes), 2000)
        # Verify ZIP/XLSX magic bytes (PK..)
        self.assertTrue(xlsx_bytes.startswith(b"PK\x03\x04"))

    def test_06_csv_parsing(self):
        """Verify parsing of uploaded CSV offset table."""
        csv_text = """Station,WL 0.0,WL 1.0,WL 2.0,WL 3.0,WL 4.0
St 0,0.0,0.2,0.4,0.6,0.8
St 1,0.0,2.5,3.1,3.4,3.6
St 2,0.0,4.8,5.2,5.4,5.5
St 3,0.0,6.0,6.2,6.3,6.4
St 4,0.0,6.5,6.6,6.7,6.7
St 5,0.0,6.7,6.7,6.7,6.7
St 6,0.0,6.6,6.6,6.6,6.7
St 7,0.0,6.2,6.3,6.4,6.5
St 8,0.0,5.1,5.4,5.6,5.7
St 9,0.0,2.8,3.2,3.5,3.7
St 10,0.0,0.3,0.5,0.7,0.8
"""
        data = LinesPlanService.parse_uploaded_file(
            filename="my_lines.csv",
            content_bytes=csv_text.encode("utf-8")
        )
        self.assertEqual(len(data.design_grid.stations), 11)
        self.assertGreater(len(data.design_grid.waterlines), 2)
        self.assertGreater(data.hydrostatics.displacement_tonnes, 0.0)

    def test_07_maxsurf_file_detection(self):
        """Verify MAXSURF file format detection."""
        from app.services.maxsurf_service import MaxsurfService
        self.assertTrue(MaxsurfService.is_maxsurf_file("hull_design.msd", b"\x0b=A \x00\x00"))
        self.assertTrue(MaxsurfService.is_maxsurf_file("vessel.hmd", b"Hydromax model"))
        self.assertTrue(MaxsurfService.is_maxsurf_file("offsets.txt", b"MAXSURF Table of Offsets\nStation\tWL 0\tWL 1"))
        self.assertFalse(MaxsurfService.is_maxsurf_file("notes.txt", b"General notes about the vessel"))

    def test_08_maxsurf_msd_settings_detection(self):
        """Verify detection of Frame of Reference and Design Grid from MAXSURF .msd."""
        import os
        from app.services.maxsurf_service import MaxsurfService
        sample_msd = r"C:\Program Files\Bentley\Offshore\Maxsurf 2025\Automation Samples\Combined\HardChine.msd"
        if os.path.exists(sample_msd):
            with open(sample_msd, "rb") as f:
                content = f.read()
            data = LinesPlanService.parse_uploaded_file("HardChine.msd", content)
            self.assertIsNotNone(data.maxsurf_settings)
            self.assertTrue(data.maxsurf_settings.is_maxsurf)
            self.assertGreater(data.maxsurf_settings.lbp, 5.0)
            self.assertGreater(data.maxsurf_settings.grid_sections_count, 5)
            self.assertGreater(data.maxsurf_settings.draft, 0.1)
            self.assertGreater(data.hydrostatics.displacement_tonnes, 0.0)
        else:
            # Test native fallback parser with mock binary content
            mock_bytes = b"\x0b=A \x00\x00\x00\x00st 1\x00st 2\x00Hull\x00" + b"\x00" * 200
            data = LinesPlanService.parse_uploaded_file("TestModel.msd", mock_bytes)
            self.assertIsNotNone(data.maxsurf_settings)
            self.assertTrue(data.maxsurf_settings.is_maxsurf)
            self.assertGreater(data.maxsurf_settings.lbp, 0.0)


if __name__ == "__main__":
    unittest.main()
