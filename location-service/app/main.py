from fastapi import FastAPI
# CORSMiddleware : autorise les requêtes cross-origin (ex: Flutter Web sur un autre port)
from fastapi.middleware.cors import CORSMiddleware
# asynccontextmanager : transforme une fonction async en context manager
# utilisé pour définir le cycle de vie (startup/shutdown) de l'app
from contextlib import asynccontextmanager
# importe le moteur de base de données asynchrone et les modèles
from app.database import engine, Base
from app.routers import location


# Crée une fonction asynchrone qui gère le cycle de vie de l'application
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # crée toutes les tables dans la base de données si elles n'existent pas
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Code exécuté à l'ARRÊT de l'application
    # libère les ressources de la base de données (ferme les connexions)
    await engine.dispose()

app = FastAPI(title="Location Service", version="1.0.0", lifespan=lifespan)

# Configuration CORS (Cross-Origin Resource Sharing)
# CORS — autorise Flutter Web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # en prod : mettre l'URL Flutter
    allow_methods=["*"], # autorise tous les verbes HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], # autorise tous les headers dans les requêtes
)

# inclut tous les endpoints du routeur location
app.include_router(location.router)