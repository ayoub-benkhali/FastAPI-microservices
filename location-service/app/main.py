from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import location

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="Location Service", version="1.0.0", lifespan=lifespan)

# CORS — autorise Flutter Web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # en prod : mettre l'URL Flutter
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(location.router)