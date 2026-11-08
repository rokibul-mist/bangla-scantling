"""
Alias module for app.api.v1.endpoints_calculation providing backwards/shorthand compatibility.
"""
from app.api.v1.endpoints_calculation import (
    router,
    calculate_state,
    calculate,
)

__all__ = ["router", "calculate_state", "calculate"]
