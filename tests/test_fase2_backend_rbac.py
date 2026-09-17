import uuid
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo
import pytest
from fastapi.testclient import TestClient

from app import models
from app.services import auth_service

try:
    COLOMBIA_TZ = ZoneInfo("America/Bogota")
except Exception:
    from datetime import timezone
    COLOMBIA_TZ = timezone(timedelta(hours=-5))


def _crear_empresa_y_admin(client: TestClient, email: str = "admin@test.com", plan: str = "basic") -> tuple[dict, str]:
    """Helper para registrar una empresa y su admin, retornando datos y token."""
    payload = {
        "nombre_comercial": f"Tienda {uuid.uuid4().hex[:6]}",
        "nit_o_cedula": f"NIT-{uuid.uuid4().hex[:8]}",
        "nombre": "Don Pedro",
        "email": email,
        "password": "Password123!",
        "rol": "admin",
    }
    res = client.post("/auth/registro-completo", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    token = data["access_token"]
    empresa_id = data["usuario"]["empresa_id"]

    # Si se especificó otro plan (ej: pro), se actualiza directamente en la BD
    if plan != "basic":
        from app.database import SessionLocal
        db = SessionLocal()
        emp = db.query(models.Empresa).filter(models.Empresa.id == uuid.UUID(empresa_id)).first()
        emp.plan = models.PlanEmpresa(plan)
        db.commit()
        db.close()

    return data, token


def test_jwt_inmediatamente_invalido_al_desactivar_usuario(client: TestClient):
    """
    P0.1: Si un cajero inicia sesión y luego es desactivado por el administrador,
    sus peticiones subsecuentes con el JWT previo deben ser rechazadas con 403.
    """
    _, admin_token = _crear_empresa_y_admin(client, "admin_jwt@test.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Admin crea cajera Paula
    cajero_payload = {
        "nombre": "Paula Cajera",
        "email": "paula_jwt@test.com",
        "password": "Password123!",
    }
    res_cajero = client.post("/api/usuarios/empleados", json=cajero_payload, headers=admin_headers)
    assert res_cajero.status_code == 201
    paula_id = res_cajero.json()["id"]

    # 2. Paula hace login y obtiene token
    res_login = client.post("/token", json={"email": "paula_jwt@test.com", "password": "Password123!"})
    assert res_login.status_code == 200
    paula_token = res_login.json()["access_token"]
    paula_headers = {"Authorization": f"Bearer {paula_token}"}

    # 3. Paula consulta /me con éxito
    res_me = client.get("/me", headers=paula_headers)
    assert res_me.status_code == 200
    assert res_me.json()["nombre"] == "Paula Cajera"

    # 4. Don Pedro desactiva a Paula
    res_deact = client.patch(f"/api/usuarios/empleados/{paula_id}/estado", json={"is_active": False}, headers=admin_headers)
    assert res_deact.status_code == 200
    assert res_deact.json()["is_active"] is False

    # 5. Paula intenta usar su token previo -> DEBE ser 403 Forbidden
    res_blocked = client.get("/me", headers=paula_headers)
    assert res_blocked.status_code == 403
    assert "Usuario desactivado" in res_blocked.json()["detail"]


def test_aislamiento_multi_tenant_anti_idor(client: TestClient):
    """
    P0.2: Un administrador de Empresa A no puede consultar ni modificar
    cajeros de Empresa B (debe retornar 404).
    """
    _, token_a = _crear_empresa_y_admin(client, "admin_tenant_a@test.com")
    _, token_b = _crear_empresa_y_admin(client, "admin_tenant_b@test.com")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Crear cajero en Empresa B
    cajero_b = client.post(
        "/api/usuarios/empleados",
        json={"nombre": "Carlos B", "email": "carlos_b@test.com", "password": "Password123!"},
        headers=headers_b,
    ).json()

    # Admin A intenta desactivar al cajero de Empresa B -> 404
    res_idor = client.patch(
        f"/api/usuarios/empleados/{cajero_b['id']}/estado",
        json={"is_active": False},
        headers=headers_a,
    )
    assert res_idor.status_code == 404
    assert res_idor.json()["detail"] == "Cajero no encontrado"

    # Admin A intenta consultar actividad filtrando por cajero de Empresa B -> 404
    res_act = client.get(
        f"/api/ventas/actividad?usuario_id={cajero_b['id']}",
        headers=headers_a,
    )
    assert res_act.status_code == 404
    assert "no encontrado" in res_act.json()["detail"]


def test_blindaje_rbac_cajero_bloqueado_de_admin_endpoints(client: TestClient):
    """
    Cajero con rol 'tendero' debe recibir 403 Forbidden en dashboard, reportes,
    gestión de empleados y mutaciones de catálogo.
    """
    data_admin, token_admin = _crear_empresa_y_admin(client, "admin_rbac@test.com")
    empresa_id = data_admin["usuario"]["empresa_id"]

    # Crear cajero
    client.post(
        "/api/usuarios/empleados",
        json={"nombre": "Cajero RBAC", "email": "cajero_rbac@test.com", "password": "Password123!"},
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    token_cajero = client.post(
        "/token", json={"email": "cajero_rbac@test.com", "password": "Password123!"}
    ).json()["access_token"]
    headers_cajero = {"Authorization": f"Bearer {token_cajero}"}

    # Endpoints que deben fallar con 403 para el cajero
    assert client.get(f"/dashboard/{empresa_id}", headers=headers_cajero).status_code == 403
    assert client.get(f"/reportes/financieros/{empresa_id}", headers=headers_cajero).status_code == 403
    assert client.get(f"/reportes/ventas/excel/{empresa_id}", headers=headers_cajero).status_code == 403
    assert client.get("/api/usuarios/empleados", headers=headers_cajero).status_code == 403
    assert client.get("/api/ventas/actividad", headers=headers_cajero).status_code == 403

    # Mutación de producto bloqueada
    nuevo_prod = {
        "nombre": "Arroz",
        "codigo_barras": "123456789",
        "precio_costo": 1000.0,
        "precio_venta": 1500.0,
        "cantidad_actual": 10.0,
        "unidad_medida": "libra",
    }
    assert client.post("/api/productos", json=nuevo_prod, headers=headers_cajero).status_code == 403


def test_catalogo_ciego_cajero_no_recibe_precios_de_costo(client: TestClient):
    """
    Al consultar GET /api/productos, el administrador recibe precio_costo,
    mientras que el cajero recibe la respuesta sin el campo precio_costo en absoluto.
    """
    _, token_admin = _crear_empresa_y_admin(client, "admin_ciego@test.com")
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    # 1. Admin crea producto con costo
    prod_data = {
        "nombre": "Aceite Vegetal 1L",
        "codigo_barras": "770999888111",
        "precio_costo": 6000.0,
        "precio_venta": 8500.0,
        "cantidad_actual": 25.0,
        "unidad_medida": "litro",
    }
    res_crear = client.post("/api/productos", json=prod_data, headers=headers_admin)
    assert res_crear.status_code == 201
    prod_id = res_crear.json()["id"]

    # 2. Admin crea cajero
    client.post(
        "/api/usuarios/empleados",
        json={"nombre": "Cajero Ciego", "email": "cajero_ciego@test.com", "password": "Password123!"},
        headers=headers_admin,
    )
    token_cajero = client.post(
        "/token", json={"email": "cajero_ciego@test.com", "password": "Password123!"}
    ).json()["access_token"]
    headers_cajero = {"Authorization": f"Bearer {token_cajero}"}

    # 3. Admin lista productos -> Contiene precio_costo
    res_admin_list = client.get("/api/productos", headers=headers_admin).json()
    item_admin = res_admin_list["inventario"][0]
    assert "precio_costo" in item_admin
    assert item_admin["precio_costo"] == 6000.0

    # 4. Cajero lista productos -> CERO precio_costo
    res_cajero_list = client.get("/api/productos", headers=headers_cajero).json()
    item_cajero = res_cajero_list["inventario"][0]
    assert "precio_costo" not in item_cajero, "Fuga de datos: el cajero jamás debe recibir precio_costo"
    assert item_cajero["precio_venta"] == 8500.0

    # 5. Obtener por ID
    res_admin_id = client.get(f"/api/productos/{prod_id}", headers=headers_admin).json()
    assert "precio_costo" in res_admin_id

    res_cajero_id = client.get(f"/api/productos/{prod_id}", headers=headers_cajero).json()
    assert "precio_costo" not in res_cajero_id


def test_trazabilidad_venta_registra_usuario_y_snapshot(client: TestClient):
    """
    Al registrar una venta en el mostrador, se debe asociar usuario_id
    y vendedor_nombre_snapshot inmutable en la BD.
    """
    data_admin, token_admin = _crear_empresa_y_admin(client, "admin_venta@test.com")
    empresa_id = data_admin["usuario"]["empresa_id"]
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    # Producto
    prod = client.post(
        "/api/productos",
        json={
            "nombre": "Gaseosa 350ml",
            "codigo_barras": "770111222333",
            "precio_costo": 1500.0,
            "precio_venta": 2500.0,
            "cantidad_actual": 50.0,
            "unidad_medida": "unidad",
        },
        headers=headers_admin,
    ).json()

    # Cajero Paula
    client.post(
        "/api/usuarios/empleados",
        json={"nombre": "Paula Vendedora", "email": "paula_vendedora@test.com", "password": "Password123!"},
        headers=headers_admin,
    )
    token_paula = client.post(
        "/token", json={"email": "paula_vendedora@test.com", "password": "Password123!"}
    ).json()["access_token"]
    headers_paula = {"Authorization": f"Bearer {token_paula}"}

    # Paula registra venta
    venta_payload = {
        "detalles": [{"producto_id": prod["id"], "cantidad": 2.0}]
    }
    res_venta = client.post(f"/api/ventas/{empresa_id}", json=venta_payload, headers=headers_paula)
    assert res_venta.status_code == 201
    venta_id = res_venta.json()["venta_id"]

    # Verificar en BD
    from app.database import SessionLocal
    db = SessionLocal()
    venta_db = db.query(models.Venta).filter(models.Venta.id == uuid.UUID(venta_id)).first()
    assert venta_db is not None
    assert str(venta_db.usuario_id) == client.get("/me", headers=headers_paula).json()["id"]
    assert venta_db.vendedor_nombre_snapshot == "Paula Vendedora"
    db.close()


def test_limite_3_cajeros_en_plan_basico_y_reactivacion(client: TestClient):
    """
    En Plan Básico:
    - Se pueden crear hasta 3 cajeros.
    - El 4º es rechazado con 403.
    - Si se desactiva 1 cajero, se libera cupo y se puede crear otro.
    - Si se intenta reactivar cuando ya hay 3 activos, es rechazado con 403.
    """
    _, token_admin = _crear_empresa_y_admin(client, "admin_limite@test.com", plan="basic")
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    # Crear 3 cajeros exitosamente
    c1 = client.post("/api/usuarios/empleados", json={"nombre": "Cajero 1", "email": "c1@test.com", "password": "Password123!"}, headers=headers_admin).json()
    c2 = client.post("/api/usuarios/empleados", json={"nombre": "Cajero 2", "email": "c2@test.com", "password": "Password123!"}, headers=headers_admin).json()
    c3 = client.post("/api/usuarios/empleados", json={"nombre": "Cajero 3", "email": "c3@test.com", "password": "Password123!"}, headers=headers_admin).json()

    # Intentar crear el 4to cajero -> 403
    res_c4 = client.post(
        "/api/usuarios/empleados",
        json={"nombre": "Cajero 4", "email": "c4@test.com", "password": "Password123!"},
        headers=headers_admin,
    )
    assert res_c4.status_code == 403
    assert "límite de 3 cajeros" in res_c4.json()["detail"]

    # Desactivar Cajero 1 -> libera cupo
    res_deact = client.patch(f"/api/usuarios/empleados/{c1['id']}/estado", json={"is_active": False}, headers=headers_admin)
    assert res_deact.status_code == 200
    assert res_deact.json()["is_active"] is False

    # Ahora crear Cajero 4 sí debe permitirse
    res_c4_ok = client.post(
        "/api/usuarios/empleados",
        json={"nombre": "Cajero 4", "email": "c4@test.com", "password": "Password123!"},
        headers=headers_admin,
    )
    assert res_c4_ok.status_code == 201

    # Intentar reactivar Cajero 1 (habiendo ya 3 activos: C2, C3, C4) -> DEBE fallar con 403
    res_react_fail = client.patch(
        f"/api/usuarios/empleados/{c1['id']}/estado",
        json={"is_active": True},
        headers=headers_admin,
    )
    assert res_react_fail.status_code == 403
    assert "límite de 3 cajeros" in res_react_fail.json()["detail"]


def test_actividad_del_dia_timezone_colombia(client: TestClient):
    """
    Verifica que Actividad del Día filtre por intervalo semiabierto [00:00, 24:00)
    en America/Bogota. Una venta a las 23:59:00 entra; 00:00:01 del día siguiente se excluye.
    """
    data_admin, token_admin = _crear_empresa_y_admin(client, "admin_tz@test.com")
    empresa_id = uuid.UUID(data_admin["usuario"]["empresa_id"])
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    # Fecha fijada: 2026-09-17
    target_date = date(2026, 9, 17)
    dt_adentro = datetime.combine(target_date, time(23, 59, 0), tzinfo=COLOMBIA_TZ)
    dt_afuera  = datetime.combine(target_date + timedelta(days=1), time(0, 0, 1), tzinfo=COLOMBIA_TZ)

    # Insertar directamente en BD para controlar timestamps exactos
    from app.database import SessionLocal
    db = SessionLocal()
    v1 = models.Venta(empresa_id=empresa_id, total=Decimal("15000.00"), fecha_venta=dt_adentro, is_active=True, vendedor_nombre_snapshot="Venta Adentro")
    v2 = models.Venta(empresa_id=empresa_id, total=Decimal("30000.00"), fecha_venta=dt_afuera, is_active=True, vendedor_nombre_snapshot="Venta Afuera")
    db.add_all([v1, v2])
    db.commit()
    db.close()

    # Consultar actividad para la fecha target
    res_act = client.get("/api/ventas/actividad?fecha=2026-09-17", headers=headers_admin)
    assert res_act.status_code == 200
    ventas = res_act.json()

    snapshots = [v["vendedor_nombre_snapshot"] for v in ventas]
    assert "Venta Adentro" in snapshots
    assert "Venta Afuera" not in snapshots, "La venta del día siguiente a las 00:00:01 no debe incluirse"


def test_concurrencia_creacion_cajeros_limite_tres_con_barrier():
    """
    Test de Concurrencia Real en PostgreSQL:
    Teniendo 2 cajeros activos en Plan Básico, dos peticiones simultáneas
    sincronizadas con Barrier(2) intentan crear un cajero adicional al mismo tiempo.
    El bloqueo pesimista SELECT FOR UPDATE sobre la empresa en PostgreSQL
    garantiza que:
    - Una petición tenga éxito (HTTP 201).
    - La otra sea serializada por el kernel de PostgreSQL, lea COUNT=3 y sea rechazada (HTTP 403).
    - El total final de cajeros en la BD sea estrictamente 3, jamás 4.
    """
    import concurrent.futures
    import threading
    import os
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database import get_db
    from app.main import app

    pg_url = (
        os.getenv("TEST_POSTGRES_URL")
        or os.getenv("POSTGRES_URL")
        or "postgresql://postgres:postgres@localhost:5432/gestion_neiva_test"
    )
    try:
        import psycopg2
        conn = psycopg2.connect(pg_url, connect_timeout=2)
        conn.close()
    except Exception:
        pytest.skip("Requiere PostgreSQL vivo con connection pool para verificar SELECT FOR UPDATE real")

    engine = create_engine(pg_url, pool_size=10, max_overflow=5)
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
        data_admin, token_admin = _crear_empresa_y_admin(pg_client, f"admin_conc_{uuid.uuid4().hex[:6]}@test.com", plan="basic")
        empresa_id = uuid.UUID(data_admin["usuario"]["empresa_id"])
        headers_admin = {"Authorization": f"Bearer {token_admin}"}

        # 1. Crear los 2 primeros cajeros (quedan 2 activos)
        c1 = pg_client.post("/api/usuarios/empleados", json={"nombre": "Cajero Inicial 1", "email": f"c_init1_{uuid.uuid4().hex[:6]}@test.com", "password": "Password123!"}, headers=headers_admin)
        c2 = pg_client.post("/api/usuarios/empleados", json={"nombre": "Cajero Inicial 2", "email": f"c_init2_{uuid.uuid4().hex[:6]}@test.com", "password": "Password123!"}, headers=headers_admin)
        assert c1.status_code == 201
        assert c2.status_code == 201

        barrier = threading.Barrier(2)
        respuestas = []

        def _crear_cajero_concurrente(idx: int):
            barrier.wait()  # Sincronización precisa en el mismo instante
            payload = {
                "nombre": f"Cajero Concurrente {idx}",
                "email": f"c_conc_{idx}_{uuid.uuid4().hex[:6]}@test.com",
                "password": "Password123!",
            }
            r = pg_client.post("/api/usuarios/empleados", json=payload, headers=headers_admin)
            respuestas.append(r)

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            f1 = executor.submit(_crear_cajero_concurrente, 1)
            f2 = executor.submit(_crear_cajero_concurrente, 2)
            concurrent.futures.wait([f1, f2])

        status_codes = sorted([r.status_code for r in respuestas])
        # Exactamente una petición debe ser 201 y la otra 403
        assert status_codes == [201, 403], f"Se esperaba [201, 403] pero se obtuvo {status_codes}"

        # Verificación en PostgreSQL: exactamente 3 cajeros activos
        db = SessionLocal()
        total_cajeros = (
            db.query(models.Usuario)
            .filter(
                models.Usuario.empresa_id == empresa_id,
                models.Usuario.rol == models.RolUsuario.TENDERO,
                models.Usuario.is_active.is_(True),
            )
            .count()
        )
        assert total_cajeros == 3, f"Inconsistencia de concurrencia: se crearon {total_cajeros} cajeros en vez de 3"
        db.close()
    finally:
        app.dependency_overrides.clear()
        engine.dispose()

