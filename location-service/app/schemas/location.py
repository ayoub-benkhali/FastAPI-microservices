from pydantic import BaseModel, Field # Field : contraintes de validation (min/max)
from datetime import datetime
from typing import Optional

class LocationCreate(BaseModel):
    user_id: int
    latitude: float  = Field(..., ge=-90,  le=90) # entre -90 et 90
    longitude: float = Field(..., ge=-180, le=180) # entre -180 et 180

 # Retourné au client — inclut id et created_at générés par la DB
class LocationResponse(BaseModel):
    id: int
    user_id: int
    latitude: float
    longitude: float
    created_at: Optional[datetime] = None

# Reçu en POST /nearby — coordonnées + rayon de recherche
class NearbyRequest(BaseModel):
    latitude: float
    longitude: float
    radius_meters: float = Field(default=5000, ge=1) # défaut 5km, minimum 1m