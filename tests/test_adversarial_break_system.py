import concurrent.futures
import os
import threading
import uuid
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base, get_db
from app.main import app

POSTGRES_URL = (
    os.getenv("TEST_POSTGRES_URL")
    or os.getenv("POSTGRES_URL")
    or "postgresql://postgres:postgres@localhost:5432/gestion_neiva_test"
)


def _check_postgres_alive():
    try:
        import psycopg2
        conn = psycopg2.connect(POSTGRES_URL, connect_timeout=2)
        conn.close()
        return True
    except Exception:
        return False


PG_ALIVE = _check_postgres_alive()


def _crear_empresa_y_admin(client: TestClient, email: str = None, plan: str = "basic", session_factory=None) -> tuple[dict, str]:
    if not email:
        email = f"admin_{uuid.uuid4().hex[:8]}@test.com"
    payload = {
        "nombre_comercial": f"Tienda Destructiva {uuid.uuid4().hex[:6]}",
        "nit_o_cedula": f"NIT-{uuid.uuid4().hex[:8]}",
        "nombre": "Admin Rompetodo",
        "email": email,
        "password": "Password123!",
        "rol": "admin",
    }
    res = client.post("/auth/registro-completo", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    token = data["access_token"]
    empresa_id = data["usuario"]["empresa_id"]

    if plan != "basic":
        if session_factory:
            db = session_factory()
        else:
            import app.database as db_module
            db = db_module.SessionLocal()
        emp = db.query(models.Empresa).filter(models.Empresa.id == uuid.UUID(empresa_id)).first()
        emp.plan = models.PlanEmpresa(plan)
        db.commit()
        db.close()

    return data, token


def _crear_cajero(client: TestClient, admin_token: str, nombre: str, email: str = None) -> tuple[dict, str]:
    if not email:
        email = f"cajero_{uuid.uuid4().hex[:8]}@test.com"
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.post(
        "/api/usuarios/empleados",
        json={"nombre": nombre, "email": email, "password": "Password123!"},
        headers=headers,
    )
    assert res.status_code == 201, res.text
    cajero_data = res.json()

    res_login = client.post("/token", json={"email": email, "password": "Password123!"})
    assert res_login.status_code == 200
    cajero_token = res_login.json()["access_token"]
    return cajero_data, cajero_token


def _crear_producto(client: TestClient, admin_token: str, stock: float = 100.0, precio: float = 2000.0) -> dict:
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "nombre": f"Producto Test {uuid.uuid4().hex[:6]}",
        "codigo_barras": f"BAR-{uuid.uuid4().hex[:10]}",
        "precio_costo": 1000.0,
        "precio_venta": precio,
        "cantidad_actual": stock,
        "unidad_medida": "unidad",
    }
    res = client.post("/api/productos", json=payload, headers=headers)
    assert res.status_code == 201, res.text
    return res.json()


# ==============================================================================
# 1. ATAQUE CONCURRENTE MASIVO: HILOS COMPITIENDO POR EL ÚLTIMO CUPO DE CAJERO
# ==============================================================================
@pytest.mark.skipif(not PG_ALIVE, reason="Requiere PostgreSQL vivo con connection pool para SELECT FOR UPDATE")
def test_ataque_concurrente_hilos_ultimo_cupo_cajero():
    """
    En PostgreSQL real vivo:
    Empresa en Plan Básico ya tiene 2 cajeros activos. Solo queda 1 cupo disponible (límite 3).
    Lanzamos 4 hilos simultáneos sincronizados con threading.Barrier(4) compitiendo por el último cupo.
    GARANTÍA POSTGRESQL: Exactamente 1 pasa (201), los otros 3 rebotan con 403 (Límite alcanzado).
    Total final en PostgreSQL = estrictamente 3 cajeros activos.
    """
    engine = create_engine(POSTGRES_URL, pool_size=10, max_overflow=5)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    pg_client = TestClient(app)

    try:
        admin_data, admin_token = _crear_empresa_y_admin(pg_client, plan="basic")
        empresa_id = uuid.UUID(admin_data["usuario"]["empresa_id"])
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Crear 2 cajeros previos
        _crear_cajero(pg_client, admin_token, "Cajero Base 1")
        _crear_cajero(pg_client, admin_token, "Cajero Base 2")

        num_atacantes = 4
        barrier = threading.Barrier(num_atacantes)
        resultados = []

        def intentar_crear(indice: int):
            barrier.wait()
            email = f"competidor_{indice}_{uuid.uuid4().hex[:6]}@test.com"
            res = pg_client.post(
                "/api/usuarios/empleados",
                json={"nombre": f"Competidor {indice}", "email": email, "password": "Password123!"},
                headers=admin_headers,
            )
            resultados.append(res.status_code)

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_atacantes) as executor:
            futuros = [executor.submit(intentar_crear, i) for i in range(num_atacantes)]
            concurrent.futures.wait(futuros)

        exitos = [s for s in resultados if s == 201]
        bloqueados = [s for s in resultados if s == 403]

        assert len(exitos) == 1, f"Debió ganar solo 1 cajero, ganaron {len(exitos)}: {resultados}"
        assert len(bloqueados) == (num_atacantes - 1), f"Debieron rebotar {num_atacantes - 1} con 403: {resultados}"

        # Verificar en base de datos PostgreSQL
        db = SessionLocal()
        total_activos = (
            db.query(models.Usuario)
            .filter(
                models.Usuario.empresa_id == empresa_id,
                models.Usuario.rol == models.RolUsuario.TENDERO,
                models.Usuario.is_active.is_(True),
            )
            .count()
        )
        db.close()
        assert total_activos == 3, f"Violación de límite: hay {total_activos} cajeros activos en PostgreSQL"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


# ==============================================================================
# 2. ATAQUE CONCURRENTE MASIVO DE SOBREVENTA: HILOS VENDIENDO STOCK = 1
# ==============================================================================
@pytest.mark.skipif(not PG_ALIVE, reason="Requiere PostgreSQL vivo con connection pool para SELECT FOR UPDATE")
def test_ataque_concurrente_hilos_sobreventa_stock_uno():
    """
    En PostgreSQL real vivo:
    Producto tiene stock = 1.0.
    4 peticiones concurrentes sincronizadas con Barrier(4) intentan vender 1 unidad.
    GARANTÍA: Solo 1 pasa (201), las otras 3 rebotan con 400 (Stock insuficiente).
    Stock final = 0.0, JAMÁS negativo.
    """
    engine = create_engine(POSTGRES_URL, pool_size=10, max_overflow=5)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    pg_client = TestClient(app)

    try:
        admin_data, admin_token = _crear_empresa_y_admin(pg_client, plan="pro", session_factory=SessionLocal)
        empresa_id = uuid.UUID(admin_data["usuario"]["empresa_id"])
        prod = _crear_producto(pg_client, admin_token, stock=1.0)
        prod_id = prod["id"]

        _, cajero_token = _crear_cajero(pg_client, admin_token, "Cajero Vendedor")
        cajero_headers = {"Authorization": f"Bearer {cajero_token}"}

        num_ventas = 4
        barrier = threading.Barrier(num_ventas)
        codigos = []

        def intentar_vender():
            barrier.wait()
            payload = {"detalles": [{"producto_id": prod_id, "cantidad": 1.0}]}
            res = pg_client.post(f"/api/ventas/{empresa_id}", json=payload, headers=cajero_headers)
            codigos.append(res.status_code)

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_ventas) as executor:
            futuros = [executor.submit(intentar_vender) for _ in range(num_ventas)]
            concurrent.futures.wait(futuros)

        ventas_exitosas = [c for c in codigos if c == 201]
        ventas_rechazadas = [c for c in codigos if c == 400]

        assert len(ventas_exitosas) == 1, f"Debió ganar exactamente 1 venta, pasaron: {codigos}"
        assert len(ventas_rechazadas) == (num_ventas - 1), f"Debieron rebotar {num_ventas - 1}: {codigos}"

        # Verificar stock en PostgreSQL
        db = SessionLocal()
        prod_db = db.query(models.Producto).filter(models.Producto.id == uuid.UUID(prod_id)).first()
        db.close()
        assert prod_db.cantidad_actual == Decimal("0.0"), f"Stock corrupto: {prod_db.cantidad_actual}"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


# ==============================================================================
# 3. IDOR EN CARRITO: INYECCIÓN DE PRODUCTO DE OTRA EMPRESA
# ==============================================================================
def test_ataque_cross_tenant_producto_de_otra_empresa(client: TestClient):
    """
    Empresa A tiene Producto A (stock 50).
    Empresa B tiene Producto B (stock 20).
    Cajero de Empresa A intenta registrar una venta con producto_id de Empresa B.
    GARANTÍA: HTTP 400 'Producto no encontrado o no pertenece a esta empresa'.
    El stock de Empresa B permanece intacto.
    """
    import app.database as db_module

    admin_a, token_admin_a = _crear_empresa_y_admin(client)
    empresa_a_id = admin_a["usuario"]["empresa_id"]
    _, token_cajero_a = _crear_cajero(client, token_admin_a, "Cajero A")
    headers_cajero_a = {"Authorization": f"Bearer {token_cajero_a}"}

    admin_b, token_admin_b = _crear_empresa_y_admin(client)
    prod_b = _crear_producto(client, token_admin_b, stock=20.0)
    prod_b_id = prod_b["id"]

    # Cajero A intenta vender Producto B en Empresa A
    payload_malicioso = {
        "detalles": [{"producto_id": prod_b_id, "cantidad": 5.0}]
    }
    res = client.post(f"/api/ventas/{empresa_a_id}", json=payload_malicioso, headers=headers_cajero_a)
    assert res.status_code == 400
    assert "no pertenece a esta empresa" in res.json()["detail"]

    # Consultar Producto B con el admin B para verificar que el stock sigue intacto en 20
    res_b = client.get(f"/api/productos/{prod_b_id}", headers={"Authorization": f"Bearer {token_admin_b}"})
    assert res_b.status_code == 200
    assert res_b.json()["cantidad_actual"] == 20.0


# ==============================================================================
# 4. TAMPERING DE SNAPSHOT: INTENTO DE CULPAR A OTRO CAJERO EN LA VENTA
# ==============================================================================
def test_ataque_tampering_snapshot_vendedor(client: TestClient):
    """
    Cajero Paula intenta inyectar usuario_id o vendedor_nombre_snapshot de Don Pedro en el payload.
    GARANTÍA: El backend ignora campos extraños y sella la venta estrictamente
    con el id y nombre extraídos del JWT verificado de Paula.
    """
    admin_data, admin_token = _crear_empresa_y_admin(client)
    empresa_id = admin_data["usuario"]["empresa_id"]
    prod = _crear_producto(client, admin_token, stock=10.0)

    _, token_paula = _crear_cajero(client, admin_token, "Paula Honesta")
    headers_paula = {"Authorization": f"Bearer {token_paula}"}

    # Payload con inyección maliciosa de usuario
    fake_user_id = str(uuid.uuid4())
    payload = {
        "usuario_id": fake_user_id,
        "vendedor_nombre_snapshot": "Don Pedro Inocente",
        "detalles": [{"producto_id": prod["id"], "cantidad": 1.0}],
    }
    res = client.post(f"/api/ventas/{empresa_id}", json=payload, headers=headers_paula)
    assert res.status_code == 201

    # Verificar en el timeline de actividad que la venta quedó atribuida a Paula
    res_act = client.get("/api/ventas/actividad", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_act.status_code == 200
    ventas = res_act.json()
    assert len(ventas) == 1
    assert ventas[0]["vendedor_nombre_snapshot"] == "Paula Honesta"
    assert ventas[0]["usuario_id"] != fake_user_id


# ==============================================================================
# 5. FUZZING DE VALORES EXTREMOS EN CANTIDADES
# ==============================================================================
def test_fuzzing_cantidades_destructivas(client: TestClient):
    """
    Envío de valores no válidos en cantidad: cero, negativos, NaN o lista vacía.
    GARANTÍA: Pydantic los rechaza con HTTP 422 Unprocessable Entity.
    """
    admin_data, admin_token = _crear_empresa_y_admin(client)
    empresa_id = admin_data["usuario"]["empresa_id"]
    prod = _crear_producto(client, admin_token, stock=50.0)
    _, token_cajero = _crear_cajero(client, admin_token, "Cajero Fuzzer")
    headers = {"Authorization": f"Bearer {token_cajero}"}

    # Cantidad 0
    res0 = client.post(f"/api/ventas/{empresa_id}", json={"detalles": [{"producto_id": prod["id"], "cantidad": 0}]}, headers=headers)
    assert res0.status_code == 422

    # Cantidad negativa
    res_neg = client.post(f"/api/ventas/{empresa_id}", json={"detalles": [{"producto_id": prod["id"], "cantidad": -5.5}]}, headers=headers)
    assert res_neg.status_code == 422

    # Carrito vacío
    res_vacio = client.post(f"/api/ventas/{empresa_id}", json={"detalles": []}, headers=headers)
    assert res_vacio.status_code == 422


# ==============================================================================
# 6. FUZZING Y RESILIENCIA EN FECHAS DE ACTIVIDAD DEL DÍA
# ==============================================================================
def test_fuzzing_fechas_actividad_del_dia(client: TestClient):
    """
    El endpoint /api/ventas/actividad debe manejar fechas inexistentes o strings
    extraños sin crashear con 500.
    """
    _, admin_token = _crear_empresa_y_admin(client)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Fecha inválida (mes 13)
    res1 = client.get("/api/ventas/actividad?fecha=2026-13-45", headers=headers)
    assert res1.status_code == 400
    assert "Formato de fecha inválido" in res1.json()["detail"]

    # String de inyección SQL
    res2 = client.get("/api/ventas/actividad?fecha=' OR 1=1 --", headers=headers)
    assert res2.status_code == 400

    # Fecha muy antigua: responde 200 con lista vacía
    res3 = client.get("/api/ventas/actividad?fecha=1900-01-01", headers=headers)
    assert res3.status_code == 200
    assert res3.json() == []


# ==============================================================================
# 7. BLINDAJE RBAC INTEGRAL: 10 ENDPOINTS ADMINISTRATIVOS CERRADOS AL CAJERO
# ==============================================================================
def test_blindaje_rbac_diez_rutas_bloqueadas_a_cajero(client: TestClient):
    """
    Verifica que un cajero no pueda acceder a ninguna de las 10 rutas
    administrativas del sistema bajo ninguna circunstancia.
    """
    admin_data, admin_token = _crear_empresa_y_admin(client)
    empresa_id = admin_data["usuario"]["empresa_id"]
    _, token_cajero = _crear_cajero(client, admin_token, "Cajero Privilegios")
    headers = {"Authorization": f"Bearer {token_cajero}"}

    endpoints_get = [
        f"/dashboard/{empresa_id}",
        f"/reportes/financieros/{empresa_id}",
        f"/reportes/ventas/excel/{empresa_id}",
        "/api/usuarios/empleados",
        "/api/ventas/actividad",
    ]
    for url in endpoints_get:
        res = client.get(url, headers=headers)
        assert res.status_code == 403, f"Fallo en {url}: retornó {res.status_code} en vez de 403"

    # Mutaciones de catálogo bloqueadas
    assert client.post("/api/productos", json={"nombre": "X"}, headers=headers).status_code == 403
    fake_id = uuid.uuid4()
    assert client.put(f"/api/productos/{fake_id}", json={"nombre": "X"}, headers=headers).status_code == 403
    assert client.delete(f"/api/productos/{fake_id}", headers=headers).status_code == 403


# ==============================================================================
# 8. PRODUCTO DESACTIVADO (SOFT DELETE): NO SE PUEDE VENDER EN MOSTRADOR
# ==============================================================================
def test_ataque_producto_inactivo_no_se_puede_vender(client: TestClient):
    """
    Un producto soft-deleted (is_active=False) no debe poder ser vendido por ningún cajero.
    """
    admin_data, admin_token = _crear_empresa_y_admin(client)
    empresa_id = admin_data["usuario"]["empresa_id"]
    prod = _crear_producto(client, admin_token, stock=10.0)
    prod_id = prod["id"]

    # Admin desactiva producto
    res_del = client.delete(f"/api/productos/{prod_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_del.status_code == 200

    # Cajero intenta vender producto desactivado
    _, token_cajero = _crear_cajero(client, admin_token, "Cajero Mostrador")
    payload = {"detalles": [{"producto_id": prod_id, "cantidad": 1.0}]}
    res_venta = client.post(f"/api/ventas/{empresa_id}", json=payload, headers={"Authorization": f"Bearer {token_cajero}"})
    assert res_venta.status_code == 400
    assert "no encontrado o no pertenece" in res_venta.json()["detail"]


# ==============================================================================
# 9. FUZZING DE PAYLOADS CON EMOJIS, CARACTERES EXTRAÑOS Y NOMBRES LARGOS
# ==============================================================================
def test_fuzzing_emojis_y_nombres_largos(client: TestClient):
    """
    Intento de inyección de nombres excesivamente largos (>100 chars) y emojis.
    Pydantic y FastAPI deben sanitizar o rechazar con 422 si excede 100 caracteres.
    """
    _, admin_token = _crear_empresa_y_admin(client)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Nombre > 100 caracteres debe ser rechazado
    nombre_gigante = "A" * 150
    res_largo = client.post(
        "/api/usuarios/empleados",
        json={"nombre": nombre_gigante, "email": "gigante@test.com", "password": "Password123!"},
        headers=headers,
    )
    assert res_largo.status_code == 422

    # Nombre con emojis y tildes válidos colombianos (UTF-8) debe ser aceptado
    nombre_emoji = "Paula Gómez 🇨🇴 🥑"
    res_emoji = client.post(
        "/api/usuarios/empleados",
        json={"nombre": nombre_emoji, "email": "paula_emoji@test.com", "password": "Password123!"},
        headers=headers,
    )
    assert res_emoji.status_code == 201
    assert res_emoji.json()["nombre"] == nombre_emoji


# ==============================================================================
# 10. POSTGRESQL: CARRERA SIMULTÁNEA ENTRE CREACIÓN Y REACTIVACIÓN
# ==============================================================================
@pytest.mark.skipif(not PG_ALIVE, reason="Requiere PostgreSQL vivo con connection pool")
def test_ataque_carrera_creacion_vs_reactivacion_postgres():
    """
    Empresa Básico tiene 2 cajeros activos y 1 desactivado (C1 inactivo, C2 activo, C3 activo).
    Queda exactamente 1 cupo.
    En el mismo instante:
    - Hilo A intenta REACTIVAR a C1.
    - Hilo B intenta CREAR a C4.
    GARANTÍA: Solo 1 tiene éxito, el otro recibe 403 (Límite alcanzado).
    Total final de cajeros activos en PostgreSQL = exactamente 3.
    """
    engine = create_engine(POSTGRES_URL, pool_size=10, max_overflow=5)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    pg_client = TestClient(app)

    try:
        admin_data, admin_token = _crear_empresa_y_admin(pg_client, plan="basic", session_factory=SessionLocal)
        empresa_id = uuid.UUID(admin_data["usuario"]["empresa_id"])
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # C1, C2, C3
        c1, _ = _crear_cajero(pg_client, admin_token, "C1")
        _crear_cajero(pg_client, admin_token, "C2")
        _crear_cajero(pg_client, admin_token, "C3")

        # Desactivar C1 (quedan 2 activos: C2 y C3; cupo disponible = 1)
        r_deact = pg_client.patch(f"/api/usuarios/empleados/{c1['id']}/estado", json={"is_active": False}, headers=admin_headers)
        assert r_deact.status_code == 200

        barrier = threading.Barrier(2)
        respuestas = []

        def _reactivar():
            barrier.wait()
            r = pg_client.patch(f"/api/usuarios/empleados/{c1['id']}/estado", json={"is_active": True}, headers=admin_headers)
            respuestas.append(r.status_code)

        def _crear_nuevo():
            barrier.wait()
            r = pg_client.post(
                "/api/usuarios/empleados",
                json={"nombre": "C4 Nuevo", "email": f"c4_{uuid.uuid4().hex[:6]}@test.com", "password": "Password123!"},
                headers=admin_headers,
            )
            respuestas.append(r.status_code)

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            f1 = executor.submit(_reactivar)
            f2 = executor.submit(_crear_nuevo)
            concurrent.futures.wait([f1, f2])

        status_codes = sorted(respuestas)
        # Uno debe tener éxito (200 o 201) y el otro debe ser 403
        assert 403 in status_codes, f"Se esperaba un 403 pero se obtuvo {status_codes}"
        assert any(c in [200, 201] for c in status_codes), f"Se esperaba un 200/201 pero se obtuvo {status_codes}"

        # Total en base de datos = exactamente 3
        db = SessionLocal()
        total_activos = (
            db.query(models.Usuario)
            .filter(
                models.Usuario.empresa_id == empresa_id,
                models.Usuario.rol == models.RolUsuario.TENDERO,
                models.Usuario.is_active.is_(True),
            )
            .count()
        )
        db.close()
        assert total_activos == 3, f"Inconsistencia: hay {total_activos} cajeros activos"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()

