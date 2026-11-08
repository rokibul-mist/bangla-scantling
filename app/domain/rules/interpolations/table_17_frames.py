"""
Table 17: Side Frames Section Modulus Interpolator.
Statutory Reference: Rule 25, Table 17.
Governing parameters: Moulded Depth D (m) and Frame Spacing s (mm).
"""

from typing import Dict, Any
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table17FramesInterpolator(BaseTableInterpolator):
    table_index = 16
    table_no_str = "Table 17"
    table_title = "Side Frames Section Modulus"
    ref_rule = "Rule 25, Table 17"
    default_unit = "cm³"

    DEPTH_NODES = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0]
    SM_NODES = [15.0, 19.0, 27.0, 46.0, 73.0, 110.0, 155.0, 215.0, 285.0, 365.0, 470.0, 590.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "stiff_side_frame") -> InterpolationResult:
        depth = float(inputs.get('depth', 5.18) or 5.18)
        spacing = float(inputs.get('frame_spacing', 550.0) or 550.0)
        kz = float(inputs.get('effective_kz', 1.25) or 1.25)

        z_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(depth, cls.DEPTH_NODES, cls.SM_NODES)
        z_corr, sp_factor = cls.apply_spacing_correction(z_base, spacing, is_sm=True)
        rreq = round(z_corr * kz, 2)

        bounding_cells = [
            {"row": idx1, "col": 1, "val": cls.SM_NODES[idx1]},
            {"row": idx2, "col": 1, "val": cls.SM_NODES[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=1,
            bounding_cells=bounding_cells,
            interpolated_val=z_corr,
            is_extrapolated=is_extrap
        )

        derivation = (
            f"Table 17 (D={depth:.2f} m, Spacing={spacing:.0f} mm): "
            f"Base Z={cls.SM_NODES[idx1]} + {lam:.3f}*({cls.SM_NODES[idx2]}-{cls.SM_NODES[idx1]}) = {z_base:.1f} cm³"
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
            formula_desc="Rule 25, Table 17 with linear interpolation by Moulded Depth D and spacing correction",
            inputs_used={"D": depth, "frame_spacing": spacing, "kz": kz},
            bounding_nodes={"D1": cls.DEPTH_NODES[idx1], "D2": cls.DEPTH_NODES[idx2], "Z1": cls.SM_NODES[idx1], "Z2": cls.SM_NODES[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=sp_factor,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )
