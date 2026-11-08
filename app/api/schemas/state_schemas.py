from typing import Dict, Any, Optional
from pydantic import BaseModel

class StateResponse(BaseModel):
    status: str = "ok"
    message: Optional[str] = None
    state: Optional[Dict[str, Any]] = None

class SavedStateResponse(BaseModel):
    has_saved: bool
    state: Optional[Dict[str, Any]] = None
