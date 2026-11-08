from fastapi import APIRouter, Depends, Request, Response
from typing import Dict, Any, Optional

from app.api.dependencies import get_state_service, get_state_repository, get_calculation_service
from app.services.state_service import StateService
from app.repositories.state_repository import StateRepository
from app.services.calculation_service import CalculationService
from app.services.pdf.lightship_pdf_service import generate_lightship_booklet_pdf
from app.api.v1.endpoints_pdf import make_content_disposition

router = APIRouter(tags=["lightship"])

def _get_computed_lightship_state(
    custom_state: Optional[Dict[str, Any]] = None,
    state_service: Optional[StateService] = None
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

    if custom_state and isinstance(custom_state, dict):
        if custom_state.get('lightship_plates'):
            computed['lightship_plates'] = custom_state['lightship_plates']
        if custom_state.get('lightship_angles'):
            computed['lightship_angles'] = custom_state['lightship_angles']
        if custom_state.get('lightship_summary'):
            computed['lightship_summary'] = custom_state['lightship_summary']
        if custom_state.get('designer_seal_png'):
            computed['designer_seal_png'] = custom_state['designer_seal_png']
        if custom_state.get('checker_seal_png'):
            computed['checker_seal_png'] = custom_state['checker_seal_png']

    return computed

@router.post("/lightship/pdf")
@router.post("/lightship/pdf/")
@router.post("/lightship/pdf/generate")
@router.post("/pdf/lightship")
@router.post("/pdf/lightship/")
@router.post("/pdf/lightship/generate")
async def generate_live_lightship_pdf(request: Request):
    """
    Accepts live state snapshot directly from frontend and streams back the generated Lightship PDF booklet.
    Ensures that unsaved or in-progress edits in Lightship table are instantly reflected!
    """
    try:
        body = await request.json()
    except Exception:
        body = {}

    computed_state = _get_computed_lightship_state(custom_state=body)
    pdf_bytes = generate_lightship_booklet_pdf(computed_state)

    vessel_name = computed_state.get('dashboard_inputs', {}).get('vessel_name', 'Vessel').replace(' ', '_')
    filename = f"{vessel_name}_Lightship_Booklet.pdf"

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

@router.get("/lightship/pdf")
@router.get("/lightship/pdf/")
@router.get("/lightship/pdf/preview")
@router.get("/pdf/lightship")
@router.get("/pdf/lightship/")
@router.get("/pdf/lightship/preview")
async def preview_lightship_pdf(
    state_service: StateService = Depends(get_state_service)
):
    """
    Renders the live Lightship PDF booklet inline.
    """
    computed_state = _get_computed_lightship_state(state_service=state_service)
    pdf_bytes = generate_lightship_booklet_pdf(computed_state)

    vessel_name = computed_state.get('dashboard_inputs', {}).get('vessel_name', 'Vessel').replace(' ', '_')
    filename = f"{vessel_name}_Lightship_Booklet.pdf"

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

@router.get("/lightship/pdf/export")
@router.get("/pdf/lightship/export")
async def export_lightship_pdf(
    state_service: StateService = Depends(get_state_service)
):
    """
    Downloads the Lightship PDF booklet as an attachment.
    """
    computed_state = _get_computed_lightship_state(state_service=state_service)
    pdf_bytes = generate_lightship_booklet_pdf(computed_state)

    vessel_name = computed_state.get('dashboard_inputs', {}).get('vessel_name', 'Vessel').replace(' ', '_')
    filename = f"{vessel_name}_Lightship_Booklet.pdf"

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
