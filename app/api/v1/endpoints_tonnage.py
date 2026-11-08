"""
API Endpoints for Statutory Gross & Net Tonnage Calculation (ISO 2001).
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
from app.services.tonnage_service import TonnageService
from app.services.state_service import StateService

router = APIRouter(prefix="/tonnage", tags=["Tonnage Calculation (ISO 2001)"])


@router.post("/calculate")
def calculate_tonnage(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    Evaluates Gross Tonnage (GT, Rule 11) and Net Tonnage (NT, Rule 12)
    as per The Inland Ships (Tonnage Measurement) Rules, 2001 (ISO 2001).
    """
    try:
        result = TonnageService.calculate_tonnage(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Tonnage calculation failed: {str(e)}")


@router.get("/current")
def get_current_tonnage() -> Dict[str, Any]:
    """
    Computes tonnage using current vessel project state.
    """
    try:
        svc = StateService()
        state = svc.get_initial_state()
        inputs = state.get("dashboard_inputs", {})
        result = TonnageService.calculate_tonnage(inputs)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute current vessel tonnage: {str(e)}")
