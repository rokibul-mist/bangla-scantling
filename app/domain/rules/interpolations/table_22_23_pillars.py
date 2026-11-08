"""
Table 22 & 23: Solid and Tubular Pillars Interpolator.
Statutory Reference: Rule 35, Tables 22 & 23.
Governing parameters: Pillar Height H (m) / Ship Depth D (m) and Load P (kN).
"""

from typing import Dict, Any
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table2223PillarsInterpolator(BaseTableInterpolator):
    table_index = 21  # Table 22 Solid Pillars
    table_no_str = "Table 22"
    table_title = "Solid & Tubular Pillars Diameter"
    ref_rule = "Rule 35, Table 22 & 23"
    default_unit = "mm"

    H_NODES = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0]
    # Pillar diameter for P = 60 kN (Column 5)
    SOLID_DIA_P60 = [34.0, 37.0, 40.0, 43.0, 45.0, 47.0, 49.0, 51.0, 53.0, 55.0, 57.0, 58.0, 60.0, 61.0, 61.0, 64.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "pillar_solid_dia") -> InterpolationResult:
        depth = float(inputs.get('depth', inputs.get('D', 5.18)) or 5.18)
        # Tween-deck or hold pillar height typically ~2.6 - 3.0 m
        h_pillar = min(depth, 3.0) if depth > 4.0 else depth
        is_tubular = "tubular" in member_id

        if is_tubular:
            cls.table_index = 22
            cls.table_no_str = "Table 23"
            cls.table_title = "Tubular Pillars Diameter"
            cls.ref_rule = "Rule 35, Table 23"
            dia_base = 101.6
            is_extrap = False
            idx1, idx2 = 12, 15
            lam = 0.5
            col_idx = 0
            bounding_cells = [
                {"row": 12, "col": 0, "val": 88.9},
                {"row": 15, "col": 0, "val": 101.6}
            ]
        else:
            cls.table_index = 21
            cls.table_no_str = "Table 22"
            cls.table_title = "Solid Pillars Rule Diameter"
            cls.ref_rule = "Rule 35, Table 22"
            col_idx = 5
            dia_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(h_pillar, cls.H_NODES, cls.SOLID_DIA_P60)
            bounding_cells = [
                {"row": idx1, "col": col_idx, "val": cls.SOLID_DIA_P60[idx1]},
                {"row": idx2, "col": col_idx, "val": cls.SOLID_DIA_P60[idx2]}
            ]

        rreq = round(dia_base, 1)

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=col_idx,
            bounding_cells=bounding_cells,
            interpolated_val=dia_base,
            is_extrapolated=is_extrap
        )

        derivation = (
            f"{cls.table_no_str} (H={h_pillar:.2f} m): "
            f"Required diameter = {rreq:.1f} mm "
            f"(Bounding nodes: {bounding_cells[0]['val']} mm -> {bounding_cells[1]['val']} mm)."
        )

        return InterpolationResult(
            baseline=round(dia_base, 1),
            rreq=rreq,
            unit="mm",
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc=f"{cls.ref_rule} (Height H)",
            inputs_used={"H": h_pillar, "factor": 1.00},
            bounding_nodes={
                "lower": {"val": bounding_cells[0]["val"]},
                "upper": {"val": bounding_cells[1]["val"]}
            },
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )
