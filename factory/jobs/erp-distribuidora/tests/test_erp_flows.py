import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

# Auxiliares para cabeceras con JWT
def get_auth_headers(client, email="admin@distrimayorista.com", nit="860123456-7"):
    res = client.post(
        "/auth/registro-completo",
        json={
            "nombre_comercial": "Distribuidora Mayorista Test",
            "nit_o_cedula": nit,
            "email": email,
            "password": "SecurePass123!",
            "rol": "admin"
        }
    )
    assert res.status_code == 201
    data = res.json()
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_flujo_completo_registro_y_auth(client):
    """Prueba el registro y posterior login exitoso"""
    # 1. Registro
    res = client.post(
        "/auth/registro-completo",
        json={
            "nombre_comercial": "Distribuidora S.A.S.",
            "nit_o_cedula": "123456789-0",
            "email": "juan@distribuidora.com",
            "password": "PasswordSecreta123!",
            "rol": "admin"
        }
    )
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["usuario"]["email"] == "juan@distribuidora.com"
    assert data["usuario"]["rol"] == "admin"

    # 2. Login
    res_login = client.post(
        "/token",
        json={
            "email": "juan@distribuidora.com",
            "password": "PasswordSecreta123!"
        }
    )
    assert res_login.status_code == 200
    assert "access_token" in res_login.json()

    # 3. /me
    headers = {"Authorization": f"Bearer {res_login.json()['access_token']}"}
    res_me = client.get("/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["email"] == "juan@distribuidora.com"


def test_crud_productos(client):
    """Prueba la gestión de catálogo de productos con multi-tenant"""
    headers = get_auth_headers(client, "admin_prod@test.com", "nit_prod")

    # 1. Crear
    res_crear = client.post(
        "/api/productos",
        json={
            "nombre": "Cuaderno 100 Hojas",
            "codigo_barras": "7701234567890",
            "precio_costo": 2500.00,
            "precio_venta": 4500.00,
            "cantidad_actual": 10.000,
            "unidad_medida": "UNIDAD",
            "categoria": "Papelería"
        },
        headers=headers
    )
    assert res_crear.status_code == 201
    prod = res_crear.json()
    assert prod["nombre"] == "Cuaderno 100 Hojas"
    assert float(prod["cantidad_actual"]) == 10.000

    # 2. Crear duplicado de código de barras -> debe fallar con 409
    res_dup = client.post(
        "/api/productos",
        json={
            "nombre": "Otro Cuaderno",
            "codigo_barras": "7701234567890",
            "precio_costo": 2000.00,
            "precio_venta": 4000.00,
            "cantidad_actual": 0,
            "unidad_medida": "UNIDAD"
        },
        headers=headers
    )
    assert res_dup.status_code == 409

    # 3. Listar
    res_listar = client.get("/api/productos", headers=headers)
    assert res_listar.status_code == 200
    assert len(res_listar.json()) == 1

    # 4. Actualizar
    prod_id = prod["id"]
    res_act = client.put(
        f"/api/productos/{prod_id}",
        json={"precio_venta": 4800.00, "nombre": "Cuaderno Norma 100 Hojas"},
        headers=headers
    )
    assert res_act.status_code == 200
    assert res_act.json()["nombre"] == "Cuaderno Norma 100 Hojas"
    assert float(res_act.json()["precio_venta"]) == 4800.00

    # 5. Borrar
    res_del = client.delete(f"/api/productos/{prod_id}", headers=headers)
    assert res_del.status_code == 200
    # Comprobar que ya no aparece en lista
    res_listar_post = client.get("/api/productos", headers=headers)
    assert len(res_listar_post.json()) == 0


def test_crud_proveedores(client):
    """Prueba el registro y eliminación de proveedores"""
    headers = get_auth_headers(client, "admin_prov@test.com", "nit_prov_empresa")

    # 1. Crear proveedor
    res_crear = client.post(
        "/api/proveedores",
        json={
            "nit_o_cedula": "900987654-3",
            "razon_social": "Distribuciones de la Sabana",
            "contacto_nombre": "Carlos Gómez",
            "telefono": "3115551234",
            "email": "sabana@distri.com",
            "direccion": "Zona Industrial"
        },
        headers=headers
    )
    assert res_crear.status_code == 201
    prov = res_crear.json()
    assert prov["razon_social"] == "Distribuciones de la Sabana"

    # 2. NIT duplicado para la misma empresa -> debe fallar con 409
    res_dup = client.post(
        "/api/proveedores",
        json={
            "nit_o_cedula": "900987654-3",
            "razon_social": "Compañía Duplicada"
        },
        headers=headers
    )
    assert res_dup.status_code == 409

    # 3. Listar paginado
    res_listar = client.get("/api/proveedores", headers=headers)
    assert res_listar.status_code == 200
    data = res_listar.json()
    assert data["total"] == 1
    assert data["items"][0]["nit_o_cedula"] == "900987654-3"

    # 4. Actualizar
    prov_id = prov["id"]
    res_act = client.put(
        f"/api/proveedores/{prov_id}",
        json={"contacto_nombre": "Carlos Gómez R."},
        headers=headers
    )
    assert res_act.status_code == 200
    assert res_act.json()["contacto_nombre"] == "Carlos Gómez R."


def test_flujo_compras_efectivo_vs_credito(client):
    """Registra una compra en efectivo (sin CxP) y otra a crédito (con CxP)"""
    headers = get_auth_headers(client, "admin_comp@test.com", "nit_comp_empresa")

    # Crear producto y proveedor
    p_res = client.post(
        "/api/productos",
        json={"nombre": "Resma Papel Bond", "codigo_barras": "111", "precio_costo": 8000.00, "precio_venta": 12000.00, "cantidad_actual": 5.0, "unidad_medida": "UNIDAD"},
        headers=headers
    )
    prod_id = p_res.json()["id"]

    prov_res = client.post(
        "/api/proveedores",
        json={"nit_o_cedula": "112233", "razon_social": "Papeles del Huila"},
        headers=headers
    )
    prov_id = prov_res.json()["id"]

    # 1. Compra en EFECTIVO -> incrementa stock, estado PAGADA, sin cuenta por pagar
    res_efectivo = client.post(
        "/api/compras",
        json={
            "proveedor_id": prov_id,
            "numero_factura": "EF-001",
            "metodo_pago": "EFECTIVO",
            "items": [{"producto_id": prod_id, "cantidad": 10.0, "precio_costo": 8500.00}]
        },
        headers=headers
    )
    assert res_efectivo.status_code == 201
    compra_ef = res_efectivo.json()
    assert compra_ef["estado"] == "PAGADA"
    assert compra_ef["cuenta_por_pagar_id"] is None
    assert float(compra_ef["total"]) == 85000.00

    # Validar stock incrementado (5 + 10 = 15) y costo actualizado a 8500
    res_p1 = client.get(f"/api/productos/{prod_id}", headers=headers)
    assert float(res_p1.json()["cantidad_actual"]) == 15.0
    assert float(res_p1.json()["precio_costo"]) == 8500.00

    # 2. Compra a CRÉDITO -> requiere fecha_vencimiento
    res_err_credito = client.post(
        "/api/compras",
        json={
            "proveedor_id": prov_id,
            "numero_factura": "CR-001",
            "metodo_pago": "CREDITO",
            "items": [{"producto_id": prod_id, "cantidad": 5.0, "precio_costo": 9000.00}]
        },
        headers=headers
    )
    assert res_err_credito.status_code == 400  # Falta fecha de vencimiento

    vence = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    res_credito = client.post(
        "/api/compras",
        json={
            "proveedor_id": prov_id,
            "numero_factura": "CR-001",
            "metodo_pago": "CREDITO",
            "fecha_vencimiento": vence,
            "items": [{"producto_id": prod_id, "cantidad": 5.0, "precio_costo": 9000.00}]
        },
        headers=headers
    )
    assert res_credito.status_code == 201
    compra_cr = res_credito.json()
    assert compra_cr["estado"] == "PENDIENTE"
    assert compra_cr["cuenta_por_pagar_id"] is not None

    # Validar stock incrementado (15 + 5 = 20) y costo actualizado a 9000
    res_p2 = client.get(f"/api/productos/{prod_id}", headers=headers)
    assert float(res_p2.json()["cantidad_actual"]) == 20.0
    assert float(res_p2.json()["precio_costo"]) == 9000.00


def test_cuentas_por_pagar_y_abonos(client):
    """Flujo de deudas: compra a crédito -> consultar deuda -> abonos -> saldar deuda -> anular abono"""
    headers = get_auth_headers(client, "admin_fin@test.com", "nit_fin_empresa")

    # Crear catálogo
    p_res = client.post(
        "/api/productos",
        json={"nombre": "Marcador Borrable", "codigo_barras": "222", "precio_costo": 3000.00, "precio_venta": 5000.00, "cantidad_actual": 0.0, "unidad_medida": "UNIDAD"},
        headers=headers
    )
    prod_id = p_res.json()["id"]

    prov_res = client.post(
        "/api/proveedores",
        json={"nit_o_cedula": "223344", "razon_social": "Marcadores Pelikan"},
        headers=headers
    )
    prov_id = prov_res.json()["id"]

    # Compra a crédito de 100 unidades a 3000 = $300.000
    vence = (datetime.now(timezone.utc) + timedelta(days=15)).isoformat()
    c_res = client.post(
        "/api/compras",
        json={
            "proveedor_id": prov_id,
            "numero_factura": "FAC-DEUDA",
            "metodo_pago": "CREDITO",
            "fecha_vencimiento": vence,
            "items": [{"producto_id": prod_id, "cantidad": 100.0, "precio_costo": 3000.0}]
        },
        headers=headers
    )
    compra = c_res.json()
    cxp_id = compra["cuenta_por_pagar_id"]

    # 1. Consultar deudas activas
    res_cxps = client.get("/api/cuentas-por-pagar", headers=headers)
    assert res_cxps.status_code == 200
    data = res_cxps.json()
    assert data["total"] == 1
    cxp = data["items"][0]
    assert float(cxp["monto_total"]) == 300000.00
    assert float(cxp["saldo_pendiente"]) == 300000.00
    assert cxp["estado"] == "PENDIENTE"

    # 2. Registrar Abono Parcial de $100.000 -> saldo pendiente $200.000
    res_abono1 = client.post(
        f"/api/cuentas-por-pagar/{cxp_id}/abonos",
        json={"monto": 100000.00, "metodo_pago": "TRANSFERENCIA", "nota": "Abono inicial"},
        headers=headers
    )
    assert res_abono1.status_code == 201
    ab_data = res_abono1.json()
    assert float(ab_data["nuevo_saldo_pendiente"]) == 200000.00
    assert ab_data["estado_obligacion"] == "PENDIENTE"
    abono1_id = ab_data["id"]

    # 3. Registrar abono excesivo -> debe fallar con 400
    res_err_abono = client.post(
        f"/api/cuentas-por-pagar/{cxp_id}/abonos",
        json={"monto": 250000.00, "metodo_pago": "EFECTIVO"},
        headers=headers
    )
    assert res_err_abono.status_code == 400

    # 4. Consultar listado de abonos
    res_list_ab = client.get(f"/api/cuentas-por-pagar/{cxp_id}/abonos", headers=headers)
    assert len(res_list_ab.json()["abonos"]) == 1
    assert float(res_list_ab.json()["abonos"][0]["monto"]) == 100000.00

    # 5. Registrar abono final de $200.000 -> debe saldar la deuda ($0 saldo pendiente, estado PAGADA)
    res_abono2 = client.post(
        f"/api/cuentas-por-pagar/{cxp_id}/abonos",
        json={"monto": 200000.00, "metodo_pago": "EFECTIVO", "nota": "Saldado completo"},
        headers=headers
    )
    assert res_abono2.status_code == 201
    assert float(res_abono2.json()["nuevo_saldo_pendiente"]) == 0.00
    assert res_abono2.json()["estado_obligacion"] == "PAGADA"

    # Verificar que el estado de la compra también pasó a PAGADA
    res_comp_verif = client.get(f"/api/compras/{compra['id']}", headers=headers)
    assert res_comp_verif.json()["estado"] == "PAGADA"

    # 6. Reversar el abono de $100.000 -> saldo pendiente sube a $100.000, estado vuelve a PENDIENTE
    res_rev = client.delete(f"/api/cuentas-por-pagar/abonos/{abono1_id}", headers=headers)
    assert res_rev.status_code == 200
    rev_data = res_rev.json()
    assert float(rev_data["nuevo_saldo_pendiente"]) == 100000.00
    assert rev_data["estado_obligacion"] == "PENDIENTE"

    # Verificar que la compra también degradó su estado a PENDIENTE
    res_comp_verif2 = client.get(f"/api/compras/{compra['id']}", headers=headers)
    assert res_comp_verif2.json()["estado"] == "PENDIENTE"


def test_anulacion_compra_y_reversion_stock(client):
    """Anulación de compra: reversa stock. Si stock no alcanza (mercancía ya vendida), rechaza anulación."""
    headers = get_auth_headers(client, "admin_anul@test.com", "nit_anul_empresa")

    # Registrar
    p_res = client.post(
        "/api/productos",
        json={"nombre": "Folder Plástico", "codigo_barras": "333", "precio_costo": 1000.00, "precio_venta": 2000.00, "cantidad_actual": 0.0, "unidad_medida": "UNIDAD"},
        headers=headers
    )
    prod_id = p_res.json()["id"]

    prov_res = client.post(
        "/api/proveedores",
        json={"nit_o_cedula": "334455", "razon_social": "Carpetas del Sur"},
        headers=headers
    )
    prov_id = prov_res.json()["id"]

    # Compra de 50 unidades -> stock sube a 50
    c_res = client.post(
        "/api/compras",
        json={
            "proveedor_id": prov_id,
            "numero_factura": "FAC-STOCK",
            "metodo_pago": "EFECTIVO",
            "items": [{"producto_id": prod_id, "cantidad": 50.0, "precio_costo": 1000.0}]
        },
        headers=headers
    )
    compra_id = c_res.json()["id"]

    # 1. Intentar anular cuando el stock es suficiente -> debe funcionar
    # Pero para probar el rechazo, primero vendamos/disminuyamos el stock
    # Vamos a simular que vendimos bajando el stock a 20 directamente
    client.put(f"/api/productos/{prod_id}", json={"cantidad_actual": 20.0}, headers=headers)

    # Ahora intentamos anular la compra de 50 -> debe fallar porque solo quedan 20 en stock
    res_fail = client.delete(f"/api/compras/{compra_id}", headers=headers)
    assert res_fail.status_code == 400
    assert "stock actual" in res_fail.json()["detail"]

    # Restauramos el stock a 50 -> ahora sí debe permitir anular
    client.put(f"/api/productos/{prod_id}", json={"cantidad_actual": 50.0}, headers=headers)
    res_success = client.delete(f"/api/compras/{compra_id}", headers=headers)
    assert res_success.status_code == 200
    assert res_success.json()["ok"] is True
    assert res_success.json()["stock_reversado"][str(prod_id)] == -50.0

    # Comprobar que el stock del producto volvió a 0
    p_verif = client.get(f"/api/productos/{prod_id}", headers=headers)
    assert float(p_verif.json()["cantidad_actual"]) == 0.0


def test_restricciones_rol_asistente(client):
    """Un usuario con rol 'asistente' no puede ver ni modificar Cuentas por Pagar ni dashboard KPIs"""
    # 1. Registrar empresa y obtener token de admin para crear asistente
    admin_headers = get_auth_headers(client, "admin_rol@test.com", "nit_rol")
    
    # Crear un usuario asistente en la misma empresa
    # Para hacerlo simple, obtenemos la empresa_id del admin
    me_res = client.get("/me", headers=admin_headers)
    empresa_id = me_res.json()["empresa_id"]

    # Simulamos el login directo de un asistente registrándolo en otra llamada o directamente
    # Registraremos otro usuario y forzamos rol asistente por BD
    # Nota: la creación de un usuario normal no tiene endpoint público excepto por registro-completo
    # Pero podemos registrar una cuenta y luego modificar su rol a 'asistente' usando admin
    # En erp-distribuidora, no hay endpoint público para cambiar roles, pero podemos crear el asistente
    # registrando una nueva empresa e ingresando rol = "asistente" en registro-completo!
    # El modelo y schema soportan 'rol = asistente' en UsuarioCrearConEmpresa.
    
    res_asist = client.post(
        "/auth/registro-completo",
        json={
            "nombre_comercial": "Distribuidora Asistente",
            "nit_o_cedula": "nit_asistente_test",
            "email": "asistente@distri.com",
            "password": "SecurePass123!",
            "rol": "asistente"
        }
    )
    assert res_asist.status_code == 201

    # Forzar el rol a 'asistente' en la base de datos de prueba
    from app.database import SessionLocal
    from app import models
    db = SessionLocal()
    try:
        user = db.query(models.Usuario).filter(models.Usuario.email == "asistente@distri.com").first()
        if user:
            user.rol = "asistente"
            db.commit()
    finally:
        db.close()

    asist_token = res_asist.json()["access_token"]
    asist_headers = {"Authorization": f"Bearer {asist_token}"}

    # Probar accesos del asistente -> debe responder 403 Forbidden a cuentas por pagar y dashboard
    res_cxp = client.get("/api/cuentas-por-pagar", headers=asist_headers)
    assert res_cxp.status_code == 403

    res_dash = client.get("/api/dashboard/kpis", headers=asist_headers)
    assert res_dash.status_code == 403

    # Pero sí debe poder registrar productos
    res_prod = client.post(
        "/api/productos",
        json={"nombre": "Lápiz", "codigo_barras": "lapiz-1", "precio_costo": 500, "precio_venta": 800, "cantidad_actual": 10},
        headers=asist_headers
    )
    assert res_prod.status_code == 201


def test_dashboard_kpis(client):
    """Valida los cálculos del dashboard financiero"""
    headers = get_auth_headers(client, "admin_dash@test.com", "nit_dash_empresa")

    # Crear catálogo
    p_res = client.post(
        "/api/productos",
        json={"nombre": "Papel Bond Resma", "codigo_barras": "resma-1", "precio_costo": 10000.0, "precio_venta": 15000.0, "cantidad_actual": 0.0},
        headers=headers
    )
    prod_id = p_res.json()["id"]

    prov_res = client.post(
        "/api/proveedores",
        json={"nit_o_cedula": "999", "razon_social": "Papeles S.A."},
        headers=headers
    )
    prov_id = prov_res.json()["id"]

    # 1. Compra a crédito de 10 resmas a 10.000 = $100.000
    vence = (datetime.now(timezone.utc) + timedelta(days=20)).isoformat()
    client.post(
        "/api/compras",
        json={
            "proveedor_id": prov_id,
            "numero_factura": "FAC-DASH-1",
            "metodo_pago": "CREDITO",
            "fecha_vencimiento": vence,
            "items": [{"producto_id": prod_id, "cantidad": 10.0, "precio_costo": 10000.0}]
        },
        headers=headers
    )

    # 2. Compra en efectivo de 5 resmas a 10.000 = $50.000
    client.post(
        "/api/compras",
        json={
            "proveedor_id": prov_id,
            "numero_factura": "FAC-DASH-2",
            "metodo_pago": "EFECTIVO",
            "items": [{"producto_id": prod_id, "cantidad": 5.0, "precio_costo": 10000.0}]
        },
        headers=headers
    )

    # En este punto:
    # Compras totales = 150.000
    # Deudas activas = 100.000
    # Valor total stock = 15 resmas * 10.000 = 150.000
    # Proveedores activos = 1
    # Con deuda activa = 1

    res_kpis = client.get("/api/dashboard/kpis", headers=headers)
    assert res_kpis.status_code == 200
    kpis = res_kpis.json()

    assert float(kpis["resumen_financiero"]["compras_totales"]) == 150000.00
    assert float(kpis["resumen_financiero"]["deudas_activas"]) == 100000.00
    assert float(kpis["resumen_financiero"]["deudas_vencidas"]) == 0.00
    assert kpis["inventario"]["total_items"] == 1
    assert float(kpis["inventario"]["valor_total_stock"]) == 150000.00
    assert kpis["proveedores"]["total_activos"] == 1
    assert kpis["proveedores"]["con_deuda_activa"] == 1
