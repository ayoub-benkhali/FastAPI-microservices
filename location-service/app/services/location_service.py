# Session asynchrone SQLAlchemy — permet d'exécuter des requêtes DB sans bloquer le thread.
from sqlalchemy.ext.asyncio import AsyncSession
# construit des requêtes SELECT de façon pythonique (ORM)
from sqlalchemy import select, text
# fonctions géospatiales de PostGIS pour manipuler les données géographiques :
# ST_AsText : convertit une géométrie PostGIS en format WKT (Well-Known Text) pour faciliter l'extraction des coordonnées
# ST_GeogFromText : convertit une chaîne WKT en type géographique utilisable par PostGIS
from geoalchemy2.functions import ST_AsText, ST_GeogFromText
from app.models.location import Location
from app.schemas.location import LocationCreate, LocationResponse
# pour lever une 404 si aucune localisation n'est trouvée pour un utilisateur donné
from fastapi import HTTPException

# Fonction utilitaire : convertit une chaîne WKT en tuple de coordonnées (lat, lon)
# WKT format : "POINT(lon lat)"
def _parse_point(wkt: str) -> tuple[float, float]:
    # Supprime "POINT(" et ")" puis divise par l'espace pour obtenir les coordonnées
    coords = wkt.replace("POINT(", "").replace(")", "").split()
    # Retourne (latitude, longitude) — note : PostGIS stocke (lon, lat) donc on les inverse
    return float(coords[1]), float(coords[0])  # lat, lon

class LocationService:

    @staticmethod
    async def save_location(db: AsyncSession, body: LocationCreate) -> LocationResponse:
        # Crée une chaîne WKT à partir de la latitude et longitude reçues
        wkt_point = f"POINT({body.longitude} {body.latitude})"
        # Crée une instance Location avec le user_id et la géométrie (SRID=4326 = WGS84, standard GPS)
        loc = Location( user_id = body.user_id, geom = f"SRID=4326;{wkt_point}" )
        # Ajoute l'objet à la session (pas encore committé)
        db.add(loc)
        # flush() : exécute l'INSERT sans committer, ce qui génère l'ID auto-incrémenté
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
         # Exécute une requête SELECT pour obtenir les colonnes d'intérêt
        result = await db.execute(
            select(Location.id, Location.user_id, Location.created_at,
                   ST_AsText(Location.geom).label("geom_wkt")) # ST_AsText : convertit la géométrie en texte WKT
            .where(Location.user_id == user_id)
            .order_by(Location.created_at.desc())
        )
        # récupère tous les résultats sous forme de tuples
        rows = result.fetchall()
        locations = []
        for row in rows:
            # extrait les coordonnées WKT et les convertit en float
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
    async def get_last_location(db: AsyncSession, user_id: int) -> LocationResponse:
        result = await db.execute(
            select(Location.id, Location.user_id, Location.created_at,
                   ST_AsText(Location.geom).label("geom_wkt"))
            .where(Location.user_id == user_id)
            .order_by(Location.created_at.desc())
            .limit(1) # limite à 1 seul résultat (le plus récent)
        )
        # récupère une seule ligne résultante (ou None si aucun résultat)
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Aucune localisation trouvée")
        # extrait les coordonnées WKT et les convertit en float
        lat, lon = _parse_point(row.geom_wkt)
        return LocationResponse(
            id=row.id,
            user_id=row.user_id,
            latitude=lat,
            longitude=lon,
            created_at=row.created_at
        )