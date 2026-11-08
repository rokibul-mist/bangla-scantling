from fastapi import APIRouter
from app.api.v1.endpoints_state import router as state_router
from app.api.v1.endpoints_calculation import router as calc_router
from app.api.v1.endpoints_pdf import router as pdf_router
from app.api.v1.endpoints_lightship import router as lightship_router
from app.api.v1.endpoints_app_form import router as app_form_router
from app.api.v1.endpoints_auto_comply import router as auto_comply_router
from app.api.v1.endpoints_vessels import router as vessels_router
from app.api.v1.endpoints_verification import router as verification_router
from app.api.v1.endpoints_strength import router as strength_router
from app.api.v1.endpoints_statutory import router as statutory_router
from app.api.v1.endpoints_tonnage import router as tonnage_router

api_router = APIRouter()
api_router.include_router(state_router)
api_router.include_router(calc_router)
api_router.include_router(pdf_router)
api_router.include_router(lightship_router)
api_router.include_router(app_form_router)
api_router.include_router(auto_comply_router)
api_router.include_router(vessels_router)
api_router.include_router(verification_router)
api_router.include_router(strength_router)
api_router.include_router(statutory_router)
api_router.include_router(tonnage_router)

__all__ = ["api_router"]
