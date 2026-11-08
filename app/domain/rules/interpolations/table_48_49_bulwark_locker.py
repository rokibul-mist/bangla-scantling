"""
Tables 47 & 48: Bulwark Plating & Bow Chain Locker Wall Plating Interpolator.
Statutory Reference: Rules 50 & 51, Tables 47 & 48.
Governing parameters: Vessel Length L (m).
"""

from typing import Dict, Any
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table4748BulwarkLockerInterpolator(BaseTableInterpolator):
    table_index = 47  # Table 47: Bulwark Plating Thickness
    table_no_str = "Table 47"
    table_title = "Bulwark Plating Thickness"
    ref_rule = "Rule 50, Table 47"
    default_unit = "mm"

    # Table 47 Bulwark Plating L nodes & values
    BULWARK_L_NODES = [20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 70.0]
    BULWARK_THK = [3.0, 3.5, 4.0, 4.0, 4.5, 4.5, 5.0, 5.0, 5.5, 6.0]

    # Table 48 Chain Locker Wall Plating L nodes & values
    LOCKER_L_NODES = [50.0, 55.0, 60.0, 65.0, 70.0]
    LOCKER_THK = [5.5, 6.0, 6.0, 6.5, 7.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "plate_bulwark") -> InterpolationResult:
        lbp = float(inputs.get('lbp', 69.85) or 69.85)
        kt = float(inputs.get('effective_kt', 1.20) or 1.20)

        is_locker = "locker" in member_id
        if is_locker:
            cls.table_index = 48
            cls.table_no_str = "Table 48"
            cls.table_title = "Bow Chain Locker Wall Plating Thickness"
            cls.ref_rule = "Rule 51, Table 48"
            x_nodes = cls.LOCKER_L_NODES
            y_nodes = cls.LOCKER_THK
        else:
            cls.table_index = 47
            cls.table_no_str = "Table 47"
            cls.table_title = "Bulwark Plating Thickness"
            cls.ref_rule = "Rule 50, Table 47"
            x_nodes = cls.BULWARK_L_NODES
            y_nodes = cls.BULWARK_THK

        col_idx = 1
        t_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(lbp, x_nodes, y_nodes)
        # Secondary outfitting plating typically minimum rule thickness
        rreq = round(t_base, 2)

        bounding_cells = [
            {"row": idx1, "col": col_idx, "val": y_nodes[idx1]},
            {"row": idx2, "col": col_idx, "val": y_nodes[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=col_idx,
            bounding_cells=bounding_cells,
            interpolated_val=t_base,
            is_extrapolated=is_extrap
        )

        derivation = (
            f"{cls.table_no_str} (L={lbp:.2f} m): "
            f"Required Thickness = {rreq:.2f} mm "
            f"(Bounding nodes: L={x_nodes[idx1]}m -> {y_nodes[idx1]} mm, "
            f"L={x_nodes[idx2]}m -> {y_nodes[idx2]} mm)."
        )

        return InterpolationResult(
            baseline=round(t_base, 2),
            rreq=rreq,
            unit="mm",
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc=f"{cls.ref_rule} (Length L)",
            inputs_used={"L": lbp, "factor": 1.00},
            bounding_nodes={
                "lower": {"L": x_nodes[idx1], "t": y_nodes[idx1]},
                "upper": {"L": x_nodes[idx2], "t": y_nodes[idx2]}
            },
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )
