"""
Table 3: Bilge Plate Thickness Interpolator.
Statutory Reference: Rule 11, Table 3.
Governing parameters: Vessel Length L (m) and Frame Spacing s (mm).
"""

from typing import Dict, Any
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table03BilgeInterpolator(BaseTableInterpolator):
    table_index = 2
    table_no_str = "Table 3"
    table_title = "Bilge Plate Thickness"
    ref_rule = "Rule 11, Table 3"
    default_unit = "mm"

    L_NODES = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0]
    THK_450 = [6.0, 6.5, 7.0, 7.5, 8.0, 8.5]
    THK_500 = [6.5, 7.0, 7.5, 8.0, 8.5, 9.0]
    THK_550 = [7.0, 7.5, 8.0, 8.5, 9.0, 9.5]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "plate_bilge") -> InterpolationResult:
        lbp = float(inputs.get('lbp', 69.85) or 69.85)
        spacing = float(inputs.get('frame_spacing', 550.0) or 550.0)
        kt = float(inputs.get('effective_kt', 1.20) or 1.20)

        if spacing <= 475.0:
            y_nodes = cls.THK_450
            col_idx = 1
            col_label = "450 mm"
        elif spacing <= 525.0:
            y_nodes = cls.THK_500
            col_idx = 2
            col_label = "500 mm"
        else:
            y_nodes = cls.THK_550
            col_idx = 3
            col_label = "550 mm"

        t_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(lbp, cls.L_NODES, y_nodes)
        t_corr, sp_factor = cls.apply_spacing_correction(t_base, spacing, is_sm=False)
        rreq = round(t_corr * kt, 2)

        bounding_cells = [
            {"row": idx1, "col": col_idx, "val": y_nodes[idx1]},
            {"row": idx2, "col": col_idx, "val": y_nodes[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=col_idx,
            bounding_cells=bounding_cells,
            interpolated_val=t_corr,
            is_extrapolated=is_extrap
        )

        derivation = (
            f"Table 3 (L={lbp:.2f} m, Spacing={spacing:.0f} mm): "
            f"Base={y_nodes[idx1]} + {lam:.3f}*({y_nodes[idx2]}-{y_nodes[idx1]}) = {t_base:.2f} mm"
        )
        if sp_factor > 1.0:
            derivation += f" x Spacing Corr({sp_factor:.3f}) = {t_corr:.2f} mm"
        derivation += f" x kt({kt:.2f}) = {rreq:.2f} mm"

        return InterpolationResult(
            baseline=round(t_corr, 2),
            rreq=rreq,
            unit="mm",
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc=f"Rule 11, Table 3 ({col_label}) with linear interpolation by L and spacing correction",
            inputs_used={"L": lbp, "frame_spacing": spacing, "kt": kt},
            bounding_nodes={"L1": cls.L_NODES[idx1], "L2": cls.L_NODES[idx2], "t1": y_nodes[idx1], "t2": y_nodes[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=sp_factor,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )
