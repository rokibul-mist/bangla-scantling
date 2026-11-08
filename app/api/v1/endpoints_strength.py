"""
Endpoints for Hull Strength, Longitudinal Bending Moments, and Midship Modulus
Statutory Reference: Rules 209 & 223, Schedule Tables 66 & 67 (SRO 308/Law-2001 & ISO 1976)
"""

import re
import urllib.parse
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse

from app.services.state_service import StateService
from app.repositories.state_repository import StateRepository
from app.services.calculation_service import CalculationService
from app.services.strength_service import StrengthService
from app.services.pdf.strength_pdf_service import generate_hull_strength_booklet_pdf

router = APIRouter(prefix="/strength", tags=["strength"])


def make_content_disposition(disposition_type: str, raw_filename: str) -> str:
    cleaned = raw_filename.replace(" ", "_")
    ascii_name = re.sub(r'[^\x20-\x7E]', '_', cleaned)
    ascii_name = re.sub(r'["\\]', '_', ascii_name)
    if not ascii_name or ascii_name == ".pdf":
        ascii_name = "Hull_Strength_Booklet.pdf"
    encoded_name = urllib.parse.quote(cleaned, encoding="utf-8")
    return f"{disposition_type}; filename=\"{ascii_name}\"; filename*=UTF-8''{encoded_name}"


def _get_computed_state(custom_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if custom_state and isinstance(custom_state, dict) and len(custom_state) > 0:
        base_state = custom_state
    else:
        repo = StateRepository()
        svc = StateService(repo)
        base_state = svc.get_saved_state() or svc.get_initial_state()

    computed = CalculationService.compute_all_calculations(base_state)
    if custom_state and isinstance(custom_state, dict):
        if custom_state.get('calculation_brain'):
            computed['calculation_brain'] = custom_state['calculation_brain']
        if custom_state.get('sheet2_results'):
            computed['sheet2_results'] = custom_state['sheet2_results']
        if custom_state.get('midship_excluded_element_ids') is not None:
            computed['midship_excluded_element_ids'] = custom_state['midship_excluded_element_ids']
        if custom_state.get('midship_selected_element_ids') is not None:
            computed['midship_selected_element_ids'] = custom_state['midship_selected_element_ids']
    return computed


@router.get("/calculate")
async def get_strength_calculations():
    """
    Computes global longitudinal strength, midship cross-section modulus,
    Table 66 hull girder stress matrix, and Table 67 local member checks from saved state.
    """
    computed = _get_computed_state()
    report = StrengthService.calculate_hull_strength(computed)
    return JSONResponse(content=report)


@router.post("/calculate")
async def post_strength_calculations(request: Request):
    """
    Computes strength metrics directly from live in-progress state payload.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}
    computed = _get_computed_state(custom_state=body)
    report = StrengthService.calculate_hull_strength(computed)
    return JSONResponse(content=report)


@router.get("/pdf")
@router.post("/pdf")
@router.post("/pdf/generate")
async def get_or_generate_strength_pdf(request: Request):
    """
    Generates and streams inline Hull Strength PDF booklet.
    """
    custom_state = None
    if request.method == "POST":
        try:
            custom_state = await request.json()
        except Exception:
            custom_state = None

    computed = _get_computed_state(custom_state=custom_state)
    pdf_bytes = generate_hull_strength_booklet_pdf(computed)

    vessel_name = computed.get('dashboard_inputs', {}).get('vessel_name', 'Vessel').replace(' ', '_')
    filename = f"{vessel_name}_Hull_Strength_Booklet.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": make_content_disposition("inline", filename),
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@router.get("/export")
async def export_strength_pdf():
    """
    Direct download attachment of the official statutory Hull Strength booklet.
    """
    computed = _get_computed_state()
    pdf_bytes = generate_hull_strength_booklet_pdf(computed)

    vessel_name = computed.get('dashboard_inputs', {}).get('vessel_name', 'Vessel').replace(' ', '_')
    filename = f"{vessel_name}_Hull_Strength_Booklet.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": make_content_disposition("attachment", filename),
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )
