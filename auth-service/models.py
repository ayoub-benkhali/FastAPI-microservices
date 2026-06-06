# Définition des colonnes et types des tables SQLAlchemy
from sqlalchemy import Column, Integer, String
# Classe de base utilisée pour créer les modèles SQLAlchem
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)