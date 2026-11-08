"""
Table 1: Keel & Inner Bottom Plating Thickness and Keel Plate Width Interpolator.
Statutory Reference: Rule 9, Table 1.
Governing parameters: Vessel Length L (m) and Frame Spacing s (mm).
"""

from typing import Dict, Any
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table01KeelInterpolator(BaseTableInterpolator):
    table_index = 0
    table_no_str = "Table 1"
    table_title = "Keel & Inner Bottom Plating Thickness"
    ref_rule = "Rule 9, Table 1"
    default_unit = "mm"

    L_NODES = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0]
    THK_450 = [4.5, 5.0, 5.5, 6.0, 6.5, 7.0]
    THK_500 = [5.0, 5.5, 6.0, 6.5, 7.0, 7.5]
    THK_550 = [5.5, 6.0, 6.5, 7.0, 7.5, 8.0]
    WIDTH_NODES = [850.0, 900.0, 950.0, 1000.0, 1050.0, 1100.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "plate_keel") -> InterpolationResult:
        lbp = float(inputs.get('lbp', 69.85) or 69.85)
        spacing = float(inputs.get('frame_spacing', 550.0) or 550.0)
        kt = float(inputs.get('effective_kt', 1.20) or 1.20)

        # 1. Keel Plate Width Calculation
        if member_id in ["w_keel", "plate_keel_width"]:
            w_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(lbp, cls.L_NODES, cls.WIDTH_NODES)
            w_req = round(w_base, 1)  # Width does not get multiplied by kt
            bounding_cells = [
                {"row": idx1, "col": 4, "val": cls.WIDTH_NODES[idx1]},
                {"row": idx2, "col": 4, "val": cls.WIDTH_NODES[idx2]}
            ]
            t_view = cls.build_table_view(
                active_rows=[idx1, idx2],
                active_col=4,
                bounding_cells=bounding_cells,
                interpolated_val=w_base,
                is_extrapolated=is_extrap
            )
            return InterpolationResult(
                baseline=round(w_base, 1),
                rreq=w_req,
                unit="mm",
                table_no=cls.table_no_str,
                table_title="Keel Plate Width",
                formula_desc="Linear interpolation of Keel Plate Width by Vessel Length L",
                inputs_used={"L": lbp, "factor": 1.00},
                bounding_nodes={"L1": cls.L_NODES[idx1], "L2": cls.L_NODES[idx2], "w1": cls.WIDTH_NODES[idx1], "w2": cls.WIDTH_NODES[idx2]},
                lambda_ratio=round(lam, 4),
                spacing_correction=1.00,
                extrapolated=is_extrap,
                derivation_text=f"Keel Width = {cls.WIDTH_NODES[idx1]} + {lam:.3f} * ({cls.WIDTH_NODES[idx2]} - {cls.WIDTH_NODES[idx1]}) = {w_base:.1f} mm",
                table_view=t_view
            )

        # 2. Thickness Calculation (plate_keel or plate_inner_bottom)
        # Select spacing column: 1 for 450mm, 2 for 500mm, 3 for 550mm
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

        # Frame spacing correction if spacing > 550 mm
        t_corr, sp_factor = cls.apply_spacing_correction(t_base, spacing, is_sm=False)

        # Required thickness
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
            f"Table 1 (L={lbp:.2f} m, Spacing={spacing:.0f} mm): "
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
            formula_desc=f"Rule 9, Table 1 ({col_label}) with linear interpolation by L and spacing correction",
            inputs_used={"L": lbp, "frame_spacing": spacing, "kt": kt},
            bounding_nodes={"L1": cls.L_NODES[idx1], "L2": cls.L_NODES[idx2], "t1": y_nodes[idx1], "t2": y_nodes[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=sp_factor,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )
