from fastapi import APIRouter, Depends # Depends : injection de dépendances (get_db)
# importe AsyncSession pour les interactions asynchrones avec la base de données
from sqlalchemy.ext.asyncio import AsyncSession
# importe la fonction get_db qui fournit une session DB pour chaque requête
from app.database import get_db
from app.schemas.location import LocationCreate, LocationResponse
# importe le service qui contient la logique métier
from app.services.location_service import LocationService
from typing import List


# prefix="/locations" : toutes les routes commencent par /locations
# tags=["Locations"]  : groupement dans la doc Swagger /docs
router = APIRouter(prefix="/locations", tags=["Locations"])

# Enregistrer une position
# response_model=LocationResponse : valide et sérialise la réponse
# request body : LocationCreate (latitude, longitude, user_id) envoyé par le client
@router.post("/", response_model=LocationResponse, status_code=201)
async def save_location(body: LocationCreate, db: AsyncSession = Depends(get_db)):
    # db : session de base de données injectée automatiquement par Depends(get_db)
    # appelle le service pour enregistrer la localisation et retourne la réponse
    return await LocationService.save_location(db, body)

# Historique d'un utilisateur
@router.get("/user/{user_id}", response_model=List[LocationResponse])
async def get_user_locations(user_id: int, db: AsyncSession = Depends(get_db)):
    return await LocationService.get_user_locations(db, user_id)

# Dernière position connue
@router.get("/user/{user_id}/last", response_model=LocationResponse)
async def get_last_location(user_id: int, db: AsyncSession = Depends(get_db)):
    return await LocationService.get_last_location(db, user_id)
