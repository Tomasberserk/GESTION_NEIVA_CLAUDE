import os

# CRÍTICO: sobreescribir ANTES de cualquier import de app.
# load_dotenv() en database.py usa override=False por defecto,
# así que si la variable ya existe en el entorno, no la pisa.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ.setdefault("SECRET_KEY", "pytest-secret-key-not-for-production")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

import app.database as db_module
from app.main import app
from app.database import Base, get_db


@pytest.fixture
def client():
    """
    Cliente HTTP con BD SQLite en memoria limpia por cada test.

    Parcheamos directamente app.database.engine y SessionLocal para que
    las queries de los routers usen la misma conexión donde creamos las tablas.
    Un engine :memory: separado sería una BD diferente — por eso fallaban antes.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    # Crear todas las tablas en ESTE engine
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Parchear el módulo global para que los routers usen este engine
    original_engine = db_module.engine
    original_session = db_module.SessionLocal
    db_module.engine = engine
    db_module.SessionLocal = TestSession

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Restaurar estado original
    app.dependency_overrides.clear()
    db_module.engine = original_engine
    db_module.SessionLocal = original_session
    Base.metadata.drop_all(engine)
    engine.dispose()
