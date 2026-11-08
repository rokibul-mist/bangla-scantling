from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from app.api.dependencies import get_state_service, get_state_repository
from app.services.state_service import StateService
from app.repositories.state_repository import StateRepository

router = APIRouter(tags=["state"])

@router.get("/initial-state")
async def get_initial_state(
    state_service: StateService = Depends(get_state_service),
    state_repo: StateRepository = Depends(get_state_repository)
):
    """
    Returns the initial state with pre-computed values, merging any saved user state if present
    """
    raw_data = state_repo.get_raw_data()
    master = state_service.get_initial_state()
    # Merge with empirical tables and application form pages
    master['empirical_tables'] = raw_data.get('empirical_tables', [])
    master['application_form_pages'] = raw_data.get('application_form_pages', [])
    return JSONResponse(content=master)

@router.post("/save-state")
async def save_state(
    request: Request,
    state_service: StateService = Depends(get_state_service)
):
    """
    Persists current calculation state to saved_state.json
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="State payload must be a JSON object")

    try:
        success = state_service.save_state(body)
        if success:
            return JSONResponse(content={"status": "ok", "message": "State saved successfully"})
        return JSONResponse(status_code=500, content={"status": "error", "message": "Failed to save state"})
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@router.get("/saved-state")
async def get_saved_state(
    state_service: StateService = Depends(get_state_service)
):
    """
    Returns saved state if present
    """
    saved = state_service.get_saved_state()
    if saved:
        return JSONResponse(content={"has_saved": True, "state": saved})
    return JSONResponse(content={"has_saved": False})

@router.post("/reset-state")
async def reset_state(
    state_service: StateService = Depends(get_state_service)
):
    """
    Removes saved_state.json to revert to factory defaults
    """
    state_service.reset_state()
    return JSONResponse(content={"status": "ok", "message": "Reset to master defaults"})
