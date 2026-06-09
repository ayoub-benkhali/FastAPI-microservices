# importe BaseSettings de pydantic_settings pour gérer les configurations
# pydantic_settings : lit les variables d'environnement et les valide avec Pydantic
from pydantic_settings import BaseSettings


# Classe de configuration héritant de BaseSettings
class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:ayoub@localhost:5432/location_db"

# this class is used to load the environment variables from the .env file
    class Config:
        # env_file : fichier .env à charger pour les variables d'environnement (utile en prod)
        env_file = ".env"

settings = Settings() # instance unique importée partout dans l'app pour accéder aux configs (ex: settings.DATABASE_URL)