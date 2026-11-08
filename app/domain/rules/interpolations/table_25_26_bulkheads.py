"""
Tables 25 & 26: Collision & Watertight Bulkheads Plating & Stiffeners Interpolator.
Statutory Reference: Rules 33 & 34, Tables 25 & 26.
Governing parameters: Bulkhead Height h (m) and Frame Spacing s (mm).
"""

from typing import Dict, Any
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table2526BulkheadsInterpolator(BaseTableInterpolator):
    table_index = 25  # Table 26: Other Watertight Bulkheads
    table_no_str = "Table 26"
    table_title = "Watertight Bulkhead Plating & Stiffeners"
    ref_rule = "Rule 34, Table 26"
    default_unit = "mm"

    HEIGHT_NODES = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]

    # Table 26: Other Watertight Bulkheads (col 3: 550mm thk, col 6: 550mm sm)
    PL_THK_550 = [4.0, 4.0, 4.0, 4.0, 5.0, 5.0, 5.5, 5.5]
    STIFF_SM_550 = [11.0, 21.0, 38.0, 64.0, 95.0, 140.0, 200.0, 275.0]

    # Table 25: Collision & After Peak Bulkheads (col 3: 550mm thk, col 6: 550mm sm)
    PL_THK_550_COLLISION = [4.0, 4.5, 4.5, 5.0, 5.5, 5.5, 6.0, 6.0]
    STIFF_SM_550_COLLISION = [13.0, 28.0, 47.0, 80.0, 120.0, 180.0, 255.0, 345.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "plate_bhd_wt") -> InterpolationResult:
        depth = float(inputs.get('depth', inputs.get('D', 5.18)) or 5.18)
        spacing = float(inputs.get('frame_spacing', inputs.get('spacing', 550.0)) or 550.0)
        kt = float(inputs.get('effective_kt', inputs.get('kt', 1.20)) or 1.20)
        kz = float(inputs.get('effective_kz', inputs.get('kz', 1.25)) or 1.25)

        is_stiffener = "stiff" in member_id
        is_collision = "collision" in member_id or "aft_peak" in member_id

        if is_collision:
            cls.table_index = 24
            cls.table_no_str = "Table 25"
            cls.table_title = "Collision & After Peak Bulkheads Plating & Stiffeners"
            cls.ref_rule = "Rule 33, Table 25"
            y_nodes = cls.STIFF_SM_550_COLLISION if is_stiffener else cls.PL_THK_550_COLLISION
        else:
            cls.table_index = 25
            cls.table_no_str = "Table 26"
            cls.table_title = "Watertight Bulkhead Plating & Stiffeners"
            cls.ref_rule = "Rule 34, Table 26"
            y_nodes = cls.STIFF_SM_550 if is_stiffener else cls.PL_THK_550

        col_idx = 6 if is_stiffener else 3
        factor = kz if is_stiffener else kt
        unit = "cm3" if is_stiffener else "mm"

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

        derivation = f"{cls.table_no_str} (Height={depth:.2f} m, Spacing={spacing:.0f} mm): Base={val_base:.2f} {unit}"
        if sp_factor > 1.0:
            derivation += f" x Spacing Corr({sp_factor:.3f}) = {val_corr:.2f} {unit}"
        derivation += f" x factor({factor:.2f}) = {rreq:.2f} {unit}"

        return InterpolationResult(
            baseline=round(val_corr, 2),
            rreq=rreq,
            unit=unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc=f"{cls.ref_rule} with linear interpolation by Height h and spacing correction",
            inputs_used={"h": depth, "frame_spacing": spacing, "factor": factor, "kt": kt, "kz": kz},
            bounding_nodes={"h1": cls.HEIGHT_NODES[idx1], "h2": cls.HEIGHT_NODES[idx2], "val1": y_nodes[idx1], "val2": y_nodes[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=sp_factor,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )
