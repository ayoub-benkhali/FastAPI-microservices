from sqlalchemy import Column, Integer, DateTime, func
from geoalchemy2 import Geography          # PostGIS
from app.database import Base

class Location(Base):
    __tablename__ = "locations"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, nullable=False, index=True)
    geom       = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    created_at = Column(DateTime, server_default=func.now())