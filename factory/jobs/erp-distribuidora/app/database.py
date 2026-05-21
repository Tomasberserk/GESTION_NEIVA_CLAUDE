import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Si no está configurada, usamos SQLite local para que corra los tests sin fricción
    DATABASE_URL = "sqlite:///./erp_distribuidora.db"

_is_sqlite = DATABASE_URL.startswith("sqlite")
_engine_kwargs: dict = {
    "pool_pre_ping": not _is_sqlite,
    "echo": os.getenv("ENVIRONMENT") == "development",
}
if not _is_sqlite:
    _engine_kwargs["pool_size"] = 5
    _engine_kwargs["max_overflow"] = 10
if _is_sqlite:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **_engine_kwargs)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
