"""
Tables 45 & 46: Anchors, Cables & Equipment Number Interpolator.
Statutory Reference: Rules 48 & 49, Tables 45 & 46.
Governing parameters: Equipment Number Z or Vessel Length L (m).
"""

from typing import Dict, Any
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table4546EquipmentInterpolator(BaseTableInterpolator):
    table_index = 45  # Table 45: Anchors and Ropes Scantlings
    table_no_str = "Table 45"
    table_title = "Anchors & Ropes Scantlings"
    ref_rule = "Rule 48, Table 45"
    default_unit = "kg"

    # Equipment Num Z nodes (col 0)
    Z_NODES = [30.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 400.0, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0]
    # Main Anchor Mass in kg (col 1)
    ANCHOR_MASS_NODES = [75.0, 90.0, 180.0, 270.0, 360.0, 450.0, 540.0, 670.0, 790.0, 920.0, 1040.0, 1170.0, 1280.0, 1390.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "anchor_mass") -> InterpolationResult:
        lbp = float(inputs.get('lbp', 69.85) or 69.85)
        breadth = float(inputs.get('breadth', 12.0) or 12.0)
        depth = float(inputs.get('depth', 5.18) or 5.18)
        draft = float(inputs.get('draft', 3.5) or 3.5)
        cb = float(inputs.get('cb', 0.82) or 0.82)

        # Statutory Equipment Number formula:
        # Delta = L * B * d * Cb * 1.025
        delta = lbp * breadth * draft * cb * 1.025
        fb = max(0.5, depth - draft)
        h_deck = 2.4
        a_profile = (fb * lbp) + (h_deck * lbp * 0.25)
        calc_z = (delta ** (2.0 / 3.0)) + (2.0 * breadth * (fb + h_deck)) + (a_profile / 10.0)

        if member_id == "chain_cable_length":
            cls.table_index = 46
            cls.table_no_str = "Table 46"
            cls.table_title = "Anchor Chain Cable Dimensions"
            cls.ref_rule = "Rule 49, Table 46"
            chain_len = 220.0 if lbp < 50.0 else (275.0 if lbp < 75.0 else 330.0)
            t_view = cls.build_table_view(
                active_rows=[6, 7],
                active_col=0,
                bounding_cells=[{"row": 6, "col": 0, "val": 22.0}, {"row": 7, "col": 0, "val": 24.0}],
                interpolated_val=chain_len,
                is_extrapolated=False
            )
            return InterpolationResult(
                baseline=chain_len,
                rreq=chain_len,
                unit="m",
                table_no=cls.table_no_str,
                table_title=cls.table_title,
                formula_desc=f"{cls.ref_rule} statutory chain cable length",
                inputs_used={"L": lbp, "Z": round(calc_z, 1)},
                bounding_nodes={"lower": {"L": 50.0, "len": 275.0}, "upper": {"L": 75.0, "len": 330.0}},
                lambda_ratio=0.5,
                spacing_correction=1.00,
                extrapolated=False,
                derivation_text=f"Rule 49: Required stud link chain length for L={lbp:.2f} m is {chain_len:.0f} m.",
                table_view=t_view
            )

        if member_id == "equipment_number":
            z_val = round(calc_z, 1)
            t_view = cls.build_table_view(
                active_rows=[6, 7],
                active_col=0,
                bounding_cells=[{"row": 6, "col": 0, "val": 300}, {"row": 7, "col": 0, "val": 400}],
                interpolated_val=z_val,
                is_extrapolated=False
            )
            return InterpolationResult(
                baseline=z_val,
                rreq=z_val,
                unit="EN",
                table_no=cls.table_no_str,
                table_title="Equipment Number Calculation",
                formula_desc="Z = Δ^(2/3) + 2B(fb+h) + A/10",
                inputs_used={"delta": round(delta, 1), "B": breadth, "fb": round(fb, 2), "A": round(a_profile, 1)},
                bounding_nodes={"lower": {"Z": 300}, "upper": {"Z": 400}},
                lambda_ratio=0.5,
                spacing_correction=1.00,
                extrapolated=False,
                derivation_text=f"Equipment Number Z = Δ^(2/3) + 2B(fb+h) + A/10 = {z_val:.1f}.",
                table_view=t_view
            )

        # Main anchor mass
        cls.table_index = 45
        cls.table_no_str = "Table 45"
        cls.table_title = "Anchors and Ropes Scantlings"
        cls.ref_rule = "Rule 48, Table 45"

        mass_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(calc_z, cls.Z_NODES, cls.ANCHOR_MASS_NODES)
        rreq = round(mass_base, 0)

        bounding_cells = [
            {"row": idx1, "col": 1, "val": cls.ANCHOR_MASS_NODES[idx1]},
            {"row": idx2, "col": 1, "val": cls.ANCHOR_MASS_NODES[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=1,
            bounding_cells=bounding_cells,
            interpolated_val=mass_base,
            is_extrapolated=is_extrap
        )

        derivation = (
            f"Table 45 (Equipment Num Z={calc_z:.1f}): "
            f"Interpolated Bower Anchor Mass = {rreq:.0f} kg "
            f"(Bounding nodes: Z={cls.Z_NODES[idx1]} -> {cls.ANCHOR_MASS_NODES[idx1]} kg, "
            f"Z={cls.Z_NODES[idx2]} -> {cls.ANCHOR_MASS_NODES[idx2]} kg)."
        )

        return InterpolationResult(
            baseline=round(mass_base, 0),
            rreq=rreq,
            unit="kg",
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc=f"{cls.ref_rule} (Equipment Number Z)",
            inputs_used={"Z": round(calc_z, 1), "delta": round(delta, 1)},
            bounding_nodes={
                "lower": {"Z": cls.Z_NODES[idx1], "val": cls.ANCHOR_MASS_NODES[idx1]},
                "upper": {"Z": cls.Z_NODES[idx2], "val": cls.ANCHOR_MASS_NODES[idx2]}
            },
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )
