from fastapi import APIRouter, Depends # Depends : injection de dépendances (get_db)
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.location import LocationCreate, LocationResponse
from app.services.location_service import LocationService
from typing import List


# prefix="/locations" : toutes les routes commencent par /locations
# tags=["Locations"]  : groupement dans la doc Swagger /docs
router = APIRouter(prefix="/locations", tags=["Locations"])

# Enregistrer une position
@router.post("/", response_model=LocationResponse, status_code=201)
async def save_location(body: LocationCreate, db: AsyncSession = Depends(get_db)):
    return await LocationService.save_location(db, body)

# Historique d'un utilisateur
@router.get("/user/{user_id}", response_model=List[LocationResponse])
async def get_user_locations(user_id: int, db: AsyncSession = Depends(get_db)):
    return await LocationService.get_user_locations(db, user_id)

# Dernière position connue
@router.get("/user/{user_id}/last", response_model=LocationResponse)
async def get_last_location(user_id: int, db: AsyncSession = Depends(get_db)):
    return await LocationService.get_last_location(db, user_id)
