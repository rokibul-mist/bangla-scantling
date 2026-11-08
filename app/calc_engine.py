"""
Backward-compatibility facade for calculation engine.
Forwards all calls to app.services.calculation_service and app.domain.calc.
"""
from app.domain.calc.section_modulus import calc_stiffener_section
from app.services.calculation_service import CalculationService

compute_all_calculations = CalculationService.compute_all_calculations

__all__ = [
    "calc_stiffener_section",
    "CalculationService",
    "compute_all_calculations",
]
