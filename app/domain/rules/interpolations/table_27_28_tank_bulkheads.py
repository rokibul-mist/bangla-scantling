"""
Tables 27 & 28: Deep Tank Bulkheads Plating & Stiffeners Interpolator.
Statutory Reference: Rule 38, Tables 27 & 28.
Governing parameters: Tank Head / Height h (m) and Frame Spacing s (mm).
"""

from typing import Dict, Any
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table2728TankBulkheadsInterpolator(BaseTableInterpolator):
    table_index = 26  # Table 27 Plating
    table_no_str = "Table 27"
    table_title = "Hull Tank Bulkhead Plating & Stiffeners"
    ref_rule = "Rule 38, Tables 27 & 28"
    default_unit = "mm"

    HEIGHT_NODES = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
    # Tank Plating thickness (550 mm spacing, Col 3)
    PL_THK_550 = [4.0, 4.5, 4.5, 5.0, 5.5, 5.5, 6.0, 6.0]
    # Tank Stiffener Section Modulus (550 mm spacing, Col 3)
    STIFF_SM_550 = [13.0, 28.0, 47.0, 80.0, 120.0, 180.0, 255.0, 345.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "plate_bhd_tank") -> InterpolationResult:
        depth = float(inputs.get('depth', 5.18) or 5.18)
        spacing = float(inputs.get('frame_spacing', 550.0) or 550.0)
        kt = float(inputs.get('effective_kt', 1.20) or 1.20)
        kz = float(inputs.get('effective_kz', 1.25) or 1.25)

        is_stiffener = "stiff" in member_id
        if is_stiffener:
            cls.table_index = 27
            cls.table_no_str = "Table 28"
            cls.table_title = "Tank Bulkhead Stiffeners Section Modulus"
            cls.ref_rule = "Rule 38, Table 28"
            y_nodes = cls.STIFF_SM_550
            factor = kz
            unit = "cm³"
        else:
            cls.table_index = 26
            cls.table_no_str = "Table 27"
            cls.table_title = "Hull Tank Bulkhead Plating Thickness"
            cls.ref_rule = "Rule 38, Table 27"
            y_nodes = cls.PL_THK_550
            factor = kt
            unit = "mm"

        col_idx = 3
        val_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(depth, cls.HEIGHT_NODES, y_nodes)
        val_corr, sp_factor = cls.apply_spacing_correction(val_base, spacing, is_sm=is_stiffener)
        rreq = round(val_corr * factor, 2)

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
            f"{cls.table_no_str} (h={depth:.2f} m, Spacing={spacing:.0f} mm): "
            f"Base={val_base:.2f}{unit}, spacing_corr={sp_factor:.3f} -> "
            f"Required={rreq:.2f} {unit} (Factor={factor:.2f})."
        )

        return InterpolationResult(
            baseline=round(val_base, 2),
            rreq=rreq,
            unit=unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc=f"{cls.ref_rule} (h, s)",
            inputs_used={"height": depth, "spacing": spacing, "factor": factor},
            bounding_nodes={
                "lower": {"h": cls.HEIGHT_NODES[idx1], "val": y_nodes[idx1]},
                "upper": {"h": cls.HEIGHT_NODES[idx2], "val": y_nodes[idx2]}
            },
            lambda_ratio=round(lam, 4),
            spacing_correction=sp_factor,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )
