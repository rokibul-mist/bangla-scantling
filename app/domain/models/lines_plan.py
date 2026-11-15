"""
Domain models for Offset Table, Lines Plan Generator, and Hull Geometry.
Statutory & Naval Architecture reference: Rules 8-20, Table 1-12 & ISO 1976 Hull Representation.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ReferenceFrame(BaseModel):
    """Molded Frame of Reference definition for coordinate system and hull datum."""
    origin_longitudinal: str = Field(default="AP", description="AP, MIDSHIP, FP, or TRANSOM")
    baseline: str = Field(default="KEEL", description="KEEL (molded baseline) or USK (underside keel)")
    centerline: str = Field(default="SYMMETRIC", description="SYMMETRIC (half-breadths) or FULL_HULL")
    units: str = Field(default="m", description="m (meters), mm (millimeters), or ft (feet)")
    scale: float = Field(default=1.0, description="Scaling multiplier to convert to meters")
    shell_thickness_mm: float = Field(default=10.0, description="Shell plating deduction/addition allowance")
    deck_camber_mm: float = Field(default=250.0, description="Standard parabolic deck camber B/50")


class StationDef(BaseModel):
    id: str
    index: int
    x_pos: float  # Longitudinal distance from origin in meters
    label: str


class WaterlineDef(BaseModel):
    id: str
    z_height: float  # Vertical height above baseline in meters
    label: str


class ButtockDef(BaseModel):
    id: str
    y_offset: float  # Transverse distance from centerline in meters
    label: str


class DesignGrid(BaseModel):
    """Transverse stations, horizontal waterlines, and vertical buttock grid planes."""
    stations: List[StationDef] = Field(default_factory=list)
    waterlines: List[WaterlineDef] = Field(default_factory=list)
    buttocks: List[ButtockDef] = Field(default_factory=list)
    lbp: float = 69.85
    beam: float = 13.41
    depth: float = 5.18
    draft: float = 4.00


class OffsetPoint(BaseModel):
    station_id: str
    wl_id: str
    half_breadth: float


class DeckProfilePoint(BaseModel):
    station_id: str
    x_pos: float
    deck_height: float
    deck_half_breadth: float
    sheer_height: float


class HullHydrostatics(BaseModel):
    """Hydrostatic properties integrated from the Table of Offsets using Simpson's rules."""
    draft_m: float = 4.00
    volume_m3: float = 0.0
    displacement_tonnes: float = 0.0
    waterplane_area_m2: float = 0.0
    wetted_surface_m2: float = 0.0
    block_coefficient_cb: float = 0.0
    prismatic_coefficient_cp: float = 0.0
    midship_coefficient_cm: float = 0.0
    waterplane_coefficient_cwp: float = 0.0
    lcb_from_ap_m: float = 0.0
    lcb_percent_lbp: float = 0.0
    lcf_from_ap_m: float = 0.0
    kmt_m: float = 0.0


class MaxsurfSettings(BaseModel):
    """Detected Bentley MAXSURF design model configuration and parameters."""
    is_maxsurf: bool = True
    model_name: str = ""
    detected_via: str = "com_automation"  # "com_automation" or "native_parser"
    fref_aft_perp: float = 0.0
    fref_fwd_perp: float = 0.0
    fref_midship: float = 0.0
    fref_baseline: float = 0.0
    fref_datum_wl: float = 0.0
    grid_sections_count: int = 0
    grid_waterlines_count: int = 0
    grid_buttocks_count: int = 0
    lbp: float = 0.0
    beam: float = 0.0
    depth: float = 0.0
    draft: float = 0.0
    cb: float = 0.0
    cm: float = 0.0
    cp: float = 0.0
    cwp: float = 0.0
    lcb: float = 0.0
    lcf: float = 0.0
    kmt: float = 0.0
    surface_names: List[str] = Field(default_factory=list)


class OffsetTableData(BaseModel):
    """Complete Table of Offsets with Reference Frame, Design Grid, and Hydrostatics."""
    vessel_name: str = "M. V. YOUNUS MOLLA-1"
    reference_frame: ReferenceFrame = Field(default_factory=ReferenceFrame)
    design_grid: DesignGrid = Field(default_factory=DesignGrid)
    # Mapping: station_id -> { wl_id: half_breadth_in_meters }
    half_breadths: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    # Heights above baseline per station
    heights_above_baseline: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    # Deck & sheer contour per station
    deck_profile: List[DeckProfilePoint] = Field(default_factory=list)
    hydrostatics: Optional[HullHydrostatics] = None
    source_file: Optional[str] = None
    preset_type: str = "general_cargo"
    maxsurf_settings: Optional[MaxsurfSettings] = None
