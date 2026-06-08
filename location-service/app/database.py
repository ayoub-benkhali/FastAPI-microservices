# create_async_engine : crée le moteur SQLAlchemy asynchrone (connexion à PostgreSQL)
# AsyncSession : session DB asynchrone (execute, commit, rollback)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

# creat session and engine for database connection
# echo to True to see the sql queries in the console
engine = create_async_engine(settings.DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker( bind=engine, class_=AsyncSession, expire_on_commit=False )

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session # donne la session à la route
            await session.commit() # commit automatique si tout s'est bien passé
        except Exception:
            await session.rollback() # annule tout en cas d'erreur
            raise