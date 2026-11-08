"""
Statutory Rule Empirical Table Interpolation Package.
Provides dedicated table interpolators and registry for structural scantling calculations.
"""
from app.domain.rules.interpolations.base_interpolator import (
    BaseTableInterpolator, InterpolationResult, TableViewData
)
from app.domain.rules.interpolations.registry import TableInterpolationRegistry

__all__ = [
    "BaseTableInterpolator",
    "InterpolationResult",
    "TableViewData",
    "TableInterpolationRegistry",
]
