from sqlalchemy import Column, Integer, DateTime, func
# Geography : type PostGIS pour stocker des coordonnées géographiques (lon/lat)
# SRID 4326 = système de coordonnées WGS84 (GPS standard)
from geoalchemy2 import Geography          
from app.database import Base

class Location(Base):
    __tablename__ = "locations"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, nullable=False, index=True)
    # SRID 4326 = GPS standard (longitude/latitude)
    # au lieu de lat = 36.8 , lon = 10.1 et lat = 36.8, on stocke un point géographique (POINT(10.1 36.8))
    geom       = Column(Geography(geometry_type="POINT", srid=4326), nullable=False) 
    created_at = Column(DateTime, server_default=func.now())