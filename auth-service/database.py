# Création de la connexion (engine) vers la base de données
from sqlalchemy import create_engine
# sessionmaker : fabrique des objets Session pour exécuter les opérations CRUD sur la BD
# declarative_base : classe de base utilisée pour définir les modèles (tables) SQLAlchemy
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://postgres:ayoub@localhost:5432/microservices"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker( autocommit=False, autoflush=False, bind=engine )

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()