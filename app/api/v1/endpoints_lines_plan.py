"""
FastAPI Endpoints for Hull Lines Plan, Offset Table Generator, and CAD Export.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import io

from app.domain.models.lines_plan import (
    ReferenceFrame,
    DesignGrid,
    OffsetTableData
)
from app.services.lines_plan_service import LinesPlanService

router = APIRouter(prefix="/lines-plan", tags=["Lines Plan & Offsets"])


class GenerateLinesRequest(BaseModel):
    lbp: float = Field(default=69.85, ge=5.0, le=400.0)
    beam: float = Field(default=13.41, ge=2.0, le=80.0)
    depth: float = Field(default=5.18, ge=1.0, le=40.0)
    draft: float = Field(default=4.00, ge=0.5, le=30.0)
    cb: float = Field(default=0.75, ge=0.35, le=0.95)
    cm: float = Field(default=0.98, ge=0.60, le=0.998)
    preset_type: str = "general_cargo"
    vessel_name: str = "M. V. YOUNUS MOLLA-1"
    reference_frame: Optional[ReferenceFrame] = None
    design_grid: Optional[DesignGrid] = None


@router.post("/generate", response_model=OffsetTableData)
async def generate_lines_plan(req: GenerateLinesRequest):
    """Generates parametric lines plan and Table of Offsets from design dimensions."""
    try:
        data = LinesPlanService.generate_parametric_offsets(
            lbp=req.lbp,
            beam=req.beam,
            depth=req.depth,
            draft=req.draft,
            cb=req.cb,
            cm=req.cm,
            reference_frame=req.reference_frame,
            design_grid=req.design_grid,
            preset_type=req.preset_type,
            vessel_name=req.vessel_name
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hull generation failed: {str(e)}")


@router.post("/upload", response_model=OffsetTableData)
async def upload_hull_file(
    file: UploadFile = File(...),
    origin: str = Form("AP"),
    baseline: str = Form("KEEL"),
    units: str = Form("m"),
    scale: float = Form(1.0)
):
    """
    Uploads and parses a hull file:
    - .csv, .txt, .dat, .offsets: Table of Offsets
    - .obj, .stl: 3D mesh slicing into naval architecture design grid
    """
    try:
        content = await file.read()
        frame = ReferenceFrame(
            origin_longitudinal=origin,
            baseline=baseline,
            units=units,
            scale=scale
        )
        table_data = LinesPlanService.parse_uploaded_file(file.filename, content, frame)
        return table_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File parsing error: {str(e)}")


@router.post("/export/dxf")
async def export_dxf_endpoint(table_data: OffsetTableData):
    """Exports production-ready AutoCAD DXF drawing with layered views."""
    try:
        dxf_bytes = LinesPlanService.export_to_dxf(table_data)
        safe_name = table_data.vessel_name.replace(' ', '_').replace('.', '_')
        return Response(
            content=dxf_bytes,
            media_type="application/dxf",
            headers={"Content-Disposition": f'attachment; filename="{safe_name}_lines_plan.dxf"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DXF generation error: {str(e)}")


@router.post("/export/xlsx")
async def export_excel_endpoint(table_data: OffsetTableData):
    """Exports formatted Table of Offsets Excel workbook (.xlsx)."""
    try:
        xlsx_bytes = LinesPlanService.export_to_excel(table_data)
        safe_name = table_data.vessel_name.replace(' ', '_').replace('.', '_')
        return Response(
            content=xlsx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{safe_name}_table_of_offsets.xlsx"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel generation error: {str(e)}")
