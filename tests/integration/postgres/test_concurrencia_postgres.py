"""Suite de Integracion PostgreSQL para Concurrencia Real y Bloqueos Pesimistas.

Esta suite ejecuta pruebas contra una base de datos PostgreSQL real viva
sin ningun tipo de bloqueo artificial de Python (ZERO db_lock).

Demuestra empíricamente:
1. Carrera simultánea por el mismo command_id en PostgreSQL:
   PostgreSQL lanza IntegrityError (psycopg2.errors.UniqueViolation) en uq_empresa_command_id,
   el orquestador recupera idempotentemente el resultado y el stock se descuenta exactamente una vez.
2. SELECT FOR UPDATE a nivel de kernel de PostgreSQL con stock=1:
   Dos hilos concurrentes compiten por la última unidad. El kernel de PostgreSQL bloquea
   a la segunda transacción hasta que la primera hace commit. El stock final es 0.0 (jamás negativo).
3. Demostración explícita de tiempo de bloqueo en kernel:
   Mide el bloqueo de SELECT FOR UPDATE demostrando que el hilo 2 queda suspendido
   en el motor PostgreSQL mientras el hilo 1 mantiene la transacción abierta.
4. Cero Lost Updates en reabastecimiento concurrente:
   Dos hilos agregan stock simultáneamente bajo transacciones independientes; ambas adiciones
   quedan registradas en PostgreSQL (stock 10 + 5 + 5 = 20.0).
5. Violación de constraint a nivel SQLAlchemy/PostgreSQL:
   Prueba directa de que PostgreSQL levanta IntegrityError ante inserts duplicados en agent_commands.

Activación:
   $env:TEST_POSTGRES_URL="postgresql://postgres:postgres@localhost:5432/gestion_neiva_test"
   pytest tests/integration/postgres/ -v
"""

import asyncio
import concurrent.futures
import os
import threading
import time
import uuid
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
import app.models as models
from app.main import app
from app.services.agente.session_store import InMemorySessionStore, set_session_store_instance

POSTGRES_URL = (
    os.getenv("TEST_POSTGRES_URL")
    or os.getenv("POSTGRES_URL")
    or "postgresql://postgres:postgres@localhost:5432/gestion_neiva_test"
)


def _check_postgres_alive():
    try:
        import psycopg2
        conn = psycopg2.connect(POSTGRES_URL, connect_timeout=3)
        conn.close()
        return True
    except Exception:
        return False


PG_ALIVE = _check_postgres_alive()

pytestmark = pytest.mark.skipif(
    not PG_ALIVE,
    reason=f"PostgreSQL no está disponible en {POSTGRES_URL}. Configure TEST_POSTGRES_URL o inicie el servicio."
)


@pytest.fixture(scope="module")
def pg_env():
    """Configura el motor PostgreSQL con connection pool real y crea las tablas."""
    engine = create_engine(POSTGRES_URL, pool_size=10, max_overflow=5)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    yield engine, SessionLocal
    engine.dispose()


@pytest.fixture
def pg_client(pg_env):
    """Provee un TestClient de FastAPI conectado directamente a PostgreSQL."""
    engine, SessionLocal = pg_env
    store = InMemorySessionStore()
    set_session_store_instance(store)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client, SessionLocal
    app.dependency_overrides.clear()


def _registrar_tienda_pg(client: TestClient, prefijo: str):
    email = f"tendero_{prefijo}_{uuid.uuid4().hex[:6]}@test.com"
    resp = client.post(
        "/auth/registro-completo",
        json={
            "nombre_comercial": f"Tienda PG {prefijo}",
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


def _crear_producto_pg(
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
# 1. Carrera concurrente por el mismo command_id (FastAPI + PostgreSQL real, ZERO db_lock)
# ---------------------------------------------------------------------------

def test_postgres_concurrencia_dos_confirmaciones_mismo_command_id(pg_client):
    """Verifica que dos hilos simultáneos confirmando el mismo command_id sin ningún lock de Python
    son arbitrados por la restricción UNIQUE de PostgreSQL (uq_empresa_command_id).
    El stock se descuenta exactamente una vez y ambas respuestas son EXECUTED."""
    client, SessionLocal = pg_client
    headers, empresa_id = _registrar_tienda_pg(client, "cmd_pg")
    prod = _crear_producto_pg(
        client, headers, empresa_id, "Arroz Diana PG 1kg", 3000, 4500, 10.0, f"BAR-CMD-{uuid.uuid4().hex[:6]}"
    )
    prod_id = prod["id"]

    # 1. Iniciar conversación para preparar pending_command y command_id
    r_ini = client.post(
        "/api/agente/mensaje",
        headers=headers,
        json={"mensaje": "Vendi 2 Arroz Diana PG"},
    )
    assert r_ini.status_code == 200
    data_ini = r_ini.json()
    assert data_ini["estado"] == "READY_TO_CONFIRM"
    conv_id = data_ini["conversation_id"]
    command_id = data_ini["command_id"]
    assert command_id is not None

    # 2. Ejecutar 2 confirmaciones simultáneas con Barrier - CERO db_lock
    barrier = threading.Barrier(2)
    respuestas = []

    def _confirmar():
        barrier.wait()  # Ambos hilos se disparan al mismo microsegundo
        t_client = TestClient(app)
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

    respuestas = [res1, res2]

    # Ambas solicitudes deben responder 200 OK y estado EXECUTED
    assert respuestas[0][0] == 200
    assert respuestas[1][0] == 200
    assert respuestas[0][1]["estado"] == "EXECUTED"
    assert respuestas[1][1]["estado"] == "EXECUTED"

    # Verificación en base de datos PostgreSQL:
    # 1. Stock descontado EXACTAMENTE una sola vez (10.0 - 2.0 = 8.0)
    db = SessionLocal()
    try:
        p_db = db.query(models.Producto).filter(models.Producto.id == prod_id).first()
        assert float(p_db.cantidad_actual) == 8.0, f"Stock esperado 8.0 pero fue {p_db.cantidad_actual}"

        # 2. Exactamente 1 registro persistido en agent_commands en PostgreSQL
        cmds = db.query(models.AgentCommand).filter(models.AgentCommand.command_id == command_id).all()
        assert len(cmds) == 1, f"Esperado 1 registro en agent_commands pero se hallaron {len(cmds)}"
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 2. Carrera concurrente por última unidad: stock=1 (SELECT FOR UPDATE en PostgreSQL)
# ---------------------------------------------------------------------------

def test_postgres_concurrencia_dos_ventas_compitiendo_stock_uno(pg_client):
    """Verifica que dos ventas concurrentes compitiendo por la última unidad en PostgreSQL
    son arbitradas a nivel de fila por SELECT FOR UPDATE.
    Exactamente una venta se ejecuta, la otra es rechazada por stock insuficiente,
    y el stock final en PostgreSQL es 0.0 (jamás negativo). CERO db_lock."""
    client, SessionLocal = pg_client
    headers, empresa_id = _registrar_tienda_pg(client, "stock1_pg")
    prod = _crear_producto_pg(
        client, headers, empresa_id, "Ultima Cerveza Poker PG", 2000, 3500, 1.0, f"BAR-POKER-{uuid.uuid4().hex[:6]}"
    )
    prod_id = prod["id"]

    # Crear dos conversaciones distintas para la misma empresa
    r_c1 = client.post("/api/agente/mensaje", headers=headers, json={"mensaje": "Vendi 1 Ultima Cerveza Poker"})
    assert r_c1.status_code == 200 and r_c1.json()["estado"] == "READY_TO_CONFIRM"
    conv_1 = r_c1.json()["conversation_id"]

    r_c2 = client.post("/api/agente/mensaje", headers=headers, json={"mensaje": "Vendi 1 Ultima Cerveza Poker"})
    assert r_c2.status_code == 200 and r_c2.json()["estado"] == "READY_TO_CONFIRM"
    conv_2 = r_c2.json()["conversation_id"]

    barrier = threading.Barrier(2)

    def _confirmar(c_id):
        barrier.wait()  # Disparo simultáneo a PostgreSQL sin locks de Python
        t_client = TestClient(app)
        return t_client.post(
            "/api/agente/mensaje",
            headers=headers,
            json={"mensaje": "si", "conversation_id": c_id},
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(_confirmar, conv_1)
        f2 = executor.submit(_confirmar, conv_2)
        resp1 = f1.result()
        resp2 = f2.result()

    assert resp1.status_code == 200
    assert resp2.status_code == 200

    estados = [resp1.json()["estado"], resp2.json()["estado"]]
    assert "EXECUTED" in estados, "Al menos una venta debió ejecutarse exitosamente"
    # La otra solicitud debe haber sido invalidada o rechazada por stock insuficiente
    assert "INVALIDATED" in estados or any("stock" in r.json().get("respuesta", "").lower() for r in [resp1, resp2])

    # Verificar stock en PostgreSQL: DEBE ser exactamente 0.0, JAMÁS negativo (-1.0)
    db = SessionLocal()
    try:
        p_db = db.query(models.Producto).filter(models.Producto.id == prod_id).first()
        assert float(p_db.cantidad_actual) == 0.0, f"Stock debió ser exactamente 0.0 pero fue {p_db.cantidad_actual}"
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 3. Demostración explícita de bloqueo en el kernel de PostgreSQL (SELECT FOR UPDATE)
# ---------------------------------------------------------------------------

def test_postgres_kernel_row_lock_select_for_update_demostracion(pg_env):
    """Demuestra físicamente que SELECT FOR UPDATE en PostgreSQL suspende al segundo hilo
    a nivel de socket/kernel del motor de base de datos hasta que el primer hilo hace commit."""
    engine, SessionLocal = pg_env

    # 1. Crear empresa y producto con stock = 1.0
    db_init = SessionLocal()
    emp = models.Empresa(
        nombre_comercial="Tienda Kernel Lock Test",
        nit_o_cedula=f"NIT-KL-{uuid.uuid4().hex[:8]}"
    )
    db_init.add(emp)
    db_init.flush()

    prod = models.Producto(
        empresa_id=emp.id,
        nombre="Cerveza Bloqueo Kernel",
        codigo_barras=f"BAR-KL-{uuid.uuid4().hex[:8]}",
        precio_costo=2000,
        precio_venta=3500,
        cantidad_actual=1.0,
        unidad_medida="unidad",
        categoria=models.CategoriaProducto.BEBIDAS,
    )
    db_init.add(prod)
    db_init.commit()
    prod_id = prod.id
    db_init.close()

    # Eventos de sincronización para medir el tiempo de bloqueo en PostgreSQL
    t1_has_lock = threading.Event()
    results = {}
    wait_durations = {}

    def hilo_1_toma_lock():
        s1 = SessionLocal()
        try:
            # Hilo 1 adquiere SELECT FOR UPDATE
            p1 = s1.query(models.Producto).filter(models.Producto.id == prod_id).with_for_update().first()
            t1_has_lock.set()  # Avisa al hilo 2 que el lock ya está adquirido
            time.sleep(0.35)   # Mantiene el lock en el kernel de PostgreSQL por 350ms
            p1.cantidad_actual -= Decimal("1.0")
            s1.commit()
            results["hilo_1"] = "VENTA_EXITOSA"
        except Exception as e:
            s1.rollback()
            results["hilo_1"] = f"ERROR: {e}"
        finally:
            s1.close()

    def hilo_2_espera_en_kernel_postgres():
        t1_has_lock.wait()  # Espera a que el hilo 1 ya tenga el lock en PostgreSQL
        s2 = SessionLocal()
        t_start = time.time()
        try:
            # Hilo 2 intenta SELECT FOR UPDATE. PostgreSQL DEBE SUSPENDERLO aquí hasta el commit del Hilo 1!
            p2 = s2.query(models.Producto).filter(models.Producto.id == prod_id).with_for_update().first()
            elapsed = time.time() - t_start
            wait_durations["hilo_2_bloqueo_segundos"] = elapsed

            if p2.cantidad_actual < Decimal("1.0"):
                results["hilo_2"] = "STOCK_INSUFICIENTE"
                s2.rollback()
            else:
                p2.cantidad_actual -= Decimal("1.0")
                s2.commit()
                results["hilo_2"] = "VENTA_EXITOSA"
        except Exception as e:
            s2.rollback()
            results["hilo_2"] = f"ERROR: {e}"
        finally:
            s2.close()

    th1 = threading.Thread(target=hilo_1_toma_lock)
    th2 = threading.Thread(target=hilo_2_espera_en_kernel_postgres)

    th1.start()
    th2.start()
    th1.join()
    th2.join()

    # Verificaciones de prueba empírica:
    assert results["hilo_1"] == "VENTA_EXITOSA"
    assert results["hilo_2"] == "STOCK_INSUFICIENTE"

    # El hilo 2 tuvo que esperar en el kernel de PostgreSQL al menos 0.25s mientras el hilo 1 dormía
    assert wait_durations.get("hilo_2_bloqueo_segundos", 0) >= 0.25, (
        f"El hilo 2 no esperó el tiempo de bloqueo en PostgreSQL: {wait_durations}"
    )

    # El stock final en PostgreSQL es exactamente 0.0
    db_check = SessionLocal()
    try:
        p_check = db_check.query(models.Producto).filter(models.Producto.id == prod_id).first()
        assert p_check.cantidad_actual == Decimal("0.0"), f"Stock debió ser 0.0 pero fue {p_check.cantidad_actual}"
    finally:
        db_check.close()


# ---------------------------------------------------------------------------
# 4. Reabastecimiento concurrente: cero Lost Updates en PostgreSQL
# ---------------------------------------------------------------------------

def test_postgres_concurrencia_reabastecimiento_sin_lost_update(pg_client):
    """Verifica que dos operaciones concurrentes de reabastecimiento en PostgreSQL
    actualizan el stock de forma atómica sin perder actualizaciones (10 + 5 + 5 = 20.0). CERO db_lock."""
    client, SessionLocal = pg_client
    headers, empresa_id = _registrar_tienda_pg(client, "reab_pg")
    prod = _crear_producto_pg(
        client, headers, empresa_id, "Aceite Diana PG 1L", 5000, 8000, 10.0, f"BAR-ACEITE-{uuid.uuid4().hex[:6]}"
    )
    prod_id = prod["id"]

    # Iniciar dos reabastecimientos en dos conversaciones
    r1 = client.post("/api/agente/mensaje", headers=headers, json={"mensaje": "Llegaron 5 Aceite Diana PG"})
    assert r1.status_code == 200 and r1.json()["estado"] == "READY_TO_CONFIRM"
    c1 = r1.json()["conversation_id"]

    r2 = client.post("/api/agente/mensaje", headers=headers, json={"mensaje": "Llegaron 5 Aceite Diana PG"})
    assert r2.status_code == 200 and r2.json()["estado"] == "READY_TO_CONFIRM"
    c2 = r2.json()["conversation_id"]

    barrier = threading.Barrier(2)

    def _confirmar(c_id):
        barrier.wait()  # Disparo simultáneo sin locks de Python
        t_client = TestClient(app)
        return t_client.post(
            "/api/agente/mensaje",
            headers=headers,
            json={"mensaje": "si", "conversation_id": c_id},
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(_confirmar, c1)
        f2 = executor.submit(_confirmar, c2)
        resp1 = f1.result()
        resp2 = f2.result()

    assert resp1.status_code == 200 and resp1.json()["estado"] == "EXECUTED"
    assert resp2.status_code == 200 and resp2.json()["estado"] == "EXECUTED"

    # Verificar stock en PostgreSQL: 10 + 5 + 5 = exactamente 20.0
    db = SessionLocal()
    try:
        p_db = db.query(models.Producto).filter(models.Producto.id == prod_id).first()
        assert float(p_db.cantidad_actual) == 20.0, f"Esperado 20.0 pero fue {p_db.cantidad_actual}"
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 5. Violación de restricción UNIQUE directa en PostgreSQL (IntegrityError nativo)
# ---------------------------------------------------------------------------

def test_postgres_directa_integrity_violation_command_id(pg_env):
    """Demuestra que la restricción UNIQUE (empresa_id, command_id) en PostgreSQL
    lanza físicamente un IntegrityError (psycopg2.errors.UniqueViolation) ante inserciones simultáneas."""
    engine, SessionLocal = pg_env
    from sqlalchemy.exc import IntegrityError

    db_init = SessionLocal()
    emp = models.Empresa(
        nombre_comercial="Tienda Unique Test",
        nit_o_cedula=f"NIT-UQ-{uuid.uuid4().hex[:8]}"
    )
    db_init.add(emp)
    db_init.commit()
    emp_id = emp.id
    db_init.close()

    cmd_id = f"cmd_uq_test_{uuid.uuid4().hex[:8]}"
    barrier = threading.Barrier(2)
    resultados = {}

    def insertar_comando(hilo_num):
        s = SessionLocal()
        barrier.wait()
        try:
            import json
            cmd = models.AgentCommand(
                empresa_id=emp_id,
                conversation_id=f"conv_{uuid.uuid4().hex[:6]}",
                command_id=cmd_id,
                action="registrar_venta",
                payload=json.dumps({"test": True}),
                status="COMPLETED",
                result=json.dumps({"ok": True}),
            )
            s.add(cmd)
            s.commit()
            resultados[hilo_num] = "INSERT_EXITOSO"
        except IntegrityError as e:
            s.rollback()
            resultados[hilo_num] = "INTEGRITY_ERROR_CAPTURADO"
        finally:
            s.close()

    th1 = threading.Thread(target=insertar_comando, args=("hilo_1",))
    th2 = threading.Thread(target=insertar_comando, args=("hilo_2",))
    th1.start()
    th2.start()
    th1.join()
    th2.join()

    # Exactamente uno insertó exitosamente y el otro fue rechazado por PostgreSQL
    vals = list(resultados.values())
    assert "INSERT_EXITOSO" in vals
    assert "INTEGRITY_ERROR_CAPTURADO" in vals

    # En la tabla de PostgreSQL sólo existe 1 fila
    db_check = SessionLocal()
    try:
        cmds = db_check.query(models.AgentCommand).filter(
            models.AgentCommand.empresa_id == emp_id,
            models.AgentCommand.command_id == cmd_id
        ).all()
        assert len(cmds) == 1
    finally:
        db_check.close()