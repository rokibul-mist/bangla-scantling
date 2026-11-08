"""
Table 24: Collision Bulkhead Position Bounds Interpolator.
Statutory Reference: Rule 32, Table 24.
Governing parameters: Vessel Length L (m).
"""

from typing import Dict, Any
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table24CollisionBhdInterpolator(BaseTableInterpolator):
    table_index = 23  # Table 24: Collision Bulkhead Position
    table_no_str = "Table 24"
    table_title = "Collision Bulkhead Position"
    ref_rule = "Rule 32, Table 24"
    default_unit = "m"

    L_NODES = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0]
    MIN_POS = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5]  # 0.05 * L
    MAX_POS = [1.6, 2.4, 3.2, 4.0, 4.8, 5.6]  # 0.08 * L

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "bhd_collision_pos") -> InterpolationResult:
        lbp = float(inputs.get('lbp', 69.85) or 69.85)

        min_p, idx1, idx2, lam, is_extrap = cls.interpolate_1d(lbp, cls.L_NODES, cls.MIN_POS)
        max_p, _, _, _, _ = cls.interpolate_1d(lbp, cls.L_NODES, cls.MAX_POS)

        bounding_cells = [
            {"row": idx1, "col": 1, "val": cls.MIN_POS[idx1]},
            {"row": idx2, "col": 1, "val": cls.MIN_POS[idx2]},
            {"row": idx1, "col": 2, "val": cls.MAX_POS[idx1]},
            {"row": idx2, "col": 2, "val": cls.MAX_POS[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=1,
            bounding_cells=bounding_cells,
            interpolated_val=min_p,
            is_extrapolated=is_extrap
        )

        derivation = f"Table 24 (L={lbp:.2f} m): Minimum 0.05L = {min_p:.2f} m | Maximum 0.08L = {max_p:.2f} m from FP"

        return InterpolationResult(
            baseline=round(min_p, 2),
            rreq=round(min_p, 2),
            unit=cls.default_unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 32, Table 24: Collision Bulkhead 0.05L to 0.08L from Fore Peak",
            inputs_used={"L": lbp},
            bounding_nodes={"L1": cls.L_NODES[idx1], "L2": cls.L_NODES[idx2], "min1": cls.MIN_POS[idx1], "max1": cls.MAX_POS[idx1]},
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )
