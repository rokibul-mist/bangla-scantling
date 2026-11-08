from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Request, HTTPException, Query, Response
from fastapi.responses import JSONResponse
from app.api.dependencies import get_vessel_service, get_state_repository
from app.services.vessel_service import VesselService
from app.repositories.state_repository import StateRepository

router = APIRouter(prefix="/vessels", tags=["vessels"])

@router.get("")
async def list_vessels(
    q: Optional[str] = Query(None, description="Search query by name, owner, type, notes"),
    vessel_type: Optional[str] = Query(None, alias="type", description="Filter by vessel type"),
    sort: str = Query("updated_at", description="Sort by field: updated_at, vessel_name, created_at, lightship_tonnes"),
    asc: bool = Query(False, description="Ascending sort order"),
    vessel_service: VesselService = Depends(get_vessel_service)
):
    """
    Returns list of saved vessels with summary particulars and compliance results.
    """
    items = vessel_service.list_vessels(
        query=q,
        vessel_type=vessel_type,
        sort_by=sort,
        ascending=asc
    )
    return JSONResponse(content={
        "status": "ok",
        "total": len(items),
        "vessels": items
    })

@router.post("")
async def save_vessel(
    request: Request,
    vessel_service: VesselService = Depends(get_vessel_service),
    state_repo: StateRepository = Depends(get_state_repository)
):
    """
    Saves a vessel calculation to the database.
    Can accept explicit state in body, or falls back to the current active workspace state.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}

    custom_meta = body.get('custom_meta', {})
    state_data = body.get('state')
    vessel_id = body.get('id') or custom_meta.get('id')

    if not state_data:
        # Fall back to active workspace state
        state_data = state_repo.get_state()

    if not state_data or 'dashboard_inputs' not in state_data:
        raise HTTPException(status_code=400, detail="No active calculation state available to save")

    try:
        saved_summary = vessel_service.save_vessel_from_state(
            state=state_data,
            vessel_id=vessel_id,
            custom_meta=custom_meta
        )
        return JSONResponse(content={
            "status": "ok",
            "message": f"Vessel '{saved_summary.get('vessel_name')}' saved successfully to database",
            "vessel": saved_summary
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save vessel: {str(e)}")

@router.get("/{vessel_id}")
async def get_vessel(
    vessel_id: str,
    vessel_service: VesselService = Depends(get_vessel_service)
):
    """
    Retrieves full vessel calculation record including state data.
    """
    vessel = vessel_service.get_vessel(vessel_id)
    if not vessel:
        raise HTTPException(status_code=404, detail="Vessel not found")
    return JSONResponse(content={"status": "ok", "vessel": vessel})

@router.delete("/{vessel_id}")
async def delete_vessel(
    vessel_id: str,
    vessel_service: VesselService = Depends(get_vessel_service)
):
    """
    Permanently deletes a vessel calculation from the database.
    """
    success = vessel_service.delete_vessel(vessel_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vessel not found or could not be deleted")
    return JSONResponse(content={"status": "ok", "message": "Vessel deleted successfully"})

@router.post("/{vessel_id}/load")
async def load_vessel(
    vessel_id: str,
    vessel_service: VesselService = Depends(get_vessel_service)
):
    """
    Loads a vessel from the database into the active calculation workspace,
    replacing saved_state.json and immediately providing live results.
    """
    loaded_state = vessel_service.load_vessel_into_workspace(vessel_id)
    if not loaded_state:
        raise HTTPException(status_code=404, detail="Vessel not found or contains corrupt calculation state")

    return JSONResponse(content={
        "status": "ok",
        "message": f"Vessel loaded successfully into active workspace",
        "state": loaded_state
    })

@router.post("/{vessel_id}/duplicate")
async def duplicate_vessel(
    vessel_id: str,
    request: Request,
    vessel_service: VesselService = Depends(get_vessel_service)
):
    """
    Duplicates an existing vessel calculation to create a variant or new revision.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}
    new_name = body.get('new_name')

    cloned = vessel_service.duplicate_vessel(vessel_id, new_name=new_name)
    if not cloned:
        raise HTTPException(status_code=404, detail="Vessel not found or could not be duplicated")

    return JSONResponse(content={
        "status": "ok",
        "message": f"Vessel cloned as '{cloned.get('vessel_name')}'",
        "vessel": cloned
    })

@router.post("/import")
async def import_vessel(
    request: Request,
    vessel_service: VesselService = Depends(get_vessel_service)
):
    """
    Imports a vessel JSON or .dos project file into the database.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    try:
        imported = vessel_service.import_vessel(payload)
        return JSONResponse(content={
            "status": "ok",
            "message": f"Vessel '{imported.get('vessel_name')}' imported successfully",
            "vessel": imported
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")

@router.get("/{vessel_id}/export")
async def export_vessel(
    vessel_id: str,
    vessel_service: VesselService = Depends(get_vessel_service)
):
    """
    Exports the vessel calculation as a downloadable JSON / .dos file.
    """
    vessel = vessel_service.get_vessel(vessel_id)
    if not vessel:
        raise HTTPException(status_code=404, detail="Vessel not found")

    vessel_name = vessel.get('vessel_name', 'vessel').replace(' ', '_').replace('.', '')
    filename = f"{vessel_name}_{vessel_id}.dos"

    import json
    content = json.dumps(vessel, indent=2, ensure_ascii=False)
    return Response(
        content=content,
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
