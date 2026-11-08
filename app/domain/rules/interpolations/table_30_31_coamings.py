"""
Tables 30 & 31: Hatch Coaming Plating Thickness Interpolators.
Statutory Reference: Rule 38, Tables 30 & 31.
Governing parameters: Vessel Length L (m) and Breadth B (m).
"""

from typing import Dict, Any
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table3031CoamingsInterpolator(BaseTableInterpolator):
    table_index = 29  # Table 30: Hatch Coaming Plating Thickness by Vessel Length
    table_no_str = "Table 30"
    table_title = "Hatch Coaming Plating Thickness"
    ref_rule = "Rule 38, Table 30"
    default_unit = "mm"

    L_NODES = [20.0, 30.0, 40.0, 50.0, 60.0, 70.0]
    THK_L = [5.0, 6.0, 7.0, 7.5, 8.0, 8.5]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "plate_coaming_long") -> InterpolationResult:
        lbp = float(inputs.get('lbp', inputs.get('L', 69.85)) or 69.85)
        kt = float(inputs.get('effective_kt', inputs.get('kt', 1.20)) or 1.20)

        t_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(lbp, cls.L_NODES, cls.THK_L)
        rreq = round(t_base * kt, 2)

        bounding_cells = [
            {"row": idx1, "col": 1, "val": cls.THK_L[idx1]},
            {"row": idx2, "col": 1, "val": cls.THK_L[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=1,
            bounding_cells=bounding_cells,
            interpolated_val=t_base,
            is_extrapolated=is_extrap
        )

        derivation = f"Table 30 (L={lbp:.2f} m): Base={cls.THK_L[idx1]} + {lam:.3f}*({cls.THK_L[idx2]}-{cls.THK_L[idx1]}) = {t_base:.2f} mm x kt({kt:.2f}) = {rreq:.2f} mm"

        return InterpolationResult(
            baseline=round(t_base, 2),
            rreq=rreq,
            unit=cls.default_unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 38, Table 30 with linear interpolation by Vessel Length L",
            inputs_used={"L": lbp, "kt": kt, "factor": kt},
            bounding_nodes={"L1": cls.L_NODES[idx1], "L2": cls.L_NODES[idx2], "t1": cls.THK_L[idx1], "t2": cls.THK_L[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )
