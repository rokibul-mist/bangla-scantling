"""
Table 13: Floors / Bottom Framing Section Modulus 3D Interpolator.
Statutory Reference: Rule 21, Table 13.
Governing parameters: Draft d (m), Frame Spacing s (mm), and Moulded Breadth B (m).
"""

from typing import Dict, Any, List, Tuple
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table13FloorsInterpolator(BaseTableInterpolator):
    table_index = 12
    table_no_str = "Table 13"
    table_title = "Floors / Bottom Framing Section Modulus"
    ref_rule = "Rule 21, Table 13"
    default_unit = "cm³"

    # Discrete nodes from schedule_tables.json Table 13
    DRAFT_NODES = [1.0, 1.5, 2.5, 3.0, 3.5, 4.0]
    SPACING_NODES = [450.0, 500.0, 550.0]
    BREADTH_NODES = [2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 12.0]

    # Grid data: 18 rows x 7 breadth columns
    TABLE_GRID = [
        # Draft 1.0
        [8.0, 18.0, 31.0, 70.0, 123.0, 196.0, 280.0],    # row 0: d=1.0, s=450
        [9.0, 20.0, 35.0, 77.0, 138.0, 218.0, 310.0],    # row 1: d=1.0, s=500
        [10.0, 22.0, 38.0, 85.0, 150.0, 235.0, 340.0],   # row 2: d=1.0, s=550
        # Draft 1.5
        [12.0, 26.0, 46.0, 105.0, 185.0, 288.0, 415.0],  # row 3: d=1.5, s=450
        [13.0, 30.0, 52.0, 115.0, 205.0, 320.0, 465.0],  # row 4: d=1.5, s=500
        [15.0, 32.0, 58.0, 128.0, 225.0, 355.0, 510.0],  # row 5: d=1.5, s=550
        # Draft 2.5
        [16.0, 35.0, 62.5, 140.0, 246.0, 385.0, 550.0],  # row 6: d=2.5, s=450
        [22.0, 48.0, 86.0, 194.0, 342.0, 535.0, 770.0],  # row 7: d=2.5, s=500
        [24.0, 53.0, 94.0, 212.0, 375.0, 590.0, 845.0],  # row 8: d=2.5, s=550
        # Draft 3.0
        [23.0, 52.0, 94.0, 208.0, 370.0, 588.0, 830.0],  # row 9: d=3.0, s=450
        [26.0, 58.0, 104.0, 232.0, 410.0, 650.0, 925.0], # row 10: d=3.0, s=500
        [28.0, 65.0, 114.0, 255.0, 450.0, 705.0, 1014.0],# row 11: d=3.0, s=550
        # Draft 3.5
        [27.0, 62.0, 108.0, 242.0, 430.0, 675.0, 968.0], # row 12: d=3.5, s=450
        [30.0, 68.0, 120.0, 270.0, 440.0, 750.0, 1076.0],# row 13: d=3.5, s=500
        [33.0, 75.0, 128.0, 300.0, 526.0, 828.0, 1183.0],# row 14: d=3.5, s=550
        # Draft 4.0
        [30.0, 70.0, 123.0, 278.0, 492.0, 765.0, 1106.0],# row 15: d=4.0, s=450
        [34.0, 78.0, 138.0, 310.0, 548.0, 854.0, 1229.0],# row 16: d=4.0, s=500
        [38.0, 85.0, 150.0, 340.0, 600.0, 935.0, 1352.0],# row 17: d=4.0, s=550
    ]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "stiff_floor_single") -> InterpolationResult:
        draft = float(inputs.get('draft', 4.0) or 4.0)
        spacing = float(inputs.get('frame_spacing', 550.0) or 550.0)
        breadth = float(inputs.get('breadth', 13.41) or 13.41)
        kz = float(inputs.get('effective_kz', 1.25) or 1.25)

        # 1. Draft Bounding Nodes (Draft 1.0 to 4.0)
        _, d_idx1, d_idx2, d_lam, d_extrap = cls.interpolate_1d(draft, cls.DRAFT_NODES, cls.DRAFT_NODES)

        # 2. Spacing Bounding Nodes (450 to 550)
        s_clamped = min(550.0, max(450.0, spacing))
        _, s_idx1, s_idx2, s_lam, _ = cls.interpolate_1d(s_clamped, cls.SPACING_NODES, cls.SPACING_NODES)

        # Helper to get interpolated value for a specific row across Breadth
        def get_row_breadth_val(r_idx: int) -> Tuple[float, int, int, float, bool]:
            row_vals = cls.TABLE_GRID[r_idx]
            return cls.interpolate_1d(breadth, cls.BREADTH_NODES, row_vals)

        # Compute values for the 4 bounding rows
        row_d1_s1 = d_idx1 * 3 + s_idx1
        row_d1_s2 = d_idx1 * 3 + s_idx2
        row_d2_s1 = d_idx2 * 3 + s_idx1
        row_d2_s2 = d_idx2 * 3 + s_idx2

        v_d1_s1, b_idx1, b_idx2, b_lam, b_extrap = get_row_breadth_val(row_d1_s1)
        v_d1_s2, _, _, _, _ = get_row_breadth_val(row_d1_s2)
        v_d2_s1, _, _, _, _ = get_row_breadth_val(row_d2_s1)
        v_d2_s2, _, _, _, _ = get_row_breadth_val(row_d2_s2)

        # Blend across spacing
        v_d1 = v_d1_s1 + s_lam * (v_d1_s2 - v_d1_s1)
        v_d2 = v_d2_s1 + s_lam * (v_d2_s2 - v_d2_s1)

        # Blend across draft
        base_sm = v_d1 + d_lam * (v_d2 - v_d1)

        # Apply spacing correction if spacing > 550 mm
        corr_sm, sp_factor = cls.apply_spacing_correction(base_sm, spacing, is_sm=True)

        # Statutory Required Section Modulus
        rreq = round(corr_sm * kz, 2)

        # Identify active rows for table visualization
        active_rows = sorted(list(set([row_d1_s1, row_d1_s2, row_d2_s1, row_d2_s2])))
        # Active columns in table: Breadth columns start at col index 2
        active_cols = [2 + b_idx1, 2 + b_idx2] if b_idx1 != b_idx2 else [2 + b_idx1]
        active_col = 2 + b_idx2

        bounding_cells = [
            {"row": r, "col": 2 + b_idx1, "val": cls.TABLE_GRID[r][b_idx1]} for r in active_rows
        ] + [
            {"row": r, "col": 2 + b_idx2, "val": cls.TABLE_GRID[r][b_idx2]} for r in active_rows
        ]

        is_extrap = d_extrap or b_extrap

        t_view = cls.build_table_view(
            active_rows=active_rows,
            active_col=active_col,
            bounding_cells=bounding_cells,
            interpolated_val=corr_sm,
            is_extrapolated=is_extrap,
            active_cols=active_cols
        )

        derivation = (
            f"Table 13 3D Interpolation (d={draft:.2f} m, B={breadth:.2f} m, s={spacing:.0f} mm): "
            f"Base Z={base_sm:.1f} cm³"
        )
        if sp_factor > 1.0:
            derivation += f" x Spacing Corr({sp_factor:.3f}) = {corr_sm:.1f} cm³"
        derivation += f" x kz({kz:.2f}) = {rreq:.2f} cm³"

        return InterpolationResult(
            baseline=round(corr_sm, 2),
            rreq=rreq,
            unit=cls.default_unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 21, Table 13 3D Interpolation across (Draft, Frame Spacing, Breadth)",
            inputs_used={"d": draft, "B": breadth, "frame_spacing": spacing, "kz": kz},
            bounding_nodes={
                "d1": cls.DRAFT_NODES[d_idx1], "d2": cls.DRAFT_NODES[d_idx2],
                "B1": cls.BREADTH_NODES[b_idx1], "B2": cls.BREADTH_NODES[b_idx2],
                "s1": cls.SPACING_NODES[s_idx1], "s2": cls.SPACING_NODES[s_idx2]
            },
            lambda_ratio=round(b_lam, 4),
            spacing_correction=sp_factor,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )
