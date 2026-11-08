from typing import Dict, Any, Optional
from pydantic import BaseModel

class CalculateRequest(BaseModel):
    state: Dict[str, Any]

class CalculateResponse(BaseModel):
    status: str = "ok"
    state: Dict[str, Any]
