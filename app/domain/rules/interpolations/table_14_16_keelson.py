"""
Tables 14, 15, 16: Keelsons Quantity, Web Plate & Face Plate Interpolators.
Statutory Reference: Rules 22 - 24, Tables 14, 15, 16.
Governing parameters: Vessel Length L (m) and Breadth B (m).
"""

from typing import Dict, Any, List
from .base_interpolator import BaseTableInterpolator, InterpolationResult, TableViewData


class Table16CenterKeelsonInterpolator(BaseTableInterpolator):
    table_index = 15  # Table 16: Center Keelson Dimensions
    table_no_str = "Table 16"
    table_title = "Center Keelson Dimensions"
    ref_rule = "Rule 24, Table 16"
    default_unit = "cm3"

    L_NODES = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0]
    WEB_THK_NODES = [7.0, 7.5, 8.0, 8.5, 9.0, 9.5]
    FACE_AREA_NODES = [21.0, 27.0, 33.0, 39.0, 45.0, 51.0]
    FACE_WIDTH_NODES = [200.0, 230.0, 250.0, 275.0, 300.0, 320.0]
    BASELINE_SM = 1057.77  # Rule baseline equivalent Section Modulus in cm3

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "stiff_centre_keelson") -> InterpolationResult:
        lbp = float(inputs.get('lbp', inputs.get('L', 69.85)) or 69.85)
        kt = float(inputs.get('effective_kt', inputs.get('kt', 1.40)) or 1.40)
        kz = float(inputs.get('effective_kz', inputs.get('kz', 1.40)) or 1.40)

        # 1. Physical statutory components from Table 16
        tw_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(lbp, cls.L_NODES, cls.WEB_THK_NODES)
        tw_req = round(tw_base * kt, 2)

        af_base, _, _, _, _ = cls.interpolate_1d(lbp, cls.L_NODES, cls.FACE_AREA_NODES)
        af_req = round(af_base * kt, 2)

        bf_base, _, _, _, _ = cls.interpolate_1d(lbp, cls.L_NODES, cls.FACE_WIDTH_NODES)
        bf_req = round(bf_base, 1)

        # 2. Section Modulus requirement
        sm_base = cls.BASELINE_SM
        sm_req = round(sm_base * kz, 2)

        # 3. Multi-column bounding cells for Table 16 (Cols 1, 2, 3)
        bounding_cells = [
            {"row": idx1, "col": 1, "val": cls.WEB_THK_NODES[idx1]},
            {"row": idx2, "col": 1, "val": cls.WEB_THK_NODES[idx2]},
            {"row": idx1, "col": 2, "val": cls.FACE_AREA_NODES[idx1]},
            {"row": idx2, "col": 2, "val": cls.FACE_AREA_NODES[idx2]},
            {"row": idx1, "col": 3, "val": cls.FACE_WIDTH_NODES[idx1]},
            {"row": idx2, "col": 3, "val": cls.FACE_WIDTH_NODES[idx2]},
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=1,
            active_cols=[1, 2, 3],
            bounding_cells=bounding_cells,
            interpolated_val=tw_base,
            is_extrapolated=is_extrap
        )

        components = [
            {
                "name": "Web Plate Thickness",
                "param": "web_thk",
                "base": round(tw_base, 2),
                "factor": kt,
                "rreq": tw_req,
                "unit": "mm",
                "rule_desc": f"Table 16 Col 1: Base {tw_base:.2f} mm × kt({kt:.2f}) = {tw_req:.2f} mm"
            },
            {
                "name": "Face Plate Sectional Area",
                "param": "face_area",
                "base": round(af_base, 2),
                "factor": kt,
                "rreq": af_req,
                "unit": "cm2",
                "rule_desc": f"Table 16 Col 2: Base {af_base:.2f} cm² × kt({kt:.2f}) = {af_req:.2f} cm²"
            },
            {
                "name": "Face Plate Width",
                "param": "flange_width",
                "base": round(bf_base, 1),
                "factor": 1.0,
                "rreq": bf_req,
                "unit": "mm",
                "rule_desc": f"Table 16 Col 3: Minimum Face Width = {bf_req:.1f} mm"
            },
            {
                "name": "Girder Section Modulus",
                "param": "sm",
                "base": round(sm_base, 2),
                "factor": kz,
                "rreq": sm_req,
                "unit": "cm3",
                "rule_desc": f"Statutory Equivalent SM: Base {sm_base:.2f} cm³ × kz({kz:.2f}) = {sm_req:.2f} cm³"
            }
        ]

        derivation = (
            f"Table 16 Center Keelson (L={lbp:.2f} m): "
            f"tw_req = {tw_req:.2f} mm, "
            f"Af_req = {af_req:.2f} cm², "
            f"bf_req = {bf_req:.1f} mm, "
            f"Req SM = {sm_req:.2f} cm³ (kz={kz:.2f})."
        )

        return InterpolationResult(
            baseline=round(sm_base, 2),
            rreq=sm_req,
            unit="cm3",
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 24, Table 16 Center Keelson Dimensions & Section Modulus",
            inputs_used={"L": lbp, "kt": kt, "kz": kz},
            bounding_nodes={
                "L1": cls.L_NODES[idx1], "L2": cls.L_NODES[idx2],
                "tw_base": round(tw_base, 2), "af_base": round(af_base, 2), "bf_base": round(bf_base, 1)
            },
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view,
            components=components
        )


class Table15SideKeelsonInterpolator(BaseTableInterpolator):
    table_index = 14  # Table 15: Side Keelson Web Thickness & Face Plate Area
    table_no_str = "Table 15"
    table_title = "Web Plate Thickness and Face Plate Sectional Area"
    ref_rule = "Rule 23, Table 15"
    default_unit = "cm3"

    L_NODES = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0]
    WEB_THK_NODES = [6.5, 7.0, 7.5, 8.0, 8.5, 9.0]
    FACE_AREA_NODES = [18.0, 23.0, 28.0, 32.0, 36.0, 42.0]
    BASELINE_SM = 400.0  # Rule baseline equivalent Section Modulus in cm3

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "stiff_side_keelson") -> InterpolationResult:
        lbp = float(inputs.get('lbp', inputs.get('L', 69.85)) or 69.85)
        kt = float(inputs.get('effective_kt', inputs.get('kt', 1.40)) or 1.40)
        kz = float(inputs.get('effective_kz', inputs.get('kz', 1.40)) or 1.40)

        # 1. Physical statutory components from Table 15
        tw_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(lbp, cls.L_NODES, cls.WEB_THK_NODES)
        tw_req = round(tw_base * kt, 2)

        af_base, _, _, _, _ = cls.interpolate_1d(lbp, cls.L_NODES, cls.FACE_AREA_NODES)
        af_req = round(af_base * kt, 2)

        # 2. Section Modulus requirement
        sm_base = cls.BASELINE_SM
        sm_req = round(sm_base * kz, 2)

        # 3. Multi-column bounding cells for Table 15 (Cols 1, 2)
        bounding_cells = [
            {"row": idx1, "col": 1, "val": cls.WEB_THK_NODES[idx1]},
            {"row": idx2, "col": 1, "val": cls.WEB_THK_NODES[idx2]},
            {"row": idx1, "col": 2, "val": cls.FACE_AREA_NODES[idx1]},
            {"row": idx2, "col": 2, "val": cls.FACE_AREA_NODES[idx2]},
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=1,
            active_cols=[1, 2],
            bounding_cells=bounding_cells,
            interpolated_val=tw_base,
            is_extrapolated=is_extrap
        )

        components = [
            {
                "name": "Web Plate Thickness",
                "param": "web_thk",
                "base": round(tw_base, 2),
                "factor": kt,
                "rreq": tw_req,
                "unit": "mm",
                "rule_desc": f"Table 15 Col 1: Base {tw_base:.2f} mm × kt({kt:.2f}) = {tw_req:.2f} mm"
            },
            {
                "name": "Face Plate Sectional Area",
                "param": "face_area",
                "base": round(af_base, 2),
                "factor": kt,
                "rreq": af_req,
                "unit": "cm2",
                "rule_desc": f"Table 15 Col 2: Base {af_base:.2f} cm² × kt({kt:.2f}) = {af_req:.2f} cm²"
            },
            {
                "name": "Girder Section Modulus",
                "param": "sm",
                "base": round(sm_base, 2),
                "factor": kz,
                "rreq": sm_req,
                "unit": "cm3",
                "rule_desc": f"Statutory Equivalent SM: Base {sm_base:.2f} cm³ × kz({kz:.2f}) = {sm_req:.2f} cm³"
            }
        ]

        derivation = (
            f"Table 15 Side Keelson (L={lbp:.2f} m): "
            f"tw_req = {tw_req:.2f} mm, "
            f"Af_req = {af_req:.2f} cm², "
            f"Req SM = {sm_req:.2f} cm³ (kz={kz:.2f})."
        )

        return InterpolationResult(
            baseline=round(sm_base, 2),
            rreq=sm_req,
            unit="cm3",
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 23, Table 15 Side Keelson Dimensions & Section Modulus",
            inputs_used={"L": lbp, "kt": kt, "kz": kz},
            bounding_nodes={
                "L1": cls.L_NODES[idx1], "L2": cls.L_NODES[idx2],
                "tw_base": round(tw_base, 2), "af_base": round(af_base, 2)
            },
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view,
            components=components
        )


# Alias Table1416KeelsonInterpolator to Table16CenterKeelsonInterpolator for backward compatibility
Table1416KeelsonInterpolator = Table16CenterKeelsonInterpolator
