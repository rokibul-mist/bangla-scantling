"""
Table 5: Deck Plating Thickness at Hatchways Interpolator.
Statutory Reference: Rule 13, Table 5.
Governing parameters: Vessel Length L (m) and Framing Type (Transverse / Longitudinal).
"""

from typing import Dict, Any
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table05DeckHatchInterpolator(BaseTableInterpolator):
    table_index = 4
    table_no_str = "Table 5"
    table_title = "Deck Plating Thickness at Hatchways"
    ref_rule = "Rule 13, Table 5"
    default_unit = "mm"

    L_NODES = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0]
    THK_TRANS = [5.0, 6.0, 7.0, 7.5, 8.5, 9.0]
    THK_LONG = [4.5, 5.5, 6.5, 7.0, 7.5, 8.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "plate_deck_hatch") -> InterpolationResult:
        lbp = float(inputs.get('lbp', 69.85) or 69.85)
        spacing = float(inputs.get('frame_spacing', 550.0) or 550.0)
        kt = float(inputs.get('effective_kt', 1.20) or 1.20)
        framing_type = str(inputs.get('framing_system', 'Transverse')).lower()
        is_long = 'long' in framing_type

        y_nodes = cls.THK_LONG if is_long else cls.THK_TRANS
        col_idx = 2 if is_long else 1
        col_label = "Longitudinal Framing" if is_long else "Transverse Framing"

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
            f"Table 5 ({col_label}, L={lbp:.2f} m): "
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
            formula_desc=f"Rule 13, Table 5 ({col_label}) with linear interpolation by L",
            inputs_used={"L": lbp, "frame_spacing": spacing, "kt": kt},
            bounding_nodes={"L1": cls.L_NODES[idx1], "L2": cls.L_NODES[idx2], "t1": y_nodes[idx1], "t2": y_nodes[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=sp_factor,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )
