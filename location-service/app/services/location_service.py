# Session asynchrone SQLAlchemy — permet d'exécuter des requêtes DB sans bloquer le thread.
from sqlalchemy.ext.asyncio import AsyncSession
# construit des requêtes SELECT de façon pythonique (ORM)
from sqlalchemy import select, text
# fonctions géospatiales de PostGIS pour manipuler les données géographiques :
# ST_AsText : convertit une géométrie PostGIS en format WKT (Well-Known Text) pour faciliter l'extraction des coordonnées
# ST_DWithin : vérifie si deux géométries sont à une distance donnée l'une de l'autre (utile pour la recherche de proximité)
# ST_GeogFromText : convertit une chaîne WKT en type géographique utilisable par PostGIS
from geoalchemy2.functions import ST_AsText, ST_DWithin, ST_GeogFromText
from app.models.location import Location
from app.schemas.location import LocationCreate, LocationResponse
# pour lever une 404 si aucune localisation n'est trouvée pour un utilisateur donné
from fastapi import HTTPException

def _parse_point(wkt: str) -> tuple[float, float]:
    # WKT format : "POINT(lon lat)"
    coords = wkt.replace("POINT(", "").replace(")", "").split()
    return float(coords[1]), float(coords[0])  # lat, lon

class LocationService:

    @staticmethod
    async def save_location(db: AsyncSession, body: LocationCreate) -> LocationResponse:
        wkt_point = f"POINT({body.longitude} {body.latitude})"
        loc = Location( user_id = body.user_id, geom = f"SRID=4326;{wkt_point}" )
        db.add(loc)
        await db.flush()

        return LocationResponse(
            id=loc.id,
            user_id=loc.user_id,
            latitude=body.latitude,
            longitude=body.longitude,
            created_at=loc.created_at
        )

    @staticmethod
    # récupère toutes les localisations d'un utilisateur, triées par date de création
    async def get_user_locations(db: AsyncSession, user_id: int) -> list[LocationResponse]: 
        result = await db.execute(
            select(Location.id, Location.user_id, Location.created_at,
                   ST_AsText(Location.geom).label("geom_wkt"))
            .where(Location.user_id == user_id)
            .order_by(Location.created_at.desc())
        )
        rows = result.fetchall()
        locations = []
        for row in rows:
            lat, lon = _parse_point(row.geom_wkt)
            locations.append(LocationResponse(
                id=row.id,
                user_id=row.user_id,
                latitude=lat,
                longitude=lon,
                created_at=row.created_at
            ))
        return locations

    @staticmethod
    async def get_nearby(db: AsyncSession, lat: float, lon: float, radius: float) -> list[LocationResponse]:
        point = f"POINT({lon} {lat})"
        result = await db.execute(
            select(Location.id, Location.user_id, Location.created_at,
                   ST_AsText(Location.geom).label("geom_wkt"))
            .where(ST_DWithin(
                Location.geom,
                ST_GeogFromText(f"SRID=4326;{point}"),
                radius
            ))
        )
        rows = result.fetchall()
        locations = []
        for row in rows:
            lat_r, lon_r = _parse_point(row.geom_wkt)
            locations.append(LocationResponse(
                id=row.id,
                user_id=row.user_id,
                latitude=lat_r,
                longitude=lon_r,
                created_at=row.created_at
            ))
        return locations

    @staticmethod
    async def get_last_location(db: AsyncSession, user_id: int) -> LocationResponse:
        result = await db.execute(
            select(Location.id, Location.user_id, Location.created_at,
                   ST_AsText(Location.geom).label("geom_wkt"))
            .where(Location.user_id == user_id)
            .order_by(Location.created_at.desc())
            .limit(1)
        )
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Aucune localisation trouvée")
        lat, lon = _parse_point(row.geom_wkt)
        return LocationResponse(
            id=row.id,
            user_id=row.user_id,
            latitude=lat,
            longitude=lon,
            created_at=row.created_at
        )