"""
Tables 32, 34 & 35: Portable Beams, Hatch Covers & Deckhouse Stiffeners Interpolator.
Statutory Reference: Rules 41 & 42, Tables 32, 34 & 35.
Governing parameters: Span Length (m) and Frame Spacing s (mm).
"""

from typing import Dict, Any
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table3235HatchBeamsCoversInterpolator(BaseTableInterpolator):
    table_index = 31  # Table 32 Portable Beams
    table_no_str = "Table 32"
    table_title = "Hatch Beams, Covers & Deckhouse Stiffeners"
    ref_rule = "Rules 41 & 42, Tables 32, 34 & 35"
    default_unit = "cm³"

    # Table 34 Hatch cover stiffener span nodes & values (col 3: 550mm)
    COVER_SPAN_NODES = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    COVER_SM_550 = [5.0, 5.0, 9.0, 14.0, 20.0, 27.0, 38.0]

    # Table 35 Deckhouse wall stiffener span nodes & values (col 3: 550mm)
    DECKHOUSE_SPAN_NODES = [2.0, 2.2, 2.4, 2.6, 2.8, 3.0]
    DECKHOUSE_SM_550 = [12.0, 14.0, 16.0, 20.0, 22.0, 26.0]

    # Table 32 Portable beam hatch width nodes & values (col 2: b=2.0m)
    PORTABLE_BP_NODES = [1.0, 1.5, 2.0, 2.5]
    PORTABLE_SM_B2 = [7.0, 10.0, 13.0, 16.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "stiff_hatch_cover") -> InterpolationResult:
        spacing = float(inputs.get('frame_spacing', 550.0) or 550.0)
        kz = float(inputs.get('effective_kz', 1.25) or 1.25)

        if "portable" in member_id or "hatch_end" in member_id or "hatch_side" in member_id:
            cls.table_index = 31
            cls.table_no_str = "Table 32"
            cls.table_title = "Portable Beams Section Modulus"
            cls.ref_rule = "Rule 41, Table 32"
            span_val = 2.0  # nominal hatch width / span
            x_nodes = cls.PORTABLE_BP_NODES
            y_nodes = cls.PORTABLE_SM_B2
            col_idx = 2
        elif "superstructure" in member_id:
            cls.table_index = 35
            cls.table_no_str = "Table 35"
            cls.table_title = "Deckhouse Out-Mounted Stiffeners Section Modulus"
            cls.ref_rule = "Rule 42, Table 35"
            span_val = 2.4  # superstructure tween deck height
            x_nodes = cls.DECKHOUSE_SPAN_NODES
            y_nodes = cls.DECKHOUSE_SM_550
            col_idx = 3
        else:
            cls.table_index = 34
            cls.table_no_str = "Table 34"
            cls.table_title = "Hatch Cover Stiffeners Section Modulus"
            cls.ref_rule = "Rule 41, Table 34"
            span_val = 3.0  # hatch cover unsupported span
            x_nodes = cls.COVER_SPAN_NODES
            y_nodes = cls.COVER_SM_550
            col_idx = 3

        val_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(span_val, x_nodes, y_nodes)
        val_corr, sp_factor = cls.apply_spacing_correction(val_base, spacing, is_sm=True)
        rreq = round(val_corr * kz, 2)

        bounding_cells = [
            {"row": idx1, "col": col_idx, "val": y_nodes[idx1]},
            {"row": idx2, "col": col_idx, "val": y_nodes[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=col_idx,
            bounding_cells=bounding_cells,
            interpolated_val=val_corr,
            is_extrapolated=is_extrap
        )

        derivation = (
            f"{cls.table_no_str} (Span={span_val:.2f} m, Spacing={spacing:.0f} mm): "
            f"Base={val_base:.1f} cm³, Spacing Factor={sp_factor:.3f} -> "
            f"Required Section Modulus = {rreq:.2f} cm³ (kz={kz:.2f})."
        )

        return InterpolationResult(
            baseline=round(val_base, 1),
            rreq=rreq,
            unit="cm³",
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc=f"{cls.ref_rule} (span, spacing)",
            inputs_used={"span": span_val, "spacing": spacing, "kz": kz},
            bounding_nodes={
                "lower": {"span": x_nodes[idx1], "val": y_nodes[idx1]},
                "upper": {"span": x_nodes[idx2], "val": y_nodes[idx2]}
            },
            lambda_ratio=round(lam, 4),
            spacing_correction=sp_factor,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )
