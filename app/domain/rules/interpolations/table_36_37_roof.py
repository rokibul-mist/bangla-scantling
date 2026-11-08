"""
Tables 36 - 37: Superstructure Roof Beams & Girders Interpolators.
Statutory Reference: Rules 44 - 45, Tables 36 - 37.
Governing parameters: Span L (m) and Spacing S (mm or m).
"""

from typing import Dict, Any, List
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table36RoofBeamsInterpolator(BaseTableInterpolator):
    table_index = 36  # Table 36: Deck Beams & Longitudinals Section Modulus for All Deck Classes
    table_no_str = "Table 36"
    table_title = "Deck Beams & Longitudinals Section Modulus for All Deck Classes"
    ref_rule = "Rule 44, Table 36"
    default_unit = "cm3"

    SPAN_NODES = [1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0]
    SPACING_NODES = [450.0, 500.0, 550.0]

    TABLE_GRID = [
        [6.0, 6.0, 7.0],
        [7.0, 8.0, 8.0],
        [12.0, 12.0, 13.0],
        [17.0, 19.0, 20.0],
        [25.0, 27.0, 30.0],
        [33.0, 38.0, 40.0],
        [44.0, 48.0, 54.0],
        [56.0, 62.0, 68.0],
        [70.0, 77.0, 84.0],
        [85.0, 94.0, 104.0],
        [102.0, 113.0, 124.0],
        [121.0, 135.0, 150.0]
    ]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "stiff_roof_beam") -> InterpolationResult:
        span = float(inputs.get('roof_beam_span') or inputs.get('beam_span') or 3.5)
        spacing = float(inputs.get('frame_spacing') or 500.0)
        kz = float(inputs.get('effective_kz') or inputs.get('kz') or 1.40)

        # Interpolate across span
        _, l_idx1, l_idx2, l_lam, is_extrap = cls.interpolate_1d(span, cls.SPAN_NODES, cls.SPAN_NODES)
        s_clamped = min(550.0, max(450.0, spacing))
        _, s_idx1, s_idx2, s_lam, _ = cls.interpolate_1d(s_clamped, cls.SPACING_NODES, cls.SPACING_NODES)

        v1 = cls.TABLE_GRID[l_idx1][s_idx1] + s_lam * (cls.TABLE_GRID[l_idx1][s_idx2] - cls.TABLE_GRID[l_idx1][s_idx1])
        v2 = cls.TABLE_GRID[l_idx2][s_idx1] + s_lam * (cls.TABLE_GRID[l_idx2][s_idx2] - cls.TABLE_GRID[l_idx2][s_idx1])
        base_sm = v1 + l_lam * (v2 - v1)

        corr_sm, sp_factor = cls.apply_spacing_correction(base_sm, spacing, is_sm=True)
        rreq = round(corr_sm * kz, 2)

        bounding_cells = [
            {"row": l_idx1, "col": 1 + s_idx1, "val": cls.TABLE_GRID[l_idx1][s_idx1]},
            {"row": l_idx1, "col": 1 + s_idx2, "val": cls.TABLE_GRID[l_idx1][s_idx2]},
            {"row": l_idx2, "col": 1 + s_idx1, "val": cls.TABLE_GRID[l_idx2][s_idx1]},
            {"row": l_idx2, "col": 1 + s_idx2, "val": cls.TABLE_GRID[l_idx2][s_idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[l_idx1, l_idx2],
            active_col=1 + s_idx2,
            active_cols=[1 + s_idx1, 1 + s_idx2] if s_idx1 != s_idx2 else [1 + s_idx1],
            bounding_cells=bounding_cells,
            interpolated_val=corr_sm,
            is_extrapolated=is_extrap
        )

        derivation = f"Table 36 (Span={span:.2f} m, Spacing={spacing:.0f} mm): Base={base_sm:.1f} cm3 x kz({kz:.2f}) = {rreq:.2f} cm3"

        return InterpolationResult(
            baseline=round(corr_sm, 2),
            rreq=rreq,
            unit=cls.default_unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 44, Table 36 Superstructure Roof Beams Section Modulus",
            inputs_used={"span": span, "spacing": spacing, "kz": kz},
            bounding_nodes={"L1": cls.SPAN_NODES[l_idx1], "L2": cls.SPAN_NODES[l_idx2]},
            lambda_ratio=round(l_lam, 4),
            spacing_correction=sp_factor,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )


class Table37RoofGirdersInterpolator(BaseTableInterpolator):
    table_index = 37  # Table 37: Deck Girders Section Modulus
    table_no_str = "Table 37"
    table_title = "Deck Girders Section Modulus"
    ref_rule = "Rule 45, Table 37"
    default_unit = "cm3"

    SPAN_NODES = [2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 14.0]
    SPACING_NODES = [2.0, 2.4, 2.8, 3.2]

    TABLE_GRID = [
        [16.0, 19.0, 24.0, 26.0],
        [38.0, 46.0, 54.0, 62.0],
        [64.0, 80.0, 91.0, 104.0],
        [105.0, 125.0, 145.0, 165.0],
        [146.0, 175.0, 205.0, 235.0],
        [260.0, 315.0, 370.0, 420.0],
        [405.0, 490.0, 570.0, 650.0],
        [590.0, 700.0, 820.0, 950.0],
        [800.0, 960.0, 1120.0, 1270.0]
    ]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "stiff_roof_girder_side") -> InterpolationResult:
        # Default span: Centre Girder 4.0m, Side Girder 3.5m
        is_centre = ("centre" in member_id)
        default_span = 4.0 if is_centre else 3.5
        span = float(inputs.get('roof_girder_span') or default_span)
        spacing = float(inputs.get('roof_girder_spacing') or 2.4)
        kz = float(inputs.get('effective_kz') or inputs.get('kz') or 1.40)

        _, l_idx1, l_idx2, l_lam, is_extrap = cls.interpolate_1d(span, cls.SPAN_NODES, cls.SPAN_NODES)
        s_clamped = min(3.2, max(2.0, spacing))
        _, s_idx1, s_idx2, s_lam, _ = cls.interpolate_1d(s_clamped, cls.SPACING_NODES, cls.SPACING_NODES)

        v1 = cls.TABLE_GRID[l_idx1][s_idx1] + s_lam * (cls.TABLE_GRID[l_idx1][s_idx2] - cls.TABLE_GRID[l_idx1][s_idx1])
        v2 = cls.TABLE_GRID[l_idx2][s_idx1] + s_lam * (cls.TABLE_GRID[l_idx2][s_idx2] - cls.TABLE_GRID[l_idx2][s_idx1])
        base_sm = v1 + l_lam * (v2 - v1)

        rreq = round(base_sm * kz, 2)

        bounding_cells = [
            {"row": l_idx1, "col": 1 + s_idx1, "val": cls.TABLE_GRID[l_idx1][s_idx1]},
            {"row": l_idx1, "col": 1 + s_idx2, "val": cls.TABLE_GRID[l_idx1][s_idx2]},
            {"row": l_idx2, "col": 1 + s_idx1, "val": cls.TABLE_GRID[l_idx2][s_idx1]},
            {"row": l_idx2, "col": 1 + s_idx2, "val": cls.TABLE_GRID[l_idx2][s_idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[l_idx1, l_idx2],
            active_col=1 + s_idx2,
            active_cols=[1 + s_idx1, 1 + s_idx2] if s_idx1 != s_idx2 else [1 + s_idx1],
            bounding_cells=bounding_cells,
            interpolated_val=base_sm,
            is_extrapolated=is_extrap
        )

        girder_type = "Centre Roof Girder" if is_centre else "Side Roof Girder"
        derivation = f"Table 37 ({girder_type}, Span={span:.2f} m, Spacing={spacing:.1f} m): Base={base_sm:.1f} cm3 x kz({kz:.2f}) = {rreq:.2f} cm3"

        return InterpolationResult(
            baseline=round(base_sm, 2),
            rreq=rreq,
            unit=cls.default_unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 45, Table 37 Superstructure Roof Girders Section Modulus",
            inputs_used={"span": span, "spacing": spacing, "kz": kz},
            bounding_nodes={"L1": cls.SPAN_NODES[l_idx1], "L2": cls.SPAN_NODES[l_idx2]},
            lambda_ratio=round(l_lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )
