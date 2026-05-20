import os

# CRÍTICO: antes de cualquier import de app
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
from app import models

import sys
print("=== SYS PATH ===", sys.path)
print("=== LOADED APP FILE ===", db_module.__file__)




from sqlalchemy.pool import StaticPool

@pytest.fixture
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    db_module.engine = original_engine
    db_module.SessionLocal = original_session
    Base.metadata.drop_all(engine)
    engine.dispose()


# ── Helpers ──────────────────────────────────────────────────────────────────

_REG_BASE = {
    "nombre_comercial": "Papelería Test",
    "nit_o_cedula": "900001001",
    "email": "admin@papeleria.com",
    "password": "testpass123",
    "rol": "admin",
}

def registrar_admin(client, overrides=None):
    """Registra empresa+admin, devuelve {token, empresa_id, usuario_id}."""
    payload = {**_REG_BASE, **(overrides or {})}
    r = client.post("/auth/registro", json=payload)
    assert r.status_code == 201, r.text
    body = r.json()
    return {
        "token": body["access_token"],
        "empresa_id": body["usuario"]["empresa_id"],
        "usuario_id": body["usuario"]["id"],
    }

def auth(token):
    return {"Authorization": f"Bearer {token}"}

_PRODUCTO_BASE = {
    "nombre": "Cuaderno cuadriculado",
    "codigo_barras": "7702011000001",
    "precio_costo": 3500,
    "precio_venta": 5000,
    "cantidad_actual": 20,
    "stock_minimo": 5,
    "categoria": "Utiles escolares",
    "unidad_medida": "unidad",
}

def crear_producto(client, token, overrides=None):
    import uuid
    payload = {
        "empresa_id": str(uuid.uuid4()),
        **_PRODUCTO_BASE,
        **(overrides or {}),
    }
    r = client.post("/productos/", json=payload, headers=auth(token))
    assert r.status_code == 201, r.text
    return r.json()


def registrar_tendero(client, admin_token, empresa_id, email="tendero@papeleria.com", password="tenderopass123"):
    """Crea un cajero y devuelve {token, id}. empresa_id requerida por UsuarioCrear aunque el router la sobreescribe."""
    r = client.post("/usuarios/", json={
        "email": email,
        "password": password,
        "empresa_id": str(empresa_id),
        "rol": "tendero",
    }, headers=auth(admin_token))
    assert r.status_code == 201, r.text
    login_r = client.post("/auth/login", json={"email": email, "password": password})
    assert login_r.status_code == 200
    return {
        "token": login_r.json()["access_token"],
        "id": r.json()["id"],
    }
