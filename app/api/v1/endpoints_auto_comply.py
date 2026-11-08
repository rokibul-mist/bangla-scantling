"""
Auto-Comply API Endpoints.
Provides preview and application of automatic scantling compliance optimization.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.services.auto_comply.service import AutoComplyService

router = APIRouter(prefix="/auto-comply", tags=["auto-comply"])


@router.post("/preview")
async def preview_auto_comply(request: Request):
    """
    Receives current state payload and returns a comprehensive comparison
    preview of all non-compliant scantlings with proposed compliant values.
    """
    try:
        body = await request.json()
        if not body:
            raise HTTPException(status_code=400, detail="State payload is required")
        preview = AutoComplyService.generate_compliance_preview(body)
        return JSONResponse(content=preview)
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@router.post("/apply")
async def apply_auto_comply(request: Request):
    """
    Applies compliant scantling values to the provided state and returns
    the fully recomputed 100% compliant master state.
    """
    try:
        body = await request.json()
        if not body:
            raise HTTPException(status_code=400, detail="State payload is required")
        result = AutoComplyService.apply_compliance(body)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
