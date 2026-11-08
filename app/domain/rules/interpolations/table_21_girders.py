"""
Table 21: Deck Girders Section Modulus Interpolator.
Statutory Reference: Rule 29, Table 21.
Governing parameters: Deck Mean Breadth (m) and Unsupported Span (m).
"""

from typing import Dict, Any
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table21GirdersInterpolator(BaseTableInterpolator):
    table_index = 20  # Table 21: Deck Girders Section Modulus
    table_no_str = "Table 21"
    table_title = "Deck Girders Section Modulus"
    ref_rule = "Rule 29, Table 21"
    default_unit = "cm3"

    BREADTH_NODES = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    # Modulus for span = 3.0 m, 4.0 m, 5.0 m (standard 3.5m span between pillars)
    SPAN3_NODES = [240.0, 305.0, 375.0, 450.0, 520.0, 590.0]
    SPAN4_NODES = [400.0, 530.0, 655.0, 785.0, 910.0, 1040.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "stiff_deck_girder") -> InterpolationResult:
        breadth = float(inputs.get('breadth', inputs.get('B', 13.41)) or 13.41)
        mean_b = min(8.0, max(3.0, breadth * 0.4))
        kz = float(inputs.get('effective_kz', inputs.get('kz', 1.25)) or 1.25)

        z3, idx1, idx2, lam, is_extrap = cls.interpolate_1d(mean_b, cls.BREADTH_NODES, cls.SPAN3_NODES)
        z4, _, _, _, _ = cls.interpolate_1d(mean_b, cls.BREADTH_NODES, cls.SPAN4_NODES)
        z_base = (z3 + z4) / 2.0  # 3.5 m span

        rreq = round(z_base * kz, 2)

        bounding_cells = [
            {"row": idx1, "col": 3, "val": cls.SPAN3_NODES[idx1]},
            {"row": idx2, "col": 3, "val": cls.SPAN3_NODES[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=3,
            bounding_cells=bounding_cells,
            interpolated_val=z_base,
            is_extrapolated=is_extrap
        )

        derivation = f"Table 21 (Mean Breadth={mean_b:.1f} m, Span=3.5 m): Base Z={z_base:.1f} cm3 x kz({kz:.2f}) = {rreq:.2f} cm3"

        return InterpolationResult(
            baseline=round(z_base, 2),
            rreq=rreq,
            unit=cls.default_unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 29, Table 21 with 2D interpolation across Deck Breadth and Girder Span",
            inputs_used={"breadth": breadth, "kz": kz, "factor": kz},
            bounding_nodes={"B1": cls.BREADTH_NODES[idx1], "B2": cls.BREADTH_NODES[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )


class Table29DeckWebBeamsInterpolator(BaseTableInterpolator):
    table_index = 28  # Rule 29
    table_no_str = "Rule 29"
    table_title = "Strength Deck Transverse Web Beams (Rule 29: 2 x Z_beam)"
    ref_rule = "Rule 29, Table 20"
    default_unit = "cm³"

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "stiff_deck_web_beam") -> InterpolationResult:
        # Evaluate ordinary deck beam from Table 20 first
        from .table_20_beams import Table20BeamsInterpolator
        beam_res = Table20BeamsInterpolator.interpolate(inputs, "stiff_deck_beam")
        
        # Rule 29 statutory multiplier: Z_web >= 2.0 * Z_beam
        kz = float(inputs.get('effective_kz', inputs.get('kz', 1.25)) or 1.25)
        base_sm = round(beam_res.baseline * 2.0, 2)
        rreq = round(beam_res.rreq * 2.0, 2)

        derivation = (
            f"Rule 29 (Deck Web Beam): Z_web = 2 x Z_beam = 2 x {beam_res.baseline:.2f} cm³ = {base_sm:.2f} cm³ "
            f"x kz({kz:.2f}) = {rreq:.2f} cm³"
        )

        return InterpolationResult(
            baseline=base_sm,
            rreq=rreq,
            unit=cls.default_unit,
            table_no="Rule 29, Table 20",
            table_title="Deck Web Beams Section Modulus",
            formula_desc="Rule 29: Section modulus shall not be less than twice the ordinary deck beam (2 x Z_beam)",
            inputs_used={"z_beam_base": beam_res.baseline, "z_beam_rreq": beam_res.rreq, "kz": kz},
            bounding_nodes={"multiplier": 2.0},
            lambda_ratio=2.0,
            spacing_correction=beam_res.spacing_correction,
            extrapolated=False,
            derivation_text=derivation,
            table_view=beam_res.table_view
        )

