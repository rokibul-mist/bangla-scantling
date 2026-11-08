"""
Tables 39 - 44: Rudder Stock, Pintle, Coupling Bolt & Steering Interpolators.
Statutory Reference: Rules 46 - 49, Tables 39 - 44.
Governing parameters: Rudder Area A (m²) and Speed V (knots).
"""

from typing import Dict, Any, List
from .base_interpolator import BaseTableInterpolator, InterpolationResult


class Table3943RudderInterpolator(BaseTableInterpolator):
    table_index = 38  # Table 39: Supported Rudder Stock Diameter
    table_no_str = "Table 39"
    table_title = "Supported Rudder Stock Diameter"
    ref_rule = "Rule 46, Table 39"
    default_unit = "mm"

    AREA_NODES = [0.25, 0.50, 0.75, 1.00, 1.25, 1.50, 1.75, 2.00, 2.25, 2.50]
    STOCK_DIA_NODES = [29.0, 48.0, 61.0, 72.0, 82.0, 92.0, 101.0, 109.0, 116.0, 123.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "rudder_stock_dia") -> InterpolationResult:
        lbp = float(inputs.get('lbp', 69.85) or 69.85)
        draft = float(inputs.get('draft', 4.0) or 4.0)
        rudder_area = float(inputs.get('rudder_area') or (lbp * draft * 0.018) or 2.15)

        d_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(rudder_area, cls.AREA_NODES, cls.STOCK_DIA_NODES)
        rreq = round(d_base, 1)

        bounding_cells = [
            {"row": idx1, "col": 1, "val": cls.STOCK_DIA_NODES[idx1]},
            {"row": idx2, "col": 1, "val": cls.STOCK_DIA_NODES[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=1,
            bounding_cells=bounding_cells,
            interpolated_val=d_base,
            is_extrapolated=is_extrap
        )

        derivation = f"Table 39 (Rudder Area={rudder_area:.2f} m²): Stock Dia={cls.STOCK_DIA_NODES[idx1]} + {lam:.3f}*({cls.STOCK_DIA_NODES[idx2]}-{cls.STOCK_DIA_NODES[idx1]}) = {d_base:.1f} mm"

        return InterpolationResult(
            baseline=round(d_base, 1),
            rreq=rreq,
            unit=cls.default_unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 46, Table 39 with linear interpolation by Rudder Area A",
            inputs_used={"rudder_area": rudder_area, "factor": 1.0},
            bounding_nodes={"A1": cls.AREA_NODES[idx1], "A2": cls.AREA_NODES[idx2], "d1": cls.STOCK_DIA_NODES[idx1], "d2": cls.STOCK_DIA_NODES[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view
        )


class Table41RudderCouplingBoltsInterpolator(BaseTableInterpolator):
    table_index = 41  # Table 41: Rudder Coupling Bolt Diameter
    table_no_str = "Table 41"
    table_title = "Rudder Coupling Bolt Diameter"
    ref_rule = "Rule 48, Table 41"
    default_unit = "mm"

    STOCK_NODES = [30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 110.0, 120.0, 130.0, 140.0]
    BOLT_3_NODES = [12.0, 16.0, 20.0, 24.0, 27.0, 30.0, 35.0, 39.0, 42.0, 48.0, 50.0, 55.0]
    BOLT_4_NODES = [10.0, 14.0, 16.0, 20.0, 24.0, 27.0, 30.0, 33.0, 36.0, 40.0, 45.0, 48.0]
    BOLT_5_NODES = [9.0, 12.0, 15.0, 18.0, 20.0, 24.0, 26.0, 30.0, 32.0, 35.0, 38.0, 42.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "rudder_coupling_bolts") -> InterpolationResult:
        stock_dia = float(inputs.get('rudder_stock_dia') or 120.8)

        b4_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(stock_dia, cls.STOCK_NODES, cls.BOLT_4_NODES)
        flange_thk = round(0.25 * stock_dia, 1)

        is_flange = (member_id == "rudder_flange_thk")
        primary_val = flange_thk if is_flange else b4_base
        rreq = round(primary_val, 1)

        bounding_cells = [
            {"row": idx1, "col": 2, "val": cls.BOLT_4_NODES[idx1]},
            {"row": idx2, "col": 2, "val": cls.BOLT_4_NODES[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=2,
            bounding_cells=bounding_cells,
            interpolated_val=b4_base,
            is_extrapolated=is_extrap
        )

        derivation = f"Table 41 (Stock Dia={stock_dia:.1f} mm): 4-Bolt Coupling Dia={b4_base:.1f} mm, Flange Thk(0.25*d)={flange_thk:.1f} mm"

        components = [
            {"name": "Coupling Bolt Diameter (4-Bolt)", "base": round(b4_base, 1), "factor": 1.0, "rreq": round(b4_base, 1), "unit": "mm"},
            {"name": "Coupling Flange Thickness", "base": flange_thk, "factor": 1.0, "rreq": flange_thk, "unit": "mm"}
        ]

        return InterpolationResult(
            baseline=round(primary_val, 1),
            rreq=rreq,
            unit=cls.default_unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 48, Table 41 Rudder Coupling Bolt & Flange",
            inputs_used={"stock_dia": stock_dia, "factor": 1.0},
            bounding_nodes={"D1": cls.STOCK_NODES[idx1], "D2": cls.STOCK_NODES[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view,
            components=components
        )


class Table44SteeringChainsInterpolator(BaseTableInterpolator):
    table_index = 44  # Table 44: Steering Chains, Rods, Shackles & Crosses Scantlings
    table_no_str = "Table 44"
    table_title = "Steering Chains, Rods, Shackles & Crosses Scantlings"
    ref_rule = "Rule 49, Table 44"
    default_unit = "mm"

    STOCK_NODES = [30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 110.0, 120.0, 130.0, 140.0]
    TILLER_LEN_NODES = [400.0, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0, 1100.0, 1200.0, 1300.0, 1350.0, 1400.0]
    CHAIN_DIA_NODES = [5.0, 5.0, 6.5, 6.5, 8.0, 8.0, 9.5, 11.0, 13.0, 16.0, 16.0, 16.0]
    ROD_DIA_NODES = [6.0, 7.0, 10.0, 10.0, 10.0, 12.0, 13.0, 14.0, 16.0, 18.0, 20.0, 22.0]

    @classmethod
    def interpolate(cls, inputs: Dict[str, Any], member_id: str = "steering_chains_shackles") -> InterpolationResult:
        stock_dia = float(inputs.get('rudder_stock_dia') or 120.8)

        tiller_base, idx1, idx2, lam, is_extrap = cls.interpolate_1d(stock_dia, cls.STOCK_NODES, cls.TILLER_LEN_NODES)
        chain_base, _, _, _, _ = cls.interpolate_1d(stock_dia, cls.STOCK_NODES, cls.CHAIN_DIA_NODES)
        rod_base, _, _, _, _ = cls.interpolate_1d(stock_dia, cls.STOCK_NODES, cls.ROD_DIA_NODES)

        is_tiller = (member_id == "steering_tiller_quadrant")
        active_col = 1 if is_tiller else 2
        primary_val = tiller_base if is_tiller else chain_base
        rreq = round(primary_val, 1)

        bounding_cells = [
            {"row": idx1, "col": 1, "val": cls.TILLER_LEN_NODES[idx1]},
            {"row": idx2, "col": 1, "val": cls.TILLER_LEN_NODES[idx2]},
            {"row": idx1, "col": 2, "val": cls.CHAIN_DIA_NODES[idx1]},
            {"row": idx2, "col": 2, "val": cls.CHAIN_DIA_NODES[idx2]},
            {"row": idx1, "col": 3, "val": cls.ROD_DIA_NODES[idx1]},
            {"row": idx2, "col": 3, "val": cls.ROD_DIA_NODES[idx2]}
        ]

        t_view = cls.build_table_view(
            active_rows=[idx1, idx2],
            active_col=active_col,
            active_cols=[1, 2, 3],
            bounding_cells=bounding_cells,
            interpolated_val=primary_val,
            is_extrapolated=is_extrap
        )

        derivation = f"Table 44 (Stock Dia={stock_dia:.1f} mm): Tiller Len={tiller_base:.0f} mm, Chain Dia={chain_base:.1f} mm, Rod Dia={rod_base:.1f} mm"

        components = [
            {"name": "Steering Tiller Length", "base": round(tiller_base, 0), "factor": 1.0, "rreq": round(tiller_base, 0), "unit": "mm"},
            {"name": "Steering Chain Diameter", "base": round(chain_base, 1), "factor": 1.0, "rreq": round(chain_base, 1), "unit": "mm"},
            {"name": "Steering Rod Diameter", "base": round(rod_base, 1), "factor": 1.0, "rreq": round(rod_base, 1), "unit": "mm"}
        ]

        return InterpolationResult(
            baseline=round(primary_val, 1),
            rreq=rreq,
            unit=cls.default_unit,
            table_no=cls.table_no_str,
            table_title=cls.table_title,
            formula_desc="Rule 49, Table 44 Steering Chains & Gear Scantlings",
            inputs_used={"stock_dia": stock_dia, "factor": 1.0},
            bounding_nodes={"D1": cls.STOCK_NODES[idx1], "D2": cls.STOCK_NODES[idx2]},
            lambda_ratio=round(lam, 4),
            spacing_correction=1.00,
            extrapolated=is_extrap,
            derivation_text=derivation,
            table_view=t_view,
            components=components
        )
