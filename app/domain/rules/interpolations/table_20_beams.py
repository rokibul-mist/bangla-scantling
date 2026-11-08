"""
Table 20: Deck Beams Section Modulus Interpolator.
Statutory Reference: Rule 28, Table 20.
Governing parameters: Beam Span l (m) and Frame Spacing s (mm).
"""

from typing import Dict, Any
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table20BeamsInterpolator(BaseTableInterpolator):
    table_index = 19
    table_no_str = "Table 20"
    table_title = "Deck Beams Section Modulus"
    ref_rule = "Rule 28, Table 20"
    default_unit = "cm³"

    SPAN_NODES = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, 12.0]
    SM_450 = [6.0, 13.0, 23.0, 36.0, 52.0, 70.0, 91.0, 142.0, 205.0]
    SM_500 = [7.0, 15.0, 26.0, 40.0, 57.0, 78.0, 100.0, 158.0, 228.0]
    SM_550 = [8.0, 16.0, 28.0, 44.0, 63.0, 85.0, 110.0, 174.0, 250.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "stiff_deck_beam") -> InterpolationResult:
        breadth = float(inputs.get('breadth', 13.41) or 13.41)
        # Unsupported beam span outside hatchway (or half breadth if no hatch)
        hatch_w = breadth * 0.65
        beam_span = float(inputs.get('deck_beam_span') or ((breadth - hatch_w) / 2.0) or 2.35)
        spacing = float(inputs.get('frame_spacing', 550.0) or 550.0)
        kz = float(inputs.get('effective_kz', 1.25) or 1.25)

        if spacing <= 475.0:
            y_nodes = cls.SM_450
            col_idx = 1
            col_label = "450 mm"
        elif spacing <= 525.0:
            y_nodes = cls.SM_500
            col_idx = 2
            col_label = "500 mm"
        else:
            y_nodes = cls.SM_550
            col_idx = 3
            col_label = "550 mm"

        z_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(beam_span, cls.SPAN_NODES, y_nodes)
        z_corr, sp_factor = cls.apply_spacing_correction(z_base, spacing, is_sm=True)
        rreq = round(z_corr * kz, 2)

        bounding_cells = [
            {"row": idx1, "col": col_idx, "val": y_nodes[idx1]},
            {"row": idx2, "col": col_idx, "val": y_nodes[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=col_idx,
            bounding_cells=bounding_cells,
            interpolated_val=z_corr,
            is_extrapolated=is_extrap
        )

        derivation = (
            f"Table 20 (Span={beam_span:.2f} m, Spacing={spacing:.0f} mm): "
            f"Base Z={y_nodes[idx1]} + {lam:.3f}*({y_nodes[idx2]}-{y_nodes[idx1]}) = {z_base:.1f} cm³"
        )
        if sp_factor > 1.0:
            derivation += f" x Spacing Corr({sp_factor:.3f}) = {z_corr:.1f} cm³"
        derivation += f" x kz({kz:.2f}) = {rreq:.2f} cm³"

        return InterpolationResult(
            baseline=round(z_corr, 2),
            rreq=rreq,
            unit=cls.default_unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc=f"Rule 28, Table 20 ({col_label}) with linear interpolation by Beam Span l",
            inputs_used={"beam_span": beam_span, "frame_spacing": spacing, "kz": kz},
            bounding_nodes={"Span1": cls.SPAN_NODES[idx1], "Span2": cls.SPAN_NODES[idx2], "Z1": y_nodes[idx1], "Z2": y_nodes[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=sp_factor,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )
