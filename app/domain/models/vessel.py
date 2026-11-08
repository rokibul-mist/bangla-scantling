from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field

class HullConstructionType(str, Enum):
    DOUBLE_BOTTOM = "Double Bottom"
    DOUBLE_HULL = "Double Hull"
    SINGLE_HULL = "Single Hull"

class MaterialType(str, Enum):
    MILD_STEEL = "Steel (Mild)"
    OLD_STEEL = "Steel (Old)"
    HIGH_TENSILE = "Steel (High Tensile)"

class RouteType(str, Enum):
    INLAND_BAY_CROSSING = "Inland & bay crossing"
    INLAND_CALM_WATER = "Inland calm water"
    BAY_CROSSING = "Bay crossing"
    COASTAL = "Coastal"
    INLAND_ROUGH_WATER = "Inland rough water"

class VesselParticulars(BaseModel):
    vessel_name: str = Field(default="MV BANGLA PRODIP", description="Official Vessel Name")
    vessel_type: str = Field(default="Steel Body Cargo Vessel", description="Vessel Classification Type")
    registration_no: str = Field(default="C-1420", description="DOS Official Registration No")
    call_sign: str = Field(default="S2XYZ", description="Radio Call Sign")
    owner_name: str = Field(default="Bengal Marine Shipping Lines Ltd.", description="Registered Owner Name")
    yard_name: str = Field(default="Meghna Shipbuilders & Dockyard", description="Shipyard of Construction")
    keel_laid_date: str = Field(default="2023-01-15", description="Keel Laying Date")
    delivery_date: str = Field(default="2024-03-20", description="Delivery Date")
    
    # Principal Dimensions
    loa: float = Field(default=76.21, description="Length Overall (m)")
    lbp: float = Field(default=69.85, description="Length Between Perpendiculars (m)")
    breadth: float = Field(default=13.41, description="Moulded Breadth (m)")
    depth: float = Field(default=5.18, description="Moulded Depth (m)")
    draft: float = Field(default=4.00, description="Design Summer Draft (m)")
    frame_spacing: float = Field(default=550.0, description="Transverse Frame Spacing (mm)")
    
    # Construction Classifications
    hull_type: str = Field(default="Double Bottom", description="Hull Construction Configuration")
    hull_material: str = Field(default="Steel (Old)", description="Construction Material")
    proposed_route: str = Field(default="Inland & bay crossing", description="Design Operational Route")
    plying_time: str = Field(default="Day & Night", description="Permitted Operating Hours")
