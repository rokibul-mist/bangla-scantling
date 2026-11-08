"""
Tables 54 - 57: Steel Piping & Bilge Suction Diameter Interpolators.
Statutory Reference: Rules 56 - 59, Tables 54 - 57.
Governing parameters: Vessel Length L (m) and Pipe Outer Diameter (mm).
"""

from typing import Dict, Any, List
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table54PipeWallInterpolator(BaseTableInterpolator):
    table_index = 54  # Table 54: Steel Pipes Minimum Wall Thickness
    table_no_str = "Table 54"
    table_title = "Steel Pipes Minimum Wall Thickness"
    ref_rule = "Rule 56, Table 54"
    default_unit = "mm"

    OD_NODES = [17.2, 21.3, 26.9, 33.7, 60.3, 88.9, 114.3, 139.7, 168.3, 193.7, 219.1]
    THK_NODES = [1.8, 2.0, 2.3, 2.6, 2.9, 3.2, 3.6, 4.0, 4.5, 5.4, 5.9]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "pipe_wall_thk") -> InterpolationResult:
        pipe_od = float(inputs.get('pipe_outer_dia') or 75.0)

        t_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(pipe_od, cls.OD_NODES, cls.THK_NODES)
        rreq = round(t_base, 2)

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

        derivation = f"Table 54 (Pipe OD={pipe_od:.1f} mm): Minimum Wall Thickness = {t_base:.2f} mm"

        return InterpolationResult(
            baseline=round(t_base, 2),
            rreq=rreq,
            unit=cls.default_unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 56, Table 54 Steel Pipes Minimum Wall Thickness",
            inputs_used={"pipe_od": pipe_od, "factor": 1.0},
            bounding_nodes={"OD1": cls.OD_NODES[idx1], "OD2": cls.OD_NODES[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )


class Table57BilgePipeInterpolator(BaseTableInterpolator):
    table_index = 57  # Table 57: Main Bilge Pipe Internal Diameter
    table_no_str = "Table 57"
    table_title = "Main Bilge Pipe Internal Diameter"
    ref_rule = "Rule 59, Table 57"
    default_unit = "mm"

    L_NODES = [30.0, 40.0, 50.0, 60.0, 70.0]
    DIA_NODES = [50.0, 55.0, 62.0, 70.0, 75.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "pipe_main_bilge_dia") -> InterpolationResult:
        lbp = float(inputs.get('lbp', 69.85) or 69.85)

        d_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(lbp, cls.L_NODES, cls.DIA_NODES)
        rreq = round(d_base, 1)

        bounding_cells = [
            {"row": idx1, "col": 1, "val": cls.DIA_NODES[idx1]},
            {"row": idx2, "col": 1, "val": cls.DIA_NODES[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=1,
            bounding_cells=bounding_cells,
            interpolated_val=d_base,
            is_extrapolated=is_extrap
        )

        derivation = f"Table 57 (L={lbp:.2f} m): Main Bilge Internal Dia = {d_base:.1f} mm"

        return InterpolationResult(
            baseline=round(d_base, 1),
            rreq=rreq,
            unit=cls.default_unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 59, Table 57 Main Bilge Pipe Internal Diameter",
            inputs_used={"L": lbp, "factor": 1.0},
            bounding_nodes={"L1": cls.L_NODES[idx1], "L2": cls.L_NODES[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )
