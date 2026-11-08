"""
Base Interpolator and Mathematical Utilities for Empirical Statutory Tables.
Provides linear interpolation, extrapolation, multi-dimensional blending,
spacing corrections, and table view formatting for Calculation Brain derivations.
"""

from typing import List, Tuple, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.repositories.empirical_tables_repository import EmpiricalTablesRepository


class TableViewData(BaseModel):
    table_id: str
    table_no: str
    title: str
    ref: str
    headers: List[str] = Field(default_factory=list)
    rows: List[List[str]] = Field(default_factory=list)
    active_row_indices: List[int] = Field(default_factory=list)
    active_col_index: Optional[int] = None
    active_col_indices: List[int] = Field(default_factory=list)
    bounding_cells: List[Dict[str, Any]] = Field(default_factory=list)
    extrapolated: bool = False
    interpolated_value: float = 0.0
    notes: Optional[Any] = None


class InterpolationResult(BaseModel):
    baseline: float
    rreq: float
    unit: str = "mm"
    table_no: str = ""
    table_title: str = ""
    formula_desc: str = ""
    inputs_used: Dict[str, Any] = Field(default_factory=dict)
    bounding_nodes: Dict[str, Any] = Field(default_factory=dict)
    lambda_ratio: float = 0.0
    spacing_correction: float = 1.00
    extrapolated: bool = False
    derivation_text: str = ""
    table_view: Optional[TableViewData] = None
    components: List[Dict[str, Any]] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class BaseTableInterpolator:
    """
    Abstract Base Class for statutory empirical table interpolators.
    """
    table_index: int = 0  # Index in schedule_tables.json
    table_no_str: str = ""
    table_title: str = ""
    ref_rule: str = ""
    default_unit: str = "mm"

    _repo = EmpiricalTablesRepository()

    @classmethod
    def get_table_data(cls) -> Optional[Dict[str, Any]]:
        tables = cls._repo.get_all_tables()
        if 0 <= cls.table_index < len(tables):
            return tables[cls.table_index]
        return None

    @staticmethod
    def interpolate_1d(
        x: float,
        x_nodes: List[float],
        y_nodes: List[float],
        allow_extrapolation: bool = True
    ) -> Tuple[float, int, int, float, bool]:
        """
        1D Linear Interpolation with linear extrapolation.
        Returns: (interpolated_y, idx1, idx2, lambda_ratio, is_extrapolated)
        """
        n = len(x_nodes)
        if n == 0 or len(y_nodes) != n:
            return 0.0, 0, 0, 0.0, False

        if n == 1:
            return float(y_nodes[0]), 0, 0, 0.0, False

        # Below minimum node
        if x <= x_nodes[0]:
            if not allow_extrapolation or x == x_nodes[0]:
                return float(y_nodes[0]), 0, 1, 0.0, False
            dx = x_nodes[1] - x_nodes[0]
            slope = (y_nodes[1] - y_nodes[0]) / dx if dx != 0 else 0.0
            val = y_nodes[0] + slope * (x - x_nodes[0])
            return float(val), 0, 1, (x - x_nodes[0]) / dx, True

        # Above maximum node
        if x >= x_nodes[-1]:
            if not allow_extrapolation or x == x_nodes[-1]:
                return float(y_nodes[-1]), n - 2, n - 1, 1.0, False
            dx = x_nodes[-1] - x_nodes[-2]
            slope = (y_nodes[-1] - y_nodes[-2]) / dx if dx != 0 else 0.0
            val = y_nodes[-1] + slope * (x - x_nodes[-1])
            return float(val), n - 2, n - 1, 1.0 + (x - x_nodes[-1]) / dx, True

        # Within bounds: locate segment
        for i in range(n - 1):
            if x_nodes[i] <= x <= x_nodes[i + 1]:
                dx = x_nodes[i + 1] - x_nodes[i]
                lam = (x - x_nodes[i]) / dx if dx != 0 else 0.0
                val = y_nodes[i] + lam * (y_nodes[i + 1] - y_nodes[i])
                return float(val), i, i + 1, float(lam), False

        return float(y_nodes[-1]), n - 2, n - 1, 1.0, False

    @staticmethod
    def apply_spacing_correction(
        base_val: float,
        spacing_mm: float,
        is_sm: bool = False
    ) -> Tuple[float, float]:
        """
        Applies statutory frame spacing correction for s > 550 mm.
        For plate thickness: t_corr = t_base * sqrt(s / 550)
        For section modulus: Z_corr = Z_base * (s / 550)
        Returns: (corrected_val, correction_ratio)
        """
        if spacing_mm <= 550.0:
            return base_val, 1.00

        ratio = spacing_mm / 550.0
        if is_sm:
            factor = ratio
        else:
            factor = ratio ** 0.5

        return round(base_val * factor, 2), round(factor, 4)

    @classmethod
    def build_table_view(
        cls,
        active_rows: List[int],
        active_col: Optional[int],
        bounding_cells: List[Dict[str, Any]],
        interpolated_val: float,
        is_extrapolated: bool = False,
        active_cols: Optional[List[int]] = None
    ) -> TableViewData:
        t_data = cls.get_table_data() or {}
        col_list = active_cols if active_cols is not None else ([active_col] if active_col is not None else [])
        return TableViewData(
            table_id=str(t_data.get('id', cls.table_no_str)),
            table_no=cls.table_no_str,
            title=cls.table_title or t_data.get('title', ''),
            ref=cls.ref_rule or t_data.get('ref', ''),
            headers=t_data.get('headers', []),
            rows=t_data.get('rows', []),
            active_row_indices=active_rows,
            active_col_index=active_col,
            active_col_indices=col_list,
            bounding_cells=bounding_cells,
            extrapolated=is_extrapolated,
            interpolated_value=round(interpolated_val, 2),
            notes=t_data.get('notes')
        )
