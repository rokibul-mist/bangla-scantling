"""
Rule 8(1): Minimum Hull Plate Material Interpolator / Statutory Rule Evaluator.
Statutory Reference: Rule 8(1) - Minimum Thickness of Hull Plating.
Governing parameter: Statutory multiplier factor kt.
"""

from typing import Dict, Any
from .base_interpolator import BaseTableInterpolator, InterpolationResult, TableViewData


class Table00Rule08MinPlateInterpolator(BaseTableInterpolator):
    table_index = 0
    table_no_str = "Rule 8(1)"
    table_title = "Minimum Hull Plate Material"
    ref_rule = "Rule 8(1) - Statutory Minimum Hull Plating"
    default_unit = "mm"

    BASE_PLATE_THK = 4.0

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "mat_min_hull") -> InterpolationResult:
        kt = float(inputs.get('effective_kt', inputs.get('kt', 1.40)) or 1.40)
        baseline = cls.BASE_PLATE_THK
        rreq = round(baseline * kt, 2)

        # Statutory schedule display for Rule 8(1)
        headers = ["Statutory Rule Category", "Baseline Scantling (mm)", "Statutory Factor (kt)", "Rule Minimum Required (mm)"]
        rows = [
            ["Mild Steel Hull Shell Plating - Rule 8(1)", "4.0", f"{kt:.2f}", f"{round(4.0 * kt, 2):.2f}"],
            ["Heavy Strakes & High-Stress Zone Plates", "5.0", f"{kt:.2f}", f"{round(5.0 * kt, 2):.2f}"],
            ["Lightweight Non-Structural Enclosures", "3.0", f"{kt:.2f}", f"{round(3.0 * kt, 2):.2f}"]
        ]

        bounding_cells = [
            {"row": 0, "col": 1, "val": 4.0},
            {"row": 0, "col": 2, "val": kt},
            {"row": 0, "col": 3, "val": rreq}
        ]

        t_view = TableViewData(
            table_id="rule_08_min_plate",
            table_no=cls.table_no_str,
            title=cls.table_title,
            ref=cls.ref_rule,
            headers=headers,
            rows=rows,
            active_row_indices=[0],
            active_col_index=3,
            bounding_cells=bounding_cells,
            extrapolated=False,
            interpolated_value=rreq,
            notes="Statutory Rule 8(1): Baseline 4.0 mm multiplied by vessel statutory service factor kt."
        )

        derivation_text = f"Rule 8(1) Minimum Hull Plating: Baseline = {baseline:.1f} mm × kt ({kt:.2f}) = {rreq:.2f} mm."

        return InterpolationResult(
            baseline=baseline,
            rreq=rreq,
            unit="mm",
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 8(1) Baseline Plate Thickness evaluated with statutory factor kt",
            inputs_used={"baseline": baseline, "kt": kt},
            bounding_nodes={"t_base": baseline, "kt": kt, "t_req": rreq},
            lambda_ratio=0.0,
            spacing_correction=1.00,
            extrapolated=False,
            derivation_text=derivation_text,
            table_view=t_view
        )
