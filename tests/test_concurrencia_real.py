"""Suite de Pruebas de Concurrencia Real, Idempotencia y Blindaje de Produccion.

Verifica:
1. Concurrencia simultanea multi-hilo (ThreadPoolExecutor + Barrier) con el mismo command_id sin locks (ZERO db_lock).
2. Carrera por stock=1 entre dos ventas concurrentes (SELECT FOR UPDATE en PostgreSQL, stock jamas negativo).
3. Endurecimiento de confirmacion: rechazo de expresiones ambiguas (si, pero..., espera) y aceptacion de inequivocos.
4. Inyeccion y saneamiento de cantidades hostiles (NaN, Infinity, 0, negativos, 1e309).
5. Fail-closed de Redis en produccion (503 Service Unavailable, cero fallback a InMemory).
6. Reabastecimiento concurrente sin lost updates (atómico en motor relacional).
"""

import concurrent.futures
import math
import os
import threading
import uuid
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base, get_db
from app.main import app
from app.services.agente import session_store
from app.services.agente.session_store import (
    InMemorySessionStore,
    SessionStoreUnavailableError,
    set_session_store_instance,
    get_session_store,
)

POSTGRES_URL = (
    os.getenv("TEST_POSTGRES_URL")
    or os.getenv("POSTGRES_URL")
    or "postgresql://postgres:postgres@localhost:5432/gestion_neiva_test"
)


def _is_pg_alive():
    try:
        import psycopg2
        conn = psycopg2.connect(POSTGRES_URL, connect_timeout=2)
        conn.close()
        return True
    except Exception:
        return False


PG_AVAILABLE = _is_pg_alive()


@pytest.fixture(autouse=True)
def reset_session_store():
    store = InMemorySessionStore()
    set_session_store_instance(store)
    yield store
    store.clear()


@pytest.fixture
def client(client):
    """Si PostgreSQL esta activo, habilita pool multi-conexion real para concurrencia multi-hilo pura.
    Sin esto (ej. SQLite en memoria de un solo hilo), no se puede ejecutar concurrencia real sin locks."""
    if not PG_AVAILABLE:
        yield client
        return

    engine = create_engine(POSTGRES_URL, pool_size=10, max_overflow=5)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    pg_client = TestClient(app)
    yield pg_client
    app.dependency_overrides.clear()
    engine.dispose()


def _registrar_tienda_concurrente(client: TestClient, prefijo: str):
    email = f"tendero_{prefijo}_{uuid.uuid4().hex[:6]}@test.com"
    resp = client.post(
        "/auth/registro-completo",
        json={
            "nombre_comercial": f"Tienda {prefijo}",
            "nit_o_cedula": f"NIT-{uuid.uuid4().hex[:8]}",
            "email": email,
            "password": "Password123!",
            "rol": "admin",
        },
    )
    assert resp.status_code == 201, resp.json()
    data = resp.json()
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    empresa_id = data["usuario"]["empresa_id"]
    return headers, empresa_id


def _crear_producto_concurrente(
    client: TestClient,
    headers: dict,
    empresa_id: str,
    nombre: str,
    precio_costo: float,
    precio_venta: float,
    cantidad: float,
    codigo_barras: str,
) -> dict:
    resp = client.post(
        "/productos/",
        headers=headers,
        json={
            "empresa_id": empresa_id,
            "nombre": nombre,
            "codigo_barras": codigo_barras,
            "precio_costo": precio_costo,
            "precio_venta": precio_venta,
            "cantidad_actual": cantidad,
            "unidad_medida": "unidad",
            "categoria": "Bebidas",
        },
    )
    assert resp.status_code == 201, resp.json()
    return resp.json()


# ---------------------------------------------------------------------------
# 1. Dos confirmaciones exactamente simultaneas con el mismo command_id (CERO db_lock)
# ---------------------------------------------------------------------------

def test_concurrencia_dos_confirmaciones_mismo_command_id(client):
    if not PG_AVAILABLE:
        pytest.skip("Concurrencia real sin locks requiere PostgreSQL.")

    headers, empresa_id = _registrar_tienda_concurrente(client, "conc_cmd")
    prod = _crear_producto_concurrente(
        client, headers, empresa_id, "Arroz Diana 1kg", 3000, 4500, 10, f"BAR-CONC-{uuid.uuid4().hex[:6]}"
    )
    prod_id = prod["id"]

    # 1. Iniciar venta para llegar a READY_TO_CONFIRM
    r_ini = client.post(
        "/api/agente/mensaje",
        headers=headers,
        json={"mensaje": "Vendi 2 Arroz Diana"},
    )
    assert r_ini.status_code == 200
    data_ini = r_ini.json()
    assert data_ini["estado"] == "READY_TO_CONFIRM"
    conv_id = data_ini["conversation_id"]
    command_id = data_ini["command_id"]
    assert command_id is not None

    # 2. Ejecutar 2 confirmaciones simultaneas con ThreadPoolExecutor y Barrier — CERO db_lock
    barrier = threading.Barrier(2)

    def _confirmar():
        barrier.wait()
        t_client = TestClient(client.app)
        resp = t_client.post(
            "/api/agente/mensaje",
            headers=headers,
            json={"mensaje": "si", "conversation_id": conv_id},
        )
        return resp.status_code, resp.json()

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(_confirmar)
        f2 = executor.submit(_confirmar)
        res1 = f1.result()
        res2 = f2.result()

    resultados = [res1, res2]

    # Ambas peticiones deben responder 200 OK
    assert resultados[0][0] == 200
    assert resultados[1][0] == 200

    estados = [r[1]["estado"] for r in resultados]
    assert all(e == "EXECUTED" for e in estados)

    # Verificacion de integridad en la base de datos: Stock descontado EXACTAMENTE una vez (10 - 2 = 8)
    r_prod = client.get(f"/productos/{prod_id}", headers=headers)
    assert r_prod.status_code == 200
    assert float(r_prod.json()["cantidad_actual"]) == 8.0


# ---------------------------------------------------------------------------
# 2. Carrera concurrente por ultima unidad (Stock = 1, dos ventas concurrentes de 1)
# ---------------------------------------------------------------------------

def test_concurrencia_dos_ventas_compitiendo_stock_uno(client):
    if not PG_AVAILABLE:
        pytest.skip("Concurrencia real sin locks requiere PostgreSQL.")

    headers, empresa_id = _registrar_tienda_concurrente(client, "conc_stock1")
    prod = _crear_producto_concurrente(
        client, headers, empresa_id, "Ultima Cerveza Aguila", 2000, 3500, 1.0, f"BAR-AGUILA-{uuid.uuid4().hex[:6]}"
    )
    prod_id = prod["id"]

    # Iniciar conversacion 1
    r_c1 = client.post(
        "/api/agente/mensaje",
        headers=headers,
        json={"mensaje": "Vendi 1 Ultima Cerveza Aguila"},
    )
    assert r_c1.status_code == 200
    d_c1 = r_c1.json()
    assert d_c1["estado"] == "READY_TO_CONFIRM"
    conv_1 = d_c1["conversation_id"]

    # Iniciar conversacion 2
    r_c2 = client.post(
        "/api/agente/mensaje",
        headers=headers,
        json={"mensaje": "Vendi 1 Ultima Cerveza Aguila"},
    )
    assert r_c2.status_code == 200
    d_c2 = r_c2.json()
    assert d_c2["estado"] == "READY_TO_CONFIRM"
    conv_2 = d_c2["conversation_id"]

    barrier = threading.Barrier(2)

    def _confirmar_conv(c_id):
        barrier.wait()
        t_client = TestClient(client.app)
        return t_client.post(
            "/api/agente/mensaje",
            headers=headers,
            json={"mensaje": "confirmar", "conversation_id": c_id},
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(_confirmar_conv, conv_1)
        f2 = executor.submit(_confirmar_conv, conv_2)
        resp1 = f1.result()
        resp2 = f2.result()

    assert resp1.status_code == 200
    assert resp2.status_code == 200

    estados = [resp1.json()["estado"], resp2.json()["estado"]]
    assert "EXECUTED" in estados
    assert "INVALIDATED" in estados or any("stock" in r.json().get("respuesta", "").lower() for r in [resp1, resp2])

    # Stock en BD debe ser EXACTAMENTE 0.0, JAMAS negativo
    r_prod = client.get(f"/productos/{prod_id}", headers=headers)
    assert r_prod.status_code == 200
    stock_final = float(r_prod.json()["cantidad_actual"])
    assert stock_final == 0.0


# ---------------------------------------------------------------------------
# 3. Endurecimiento de confirmacion (Expresiones inequivocas vs ambiguas)
# ---------------------------------------------------------------------------

def test_hardening_confirmacion_inequivoca(client):
    headers, empresa_id = _registrar_tienda_concurrente(client, "hard_conf")
    _crear_producto_concurrente(
        client, headers, empresa_id, "Pan Tajado Bimbo", 4000, 6000, 15, f"BAR-PAN-{uuid.uuid4().hex[:6]}"
    )

    r1 = client.post(
        "/api/agente/mensaje",
        headers=headers,
        json={"mensaje": "Vendi 2 Pan Tajado Bimbo"},
    )
    assert r1.status_code == 200
    conv_id = r1.json()["conversation_id"]
    assert r1.json()["estado"] == "READY_TO_CONFIRM"

    # Intento 1: "si, pero quiero cambiar la cantidad" -> NO debe confirmar
    r_ambiguo = client.post(
        "/api/agente/mensaje",
        headers=headers,
        json={"mensaje": "si, pero quiero cambiar la cantidad", "conversation_id": conv_id},
    )
    assert r_ambiguo.status_code == 200
    d_amb = r_ambiguo.json()
    assert d_amb["estado"] == "READY_TO_CONFIRM"
    assert "tienes pendiente confirmar" in d_amb["respuesta"].lower()

    # Intento 2: "espera, pero si" -> NO debe confirmar
    r_espera = client.post(
        "/api/agente/mensaje",
        headers=headers,
        json={"mensaje": "espera, pero si", "conversation_id": conv_id},
    )
    assert r_espera.status_code == 200
    assert r_espera.json()["estado"] == "READY_TO_CONFIRM"

    # Intento 3: "no, si" -> Es cancelacion por comenzar con no / contradecir
    r_no_si = client.post(
        "/api/agente/mensaje",
        headers=headers,
        json={"mensaje": "no, si", "conversation_id": conv_id},
    )
    assert r_no_si.status_code == 200
    assert r_no_si.json()["estado"] == "REJECTED"


# ---------------------------------------------------------------------------
# 4. Validacion de inputs hostiles y valores extremos en cantidades
# ---------------------------------------------------------------------------

def test_validacion_cantidades_hostiles(client):
    headers, empresa_id = _registrar_tienda_concurrente(client, "hostil_qty")
    _crear_producto_concurrente(
        client, headers, empresa_id, "Leche Alqueria 1L", 3500, 4800, 50, f"BAR-LECHE-{uuid.uuid4().hex[:6]}"
    )

    cantidades_hostiles = [
        "Vendi 0 Leche Alqueria",
        "Vendi -5 Leche Alqueria",
        "Vendi 999999999 Leche Alqueria",
        "Vendi 1e309 Leche Alqueria",
        "Vendi NaN Leche Alqueria",
        "Vendi Infinity Leche Alqueria",
    ]

    for msg in cantidades_hostiles:
        resp = client.post(
            "/api/agente/mensaje",
            headers=headers,
            json={"mensaje": msg},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["estado"] != "READY_TO_CONFIRM"
        assert data["estado"] != "EXECUTED"


# ---------------------------------------------------------------------------
# 5. Redis obligatorio en produccion (Fail-closed sin fallback a InMemory)
# ---------------------------------------------------------------------------

def test_redis_produccion_fail_closed(monkeypatch, client):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("REDIS_URL", raising=False)
    set_session_store_instance(None)

    with pytest.raises(SessionStoreUnavailableError):
        get_session_store()

    monkeypatch.setenv("ENVIRONMENT", "test")
    set_session_store_instance(None)


# ---------------------------------------------------------------------------
# 6. Reabastecimiento concurrente (Proteccion contra Lost Update)
# ---------------------------------------------------------------------------

def test_concurrencia_reabastecimiento_lost_update(client):
    if not PG_AVAILABLE:
        pytest.skip("Concurrencia real sin locks requiere PostgreSQL.")

    headers, empresa_id = _registrar_tienda_concurrente(client, "conc_reab")
    prod = _crear_producto_concurrente(
        client, headers, empresa_id, "Aceite Diana 1L", 5000, 8000, 10.0, f"BAR-ACEITE-REAB-{uuid.uuid4().hex[:6]}"
    )
    prod_id = prod["id"]

    # Iniciar dos reabastecimientos en dos conversaciones
    r1 = client.post("/api/agente/mensaje", headers=headers, json={"mensaje": "Llegaron 5 Aceite Diana"})
    assert r1.status_code == 200 and r1.json()["estado"] == "READY_TO_CONFIRM"
    c1 = r1.json()["conversation_id"]

    r2 = client.post("/api/agente/mensaje", headers=headers, json={"mensaje": "Llegaron 5 Aceite Diana"})
    assert r2.status_code == 200 and r2.json()["estado"] == "READY_TO_CONFIRM"
    c2 = r2.json()["conversation_id"]

    barrier = threading.Barrier(2)

    def _confirmar(c_id):
        barrier.wait()
        t_client = TestClient(client.app)
        return t_client.post("/api/agente/mensaje", headers=headers, json={"mensaje": "si", "conversation_id": c_id})

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(_confirmar, c1)
        f2 = executor.submit(_confirmar, c2)
        resp1 = f1.result()
        resp2 = f2.result()

    assert resp1.status_code == 200 and resp1.json()["estado"] == "EXECUTED"
    assert resp2.status_code == 200 and resp2.json()["estado"] == "EXECUTED"

    # Verificar que el stock final es exactamente 10 + 5 + 5 = 20.0 (cero lost updates)
    r_prod = client.get(f"/productos/{prod_id}", headers=headers)
    assert r_prod.status_code == 200
    assert float(r_prod.json()["cantidad_actual"]) == 20.0