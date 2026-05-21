import os
import uuid
import pytest
from sqlalchemy import create_engine, TypeDecorator, CHAR
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.postgresql import UUID
from fastapi.testclient import TestClient

# Establecer variables de entorno para pruebas
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ.setdefault("SECRET_KEY", "super-secret-key-for-jwt-distribuidora-mayorista-medium")
os.environ.setdefault("ENVIRONMENT", "testing")

import app.database as db_module
from app.database import Base, get_db
from app.main import app


# TypeDecorator para UUID en SQLite
class GUID(TypeDecorator):
    """Platform-independent GUID type that uses CHAR(32) on SQLite."""
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return str(value)
        if not isinstance(value, uuid.UUID):
            return str(uuid.UUID(value)) if value else None
        return str(value).replace('-', '')

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            return uuid.UUID(value) if value else None
        return value


@pytest.fixture
def client():
    # Convertir dinámicamente columnas UUID a GUID para compatibilidad con SQLite
    for table in Base.metadata.tables.values():
        for column in table.columns:
            if isinstance(column.type, UUID):
                column.type = GUID()

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Crear tablas
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Parchear engine y sessionmaker locales del módulo database
    original_engine = db_module.engine
    original_session = db_module.SessionLocal
    db_module.engine = engine
    db_module.SessionLocal = TestSession

    def override_get_db():
        db = TestSession()
        try:
            yield db
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Restaurar
    app.dependency_overrides.clear()
    db_module.engine = original_engine
    db_module.SessionLocal = original_session
    Base.metadata.drop_all(engine)
    engine.dispose()
