from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

class MemberType(str, Enum):
    PLATE = "plate"
    STIFFENER = "stiffener"
    LIMIT = "limit"
    DIMENSION = "dimension"
    EQUIPMENT = "equipment"
    PIPING = "piping"

class ComplianceStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON-COMPLIANT"

class ScantlingMember(BaseModel):
    id: str
    name: str
    category: str
    type: MemberType
    table_ref: str
    applicable_hull_types: List[str] = Field(default_factory=lambda: ["all"])
    applicable_vessel_types: List[str] = Field(default_factory=lambda: ["all"])
    baseline: float
    unit: str = "mm"
    notes: Optional[str] = ""
    bound_plate_key: Optional[str] = None
    welded_on_plate: Optional[str] = None
    welded_plate_key: Optional[str] = None
    welded_plate_thickness: Optional[float] = None
    factor: Optional[float] = 1.00
    rreq: Optional[float] = None
    dact: Optional[float] = None
    margin: Optional[float] = None
    status: Optional[ComplianceStatus] = None
