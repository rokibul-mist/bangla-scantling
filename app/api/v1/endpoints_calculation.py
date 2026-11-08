from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.api.dependencies import get_calculation_service
from app.services.calculation_service import CalculationService

router = APIRouter(tags=["calculation"])

@router.post("/calculate")
async def calculate_state(
    request: Request,
    calc_service: CalculationService = Depends(get_calculation_service)
):
    """
    Takes updated inputs and stiffener dimensions, recalculates all values and compliance.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Calculation payload must be a JSON object")

    updated_state = calc_service.compute_all_calculations(body)
    return JSONResponse(content=updated_state)

calculate = calculate_state
