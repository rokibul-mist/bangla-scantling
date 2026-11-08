"""
Tables 49 - 50: V-Strut and I-Strut Dimensions Interpolator.
Statutory Reference: Rules 51 - 52, Tables 49 - 50.
Governing parameter: Propeller Shaft Diameter D (mm).
"""

from typing import Dict, Any, List
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table49VStrutInterpolator(BaseTableInterpolator):
    table_index = 49  # Table 49: V-Strut Dimensions
    table_no_str = "Table 49"
    table_title = "V-Strut Dimensions"
    ref_rule = "Rule 51, Table 49"
    default_unit = "mm"

    SHAFT_NODES = [25.0, 40.0, 60.0, 75.0, 90.0, 105.0, 125.0, 150.0]
    WIDTH_NODES = [56.0, 86.0, 132.0, 168.0, 203.0, 234.0, 278.0, 334.0]
    THK_NODES = [9.0, 15.0, 22.0, 28.0, 33.0, 38.0, 45.0, 55.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "v_strut_shaft") -> InterpolationResult:
        shaft_dia = float(inputs.get('shaft_propeller_dia') or inputs.get('shaft_thrust_dia') or 105.0)

        w_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(shaft_dia, cls.SHAFT_NODES, cls.WIDTH_NODES)
        t_base, _, _, _, _ = cls.interpolate_1d(shaft_dia, cls.SHAFT_NODES, cls.THK_NODES)

        rreq = round(t_base, 1)

        bounding_cells = [
            {"row": idx1, "col": 1, "val": cls.WIDTH_NODES[idx1]},
            {"row": idx2, "col": 1, "val": cls.WIDTH_NODES[idx2]},
            {"row": idx1, "col": 2, "val": cls.THK_NODES[idx1]},
            {"row": idx2, "col": 2, "val": cls.THK_NODES[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=2,
            active_cols=[1, 2],
            bounding_cells=bounding_cells,
            interpolated_val=t_base,
            is_extrapolated=is_extrap
        )

        derivation = f"Table 49 (Shaft Dia={shaft_dia:.1f} mm): Width={w_base:.1f} mm, Thickness={t_base:.1f} mm"

        components = [
            {"name": "Strut Width (per strut)", "base": round(w_base, 1), "factor": 1.0, "rreq": round(w_base, 1), "unit": "mm"},
            {"name": "Strut Thickness (per strut)", "base": round(t_base, 1), "factor": 1.0, "rreq": round(t_base, 1), "unit": "mm"}
        ]

        return InterpolationResult(
            baseline=round(t_base, 1),
            rreq=rreq,
            unit=cls.default_unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 51, Table 49 V-Strut Dimensions",
            inputs_used={"shaft_dia": shaft_dia, "factor": 1.0},
            bounding_nodes={"D1": cls.SHAFT_NODES[idx1], "D2": cls.SHAFT_NODES[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view,
            components=components
        )


class Table50IStrutInterpolator(BaseTableInterpolator):
    table_index = 50  # Table 50: I-Strut Dimensions
    table_no_str = "Table 50"
    table_title = "I-Strut Dimensions"
    ref_rule = "Rule 52, Table 50"
    default_unit = "mm"

    SHAFT_NODES = [25.0, 40.0, 60.0, 75.0, 90.0, 105.0, 125.0, 150.0]
    WIDTH_NODES = [80.0, 130.0, 190.0, 240.0, 290.0, 340.0, 400.0, 480.0]
    THK_NODES = [12.0, 21.0, 30.0, 40.0, 48.0, 54.0, 64.0, 76.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "i_strut_shaft") -> InterpolationResult:
        shaft_dia = float(inputs.get('shaft_propeller_dia') or inputs.get('shaft_thrust_dia') or 105.0)

        w_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(shaft_dia, cls.SHAFT_NODES, cls.WIDTH_NODES)
        t_base, _, _, _, _ = cls.interpolate_1d(shaft_dia, cls.SHAFT_NODES, cls.THK_NODES)

        rreq = round(t_base, 1)

        bounding_cells = [
            {"row": idx1, "col": 1, "val": cls.WIDTH_NODES[idx1]},
            {"row": idx2, "col": 1, "val": cls.WIDTH_NODES[idx2]},
            {"row": idx1, "col": 2, "val": cls.THK_NODES[idx1]},
            {"row": idx2, "col": 2, "val": cls.THK_NODES[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=2,
            active_cols=[1, 2],
            bounding_cells=bounding_cells,
            interpolated_val=t_base,
            is_extrapolated=is_extrap
        )

        derivation = f"Table 50 (Shaft Dia={shaft_dia:.1f} mm): Width={w_base:.1f} mm, Thickness={t_base:.1f} mm"

        components = [
            {"name": "Strut Width (per strut)", "base": round(w_base, 1), "factor": 1.0, "rreq": round(w_base, 1), "unit": "mm"},
            {"name": "Strut Thickness (per strut)", "base": round(t_base, 1), "factor": 1.0, "rreq": round(t_base, 1), "unit": "mm"}
        ]

        return InterpolationResult(
            baseline=round(t_base, 1),
            rreq=rreq,
            unit=cls.default_unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 52, Table 50 I-Strut Dimensions",
            inputs_used={"shaft_dia": shaft_dia, "factor": 1.0},
            bounding_nodes={"D1": cls.SHAFT_NODES[idx1], "D2": cls.SHAFT_NODES[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view,
            components=components
        )
