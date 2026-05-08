import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL no está configurada. "
        "Copia .env.example a .env y completa tus credenciales."
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # Detecta conexiones muertas antes de usarlas
    pool_size=10,         # Conexiones activas en el pool
    max_overflow=20,      # Conexiones adicionales permitidas bajo carga
    echo=os.getenv("ENVIRONMENT") == "development",
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency de FastAPI: provee una sesión de BD y garantiza su cierre."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
