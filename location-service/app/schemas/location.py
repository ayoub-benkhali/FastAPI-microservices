from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class LocationCreate(BaseModel):
    user_id: int
    latitude: float  = Field(..., ge=-90,  le=90)
    longitude: float = Field(..., ge=-180, le=180)

class LocationResponse(BaseModel):
    id: int
    user_id: int
    latitude: float
    longitude: float
    created_at: Optional[datetime] = None

class NearbyRequest(BaseModel):
    latitude: float
    longitude: float
    radius_meters: float = Field(default=1000, ge=1)