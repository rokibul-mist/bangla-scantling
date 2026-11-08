import re
import urllib.parse
from fastapi import APIRouter, Depends, Request, Response
from typing import Dict, Any

from app.api.dependencies import get_state_service, get_state_repository, get_calculation_service
from app.services.state_service import StateService
from app.repositories.state_repository import StateRepository
from app.services.calculation_service import CalculationService
from app.services.pdf.detail_calc_pdf_service import generate_detail_calculation_booklet_pdf

router = APIRouter(tags=["pdf"])


def make_content_disposition(disposition_type: str, raw_filename: str) -> str:
    """
    Produces RFC 6266 / RFC 5987 compliant Content-Disposition header.
    ASCII filename fallback + UTF-8 encoded filename*.
    Prevents latin-1 encoding crashes when raw_filename contains Bengali or non-ASCII characters.
    """
    cleaned = raw_filename.replace(" ", "_")
    ascii_name = re.sub(r'[^\x20-\x7E]', '_', cleaned)
    ascii_name = re.sub(r'["\\]', '_', ascii_name)
    if not ascii_name or ascii_name == ".pdf":
        ascii_name = "document.pdf"
    encoded_name = urllib.parse.quote(cleaned, encoding="utf-8")
    return f"{disposition_type}; filename=\"{ascii_name}\"; filename*=UTF-8''{encoded_name}"

def _get_computed_state(
    custom_state: Dict[str, Any] = None,
    state_service: StateService = None
) -> Dict[str, Any]:
    if custom_state and isinstance(custom_state, dict) and len(custom_state) > 0:
        base_state = custom_state
    elif state_service:
        base_state = state_service.get_saved_state() or state_service.get_initial_state()
    else:
        repo = StateRepository()
        svc = StateService(repo)
        base_state = svc.get_saved_state() or svc.get_initial_state()
    
    computed = CalculationService.compute_all_calculations(base_state)

    # When custom_state is supplied from live UI session, preserve client-calculated
    # brain items, detail sheets, and seals to guarantee 100% exact parity with user screen:
    if custom_state and isinstance(custom_state, dict):
        if custom_state.get('calculation_brain'):
            computed['calculation_brain'] = custom_state['calculation_brain']
        if custom_state.get('sheet2_results'):
            computed['sheet2_results'] = custom_state['sheet2_results']
        if custom_state.get('designer_seal_png'):
            computed['designer_seal_png'] = custom_state['designer_seal_png']
        if custom_state.get('checker_seal_png'):
            computed['checker_seal_png'] = custom_state['checker_seal_png']
        if custom_state.get('lightship_plates'):
            computed['lightship_plates'] = custom_state['lightship_plates']
        if custom_state.get('lightship_angles'):
            computed['lightship_angles'] = custom_state['lightship_angles']
        if custom_state.get('lightship_summary'):
            computed['lightship_summary'] = custom_state['lightship_summary']

    return computed


@router.get("/pdf/detail-calc")
@router.get("/pdf/detail-calc/")
@router.get("/pdf/detail-calc/preview")
@router.get("/pdf/detail-calculation/preview")
@router.get("/detail-calc")
@router.get("/detail-calc/")
@router.get("/detail-calc/preview")
@router.get("/detail-calculation/preview")
async def preview_detail_calc_pdf(
    state_service: StateService = Depends(get_state_service)
):
    """
    Renders the live Detail Calculation Engineering Booklet (Cover + Dashboard + Sheets + Figures) inline.
    """
    computed_state = _get_computed_state(state_service=state_service)
    pdf_bytes = generate_detail_calculation_booklet_pdf(computed_state)

    vessel_name = computed_state.get('dashboard_inputs', {}).get('vessel_name', 'Vessel').replace(' ', '_')
    filename = f"{vessel_name}_Detail_Calculation_Booklet.pdf"

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


@router.get("/pdf/detail-calc/export")
@router.get("/pdf/detail-calculation/export")
@router.get("/detail-calc/export")
@router.get("/detail-calculation/export")
async def export_detail_calc_pdf(
    state_service: StateService = Depends(get_state_service)
):
    """
    Downloads the live Detail Calculation Engineering Booklet PDF.
    """
    computed_state = _get_computed_state(state_service=state_service)
    pdf_bytes = generate_detail_calculation_booklet_pdf(computed_state)

    vessel_name = computed_state.get('dashboard_inputs', {}).get('vessel_name', 'Vessel').replace(' ', '_')
    filename = f"{vessel_name}_Detail_Calculation_Booklet.pdf"

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


@router.post("/pdf/detail-calc")
@router.post("/pdf/detail-calc/")
@router.post("/pdf/detail-calc/generate")
@router.post("/pdf/detail-calculation/generate")
@router.post("/detail-calc")
@router.post("/detail-calc/")
@router.post("/detail-calc/generate")
@router.post("/detail-calculation/generate")
async def generate_live_detail_calc_pdf(request: Request):
    """
    Accepts live state snapshot directly from frontend and streams back the generated PDF.
    Ensures that unsaved or in-progress edits in Dashboard / Detail Calc are instantly reflected!
    """
    try:
        body = await request.json()
    except Exception:
        body = {}
    
    computed_state = _get_computed_state(custom_state=body)
    pdf_bytes = generate_detail_calculation_booklet_pdf(computed_state)

    vessel_name = computed_state.get('dashboard_inputs', {}).get('vessel_name', 'Vessel').replace(' ', '_')
    filename = f"{vessel_name}_Detail_Calculation_Booklet.pdf"

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
