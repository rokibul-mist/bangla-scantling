"""
Table 7 - 12: Stem, Stern Post, Propeller Post, Sole Piece & Boss Interpolators.
Statutory Reference: Rules 15 - 19, Tables 7 - 12.
Governing parameters: Vessel Length L (m) and Propeller Shaft Dia (mm).
"""

from typing import Dict, Any, List
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table07StemInterpolator(BaseTableInterpolator):
    table_index = 6
    table_no_str = "Table 7"
    table_title = "Steel Plate Stem Thickness"
    ref_rule = "Rule 15, Table 7"
    default_unit = "mm"

    L_NODES = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0]
    THK_STEM = [6.0, 7.0, 8.0, 9.0, 10.0, 11.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "plate_stem") -> InterpolationResult:
        lbp = float(inputs.get('lbp', 69.85) or 69.85)
        kt = float(inputs.get('effective_kt', 1.20) or 1.20)

        t_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(lbp, cls.L_NODES, cls.THK_STEM)
        rreq = round(t_base * kt, 2)

        bounding_cells = [
            {"row": idx1, "col": 1, "val": cls.THK_STEM[idx1]},
            {"row": idx2, "col": 1, "val": cls.THK_STEM[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=1,
            bounding_cells=bounding_cells,
            interpolated_val=t_base,
            is_extrapolated=is_extrap
        )

        derivation = f"Table 7 (L={lbp:.2f} m): Base={cls.THK_STEM[idx1]} + {lam:.3f}*({cls.THK_STEM[idx2]}-{cls.THK_STEM[idx1]}) = {t_base:.2f} mm x kt({kt:.2f}) = {rreq:.2f} mm"

        return InterpolationResult(
            baseline=round(t_base, 2),
            rreq=rreq,
            unit="mm",
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 15, Table 7 with linear interpolation by L",
            inputs_used={"L": lbp, "kt": kt},
            bounding_nodes={"L1": cls.L_NODES[idx1], "L2": cls.L_NODES[idx2], "t1": cls.THK_STEM[idx1], "t2": cls.THK_STEM[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )


class Table08BarStemInterpolator(BaseTableInterpolator):
    table_index = 7
    table_no_str = "Table 8"
    table_title = "Rectangular Bar Stem Dimensions"
    ref_rule = "Rule 16, Table 8"
    default_unit = "mm"

    L_NODES = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0]
    WIDTH_NODES = [100.0, 110.0, 125.0, 135.0, 150.0, 165.0]
    THK_NODES = [20.0, 22.0, 25.0, 30.0, 35.0, 40.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "bar_stem") -> InterpolationResult:
        lbp = float(inputs.get('lbp', 69.85) or 69.85)
        w_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(lbp, cls.L_NODES, cls.WIDTH_NODES)
        t_base, _, _, _, _ = cls.interpolate_1d(lbp, cls.L_NODES, cls.THK_NODES)

        rreq = round(w_base, 1)

        bounding_cells = [
            {"row": idx1, "col": 1, "val": cls.WIDTH_NODES[idx1]},
            {"row": idx2, "col": 1, "val": cls.WIDTH_NODES[idx2]},
            {"row": idx1, "col": 2, "val": cls.THK_NODES[idx1]},
            {"row": idx2, "col": 2, "val": cls.THK_NODES[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=1,
            active_cols=[1, 2],
            bounding_cells=bounding_cells,
            interpolated_val=w_base,
            is_extrapolated=is_extrap
        )

        derivation = f"Table 8 (L={lbp:.2f} m): Width={w_base:.1f} mm, Thickness={t_base:.1f} mm"

        components = [
            {"name": "Breadth / Width", "base": round(w_base, 1), "factor": 1.0, "rreq": round(w_base, 1), "unit": "mm"},
            {"name": "Thickness", "base": round(t_base, 1), "factor": 1.0, "rreq": round(t_base, 1), "unit": "mm"}
        ]

        return InterpolationResult(
            baseline=round(w_base, 1),
            rreq=rreq,
            unit=cls.default_unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 16, Table 8 Rectangular Bar Stem Dimensions",
            inputs_used={"L": lbp, "factor": 1.0},
            bounding_nodes={"L1": cls.L_NODES[idx1], "L2": cls.L_NODES[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view,
            components=components
        )


class Table09SternBarInterpolator(BaseTableInterpolator):
    table_index = 8
    table_no_str = "Table 9"
    table_title = "Rectangular Stern Bar Dimensions"
    ref_rule = "Rule 17, Table 9"
    default_unit = "mm"

    L_NODES = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0]
    WIDTH_NODES = [100.0, 110.0, 125.0, 135.0, 150.0, 165.0]
    THK_NODES = [20.0, 25.0, 30.0, 35.0, 40.0, 45.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "stern_frame_bar") -> InterpolationResult:
        lbp = float(inputs.get('lbp', 69.85) or 69.85)
        w_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(lbp, cls.L_NODES, cls.WIDTH_NODES)
        t_base, _, _, _, _ = cls.interpolate_1d(lbp, cls.L_NODES, cls.THK_NODES)

        rreq = round(w_base, 1)

        bounding_cells = [
            {"row": idx1, "col": 1, "val": cls.WIDTH_NODES[idx1]},
            {"row": idx2, "col": 1, "val": cls.WIDTH_NODES[idx2]},
            {"row": idx1, "col": 2, "val": cls.THK_NODES[idx1]},
            {"row": idx2, "col": 2, "val": cls.THK_NODES[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=1,
            active_cols=[1, 2],
            bounding_cells=bounding_cells,
            interpolated_val=w_base,
            is_extrapolated=is_extrap
        )

        derivation = f"Table 9 (L={lbp:.2f} m): Width={w_base:.1f} mm, Thickness={t_base:.1f} mm"

        components = [
            {"name": "Breadth / Width", "base": round(w_base, 1), "factor": 1.0, "rreq": round(w_base, 1), "unit": "mm"},
            {"name": "Thickness", "base": round(t_base, 1), "factor": 1.0, "rreq": round(t_base, 1), "unit": "mm"}
        ]

        return InterpolationResult(
            baseline=round(w_base, 1),
            rreq=rreq,
            unit=cls.default_unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 17, Table 9 Rectangular Stern Bar Dimensions",
            inputs_used={"L": lbp, "factor": 1.0},
            bounding_nodes={"L1": cls.L_NODES[idx1], "L2": cls.L_NODES[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view,
            components=components
        )


class Table10PropellerPostInterpolator(BaseTableInterpolator):
    table_index = 9
    table_no_str = "Table 10"
    table_title = "Propeller Post Dimensions"
    ref_rule = "Rule 18, Table 10"
    default_unit = "mm"

    L_NODES = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0]
    WIDTH_NODES = [150.0, 172.0, 200.0, 225.0, 250.0, 275.0]
    THK_NODES = [28.0, 37.0, 45.0, 55.0, 64.0, 75.0]
    RADIUS_NODES = [24.0, 28.0, 32.0, 36.0, 40.0, 45.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "propeller_post") -> InterpolationResult:
        lbp = float(inputs.get('lbp', 69.85) or 69.85)
        w_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(lbp, cls.L_NODES, cls.WIDTH_NODES)
        t_base, _, _, _, _ = cls.interpolate_1d(lbp, cls.L_NODES, cls.THK_NODES)
        r_base, _, _, _, _ = cls.interpolate_1d(lbp, cls.L_NODES, cls.RADIUS_NODES)

        rreq = round(w_base, 1)

        bounding_cells = [
            {"row": idx1, "col": 1, "val": cls.WIDTH_NODES[idx1]},
            {"row": idx2, "col": 1, "val": cls.WIDTH_NODES[idx2]},
            {"row": idx1, "col": 2, "val": cls.THK_NODES[idx1]},
            {"row": idx2, "col": 2, "val": cls.THK_NODES[idx2]},
            {"row": idx1, "col": 3, "val": cls.RADIUS_NODES[idx1]},
            {"row": idx2, "col": 3, "val": cls.RADIUS_NODES[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=1,
            active_cols=[1, 2, 3],
            bounding_cells=bounding_cells,
            interpolated_val=w_base,
            is_extrapolated=is_extrap
        )

        derivation = f"Table 10 (L={lbp:.2f} m): Width={w_base:.1f} mm, Thickness={t_base:.1f} mm, Radius={r_base:.1f} mm"

        components = [
            {"name": "Breadth / Width", "base": round(w_base, 1), "factor": 1.0, "rreq": round(w_base, 1), "unit": "mm"},
            {"name": "Thickness", "base": round(t_base, 1), "factor": 1.0, "rreq": round(t_base, 1), "unit": "mm"},
            {"name": "Radius", "base": round(r_base, 1), "factor": 1.0, "rreq": round(r_base, 1), "unit": "mm"}
        ]

        return InterpolationResult(
            baseline=round(w_base, 1),
            rreq=rreq,
            unit=cls.default_unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 18, Table 10 Propeller Post Dimensions",
            inputs_used={"L": lbp, "factor": 1.0},
            bounding_nodes={"L1": cls.L_NODES[idx1], "L2": cls.L_NODES[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view,
            components=components
        )


class Table11SolePieceInterpolator(BaseTableInterpolator):
    table_index = 10
    table_no_str = "Table 11"
    table_title = "Sole Piece Dimensions"
    ref_rule = "Rule 19, Table 11"
    default_unit = "mm"

    L_NODES = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0]
    THK_NODES = [30.0, 40.0, 50.0, 60.0, 70.0, 75.0]
    WIDTH_NODES = [90.0, 120.0, 150.0, 170.0, 190.0, 210.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "sole_piece") -> InterpolationResult:
        lbp = float(inputs.get('lbp', 69.85) or 69.85)
        w_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(lbp, cls.L_NODES, cls.WIDTH_NODES)
        t_base, _, _, _, _ = cls.interpolate_1d(lbp, cls.L_NODES, cls.THK_NODES)

        is_thk = (member_id == "sole_piece_thk")
        active_col = 1 if is_thk else 2
        primary_val = t_base if is_thk else w_base
        rreq = round(primary_val, 1)

        bounding_cells = [
            {"row": idx1, "col": 1, "val": cls.THK_NODES[idx1]},
            {"row": idx2, "col": 1, "val": cls.THK_NODES[idx2]},
            {"row": idx1, "col": 2, "val": cls.WIDTH_NODES[idx1]},
            {"row": idx2, "col": 2, "val": cls.WIDTH_NODES[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=active_col,
            active_cols=[1, 2],
            bounding_cells=bounding_cells,
            interpolated_val=primary_val,
            is_extrapolated=is_extrap
        )

        derivation = f"Table 11 (L={lbp:.2f} m): Breadth={w_base:.1f} mm, Thickness={t_base:.1f} mm"

        components = [
            {"name": "Breadth / Width", "base": round(w_base, 1), "factor": 1.0, "rreq": round(w_base, 1), "unit": "mm"},
            {"name": "Thickness", "base": round(t_base, 1), "factor": 1.0, "rreq": round(t_base, 1), "unit": "mm"}
        ]

        return InterpolationResult(
            baseline=round(primary_val, 1),
            rreq=rreq,
            unit=cls.default_unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 19, Table 11 Sole Piece Dimensions",
            inputs_used={"L": lbp, "factor": 1.0},
            bounding_nodes={"L1": cls.L_NODES[idx1], "L2": cls.L_NODES[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view,
            components=components
        )


class Table12PropellerBossInterpolator(BaseTableInterpolator):
    table_index = 11
    table_no_str = "Table 12"
    table_title = "Propeller Boss Thickness"
    ref_rule = "Rule 19, Table 12"
    default_unit = "mm"

    SHAFT_NODES = [30.0, 40.0, 50.0, 60.0, 75.0, 90.0, 105.0, 120.0, 140.0, 160.0]
    THK_NODES = [11.0, 14.0, 18.0, 21.0, 27.0, 32.0, 38.0, 42.0, 50.0, 58.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "propeller_boss_thk") -> InterpolationResult:
        shaft_dia = float(inputs.get('shaft_propeller_dia') or inputs.get('shaft_intermediate_dia') or 105.0)
        t_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(shaft_dia, cls.SHAFT_NODES, cls.THK_NODES)

        rreq = round(t_base, 1)

        bounding_cells = [
            {"row": idx1, "col": 1, "val": cls.THK_NODES[idx1]},
            {"row": idx2, "col": 1, "val": cls.THK_NODES[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=1,
            bounding_cells=bounding_cells,
            interpolated_val=t_base,
            is_extrapolated=is_extrap
        )

        derivation = f"Table 12 (Shaft Dia={shaft_dia:.1f} mm): Boss Thickness = {t_base:.1f} mm"

        return InterpolationResult(
            baseline=round(t_base, 1),
            rreq=rreq,
            unit=cls.default_unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 19, Table 12 Propeller Boss Thickness",
            inputs_used={"shaft_dia": shaft_dia, "factor": 1.0},
            bounding_nodes={"d1": cls.SHAFT_NODES[idx1], "d2": cls.SHAFT_NODES[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )
