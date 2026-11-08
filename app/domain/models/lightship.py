from typing import Optional
from pydantic import BaseModel, Field

class LightshipPlate(BaseModel):
    name: str = Field(description="Clean element name without embedded dimensions")
    l_dim: float = Field(default=0.0, description="Length (mm)")
    b_dim: float = Field(default=0.0, description="Breadth / Width (mm)")
    t: float = Field(default=0.0, description="Thickness (mm)")
    vol: float = Field(default=0.0, description="Volume (m3)")
    density: float = Field(default=7850.0, description="Density (kg/m3)")
    qty: int = Field(default=1, description="Quantity")
    weight_kg: float = Field(default=0.0, description="Total Weight (kg)")
    weight_tonne: float = Field(default=0.0, description="Total Weight (tonne)")

class LightshipAngle(BaseModel):
    name: str = Field(description="Clean element name without embedded dimensions")
    l_dim: float = Field(default=0.0, description="Flange / Leg 1 dimension (mm)")
    b_dim: float = Field(default=0.0, description="Flange / Leg 2 dimension (mm)")
    t: float = Field(default=0.0, description="Thickness (mm)")
    area: float = Field(default=0.0, description="Cross section area (mm2)")
    length: float = Field(default=0.0, description="Total Length (mm)")
    vol: float = Field(default=0.0, description="Volume (m3)")
    density: float = Field(default=7850.0, description="Density (kg/m3)")
    qty: int = Field(default=1, description="Quantity")
    weight_kg: float = Field(default=0.0, description="Total Weight (kg)")
    weight_tonne: float = Field(default=0.0, description="Total Weight (tonne)")

class LightshipSummary(BaseModel):
    total_plate_tonne: float
    total_angle_tonne: float
    total_steel_tonne: float
    allowance_tonne: float
    outfit_tonne: float
    piping_tonne: float
    electrical_tonne: float
    accom_tonne: float
    misc_tonne: float
    total_lightship_tonne: float
