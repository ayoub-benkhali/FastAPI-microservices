from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.location import LocationCreate, LocationResponse, NearbyRequest
from app.services.location_service import LocationService
from typing import List

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

# Points proches d'une coordonnée
@router.post("/nearby", response_model=List[LocationResponse])
async def get_nearby(body: NearbyRequest, db: AsyncSession = Depends(get_db)):
    return await LocationService.get_nearby(db, body.latitude, body.longitude, body.radius_meters)