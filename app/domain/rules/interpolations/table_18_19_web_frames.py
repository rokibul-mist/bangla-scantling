"""
Tables 18 & 19: Web Frames Maximum Spacing & Side Stringers Section Modulus Interpolator.
Statutory Reference: Rules 26 & 27, Tables 18 & 19.
Governing parameters: Vessel Depth D (m) and Web Frame Span L (m).
"""

from typing import Dict, Any
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table1819WebFramesInterpolator(BaseTableInterpolator):
    table_index = 18  # Table 19: Side Stringers / Web Frames Section Modulus
    table_no_str = "Table 19"
    table_title = "Side Stringers / Web Frames Section Modulus"
    ref_rule = "Rule 27, Table 19"
    default_unit = "cm3"

    DEPTH_NODES = [2.5, 3.0, 3.5, 4.0]
    # Modulus for span L = 1.5, 2.0, 3.0, 4.0, 5.0 m
    # For standard span L = 2.5 m (interpolated across col 2: L=2.0 and col 3: L=3.0)
    SM_2M = [36.0, 53.0, 71.0, 93.0]
    SM_3M = [82.0, 118.0, 160.0, 209.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "stiff_web_frame") -> InterpolationResult:
        depth = float(inputs.get('depth', inputs.get('D', 5.18)) or 5.18)
        spacing = float(inputs.get('frame_spacing', inputs.get('spacing', 550.0)) or 550.0)
        kz = float(inputs.get('effective_kz', inputs.get('kz', 1.25)) or 1.25)

        # Interpolate across Depth for 2.0m span and 3.0m span, then blend to 2.5m span
        z2, idx1, idx2, lam, is_extrap = cls.interpolate_1d(depth, cls.DEPTH_NODES, cls.SM_2M)
        z3, _, _, _, _ = cls.interpolate_1d(depth, cls.DEPTH_NODES, cls.SM_3M)
        z_base = (z2 + z3) / 2.0

        rreq = round(z_base * kz, 2)

        bounding_cells = [
            {"row": idx1, "col": 2, "val": cls.SM_2M[idx1]},
            {"row": idx2, "col": 2, "val": cls.SM_2M[idx2]},
            {"row": idx1, "col": 3, "val": cls.SM_3M[idx1]},
            {"row": idx2, "col": 3, "val": cls.SM_3M[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=2,
            bounding_cells=bounding_cells,
            interpolated_val=z_base,
            is_extrapolated=is_extrap,
            active_cols=[2, 3]
        )

        derivation = f"Table 19 (D={depth:.2f} m, Span=2.5 m): Base Z={z_base:.1f} cm3 x kz({kz:.2f}) = {rreq:.2f} cm3"

        return InterpolationResult(
            baseline=round(z_base, 2),
            rreq=rreq,
            unit=cls.default_unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 27, Table 19 with 2D interpolation across Depth D and Web Frame Span",
            inputs_used={"D": depth, "kz": kz, "factor": kz},
            bounding_nodes={"D1": cls.DEPTH_NODES[idx1], "D2": cls.DEPTH_NODES[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )
