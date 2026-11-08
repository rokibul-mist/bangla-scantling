from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field

class ProfileType(str, Enum):
    ANGLE = "L"
    TEE = "T"
    FLAT_BAR = "FB"

class StiffenerDimensions(BaseModel):
    profile_type: ProfileType = ProfileType.ANGLE
    web_depth: float = Field(default=150.0, description="Web height hw (mm)")
    web_thk: float = Field(default=10.0, description="Web thickness tw (mm)")
    flange_width: float = Field(default=100.0, description="Flange width bf (mm)")
    flange_thk: float = Field(default=10.0, description="Flange thickness tf (mm)")

class SectionProperties(BaseModel):
    ap: float = Field(description="Attached plate area (mm2)")
    aw: float = Field(description="Web area (mm2)")
    af: float = Field(description="Flange area (mm2)")
    atot: float = Field(description="Total cross-section area (mm2)")
    yna: float = Field(description="Neutral axis distance from outer plate face (mm)")
    ip: float = Field(description="Plate moment of inertia about NA (mm4)")
    iw: float = Field(description="Web moment of inertia about NA (mm4)")
    iff: float = Field(description="Flange moment of inertia about NA (mm4)")
    ina: float = Field(description="Total moment of inertia Ina (mm4)")
    ymax: float = Field(description="Maximum distance from NA to extreme fiber (mm)")
    z_mm3: float = Field(description="Section modulus Z (mm3)")
    z_cm3: float = Field(description="Section modulus Z (cm3)")
