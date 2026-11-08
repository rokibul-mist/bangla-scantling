"""
Endpoints for Cross-Deliverables Verification & Statutory Audit
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any

from app.services.verification_service import VerificationService
from app.repositories.state_repository import StateRepository

router = APIRouter(tags=["verification"])


@router.get("/verification/audit")
@router.get("/verify")
async def get_verification_audit():
    """
    Runs full verification audit across current saved state and generated deliverables.
    Returns status, check counts, and itemized diagnostics.
    """
    repo = StateRepository()
    state = repo.get_saved_state() or repo.get_state()
    report = VerificationService.run_comprehensive_verification(state=state)
    return JSONResponse(content=report)


@router.post("/verification/audit")
@router.post("/verify")
async def post_verification_audit(request: Request):
    """
    Accepts live state snapshot and runs verification against current deliverables and state models.
    """
    try:
        body = await request.json()
    except Exception:
        body = None

    if body is not None and not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Verification payload must be a JSON object")

    report = VerificationService.run_comprehensive_verification(state=body)
    return JSONResponse(content=report)
