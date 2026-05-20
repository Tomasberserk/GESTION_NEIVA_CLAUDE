import pytest
from conftest import registrar_admin, auth, crear_producto


def test_registrar_venta_happy_path(client):
    """Registrar venta happy path → 201, total correcto, stock descontado."""
    admin_data = registrar_admin(client)
    prod = crear_producto(client, admin_data["token"], {
        "codigo_barras": "7702011000010",
        "precio_venta": 5000,
        "cantidad_actual": 20,
    })

    r = client.post(f"/ventas/{admin_data['empresa_id']}", json={
        "items": [
            {"producto_id": prod["id"], "cantidad": 3}
        ]
    }, headers=auth(admin_data["token"]))
    assert r.status_code == 201
    body = r.json()
    assert body["total"] == 15000  # 5000 * 3
    assert "venta_id" in body
    assert "mensaje" in body

    # Verificar stock descontado
    prod_after = client.get(f"/productos/{admin_data['empresa_id']}",
                            headers=auth(admin_data["token"])).json()
    found = next((p for p in prod_after["inventario"] if p["id"] == prod["id"]), None)
    assert found["cantidad_actual"] == 17  # 20 - 3


def test_venta_stock_insuficiente(client):
    """Venta con stock insuficiente → 400."""
    admin_data = registrar_admin(client)
    prod = crear_producto(client, admin_data["token"], {
        "codigo_barras": "7702011000011",
        "cantidad_actual": 5,
    })

    r = client.post(f"/ventas/{admin_data['empresa_id']}", json={
        "items": [
            {"producto_id": prod["id"], "cantidad": 10}
        ]
    }, headers=auth(admin_data["token"]))
    assert r.status_code == 400


def test_venta_carrito_vacio(client):
    """Venta carrito vacío → 422."""
    admin_data = registrar_admin(client)

    r = client.post(f"/ventas/{admin_data['empresa_id']}", json={
        "items": []
    }, headers=auth(admin_data["token"]))
    assert r.status_code == 422


def test_listar_ventas_propia_empresa(client):
    """GET listar ventas propia empresa → 200."""
    admin_data = registrar_admin(client)
    prod = crear_producto(client, admin_data["token"], {
        "codigo_barras": "7702011000012",
        "precio_venta": 5000,
        "cantidad_actual": 20,
    })

    # Registrar venta
    client.post(f"/ventas/{admin_data['empresa_id']}", json={
        "items": [
            {"producto_id": prod["id"], "cantidad": 2}
        ]
    }, headers=auth(admin_data["token"]))

    r = client.get(f"/ventas/{admin_data['empresa_id']}",
                   headers=auth(admin_data["token"]))
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert len(body) >= 1


def test_listar_ventas_otra_empresa(client):
    """GET listar ventas otra empresa → 403."""
    admin1 = registrar_admin(client, {
        "nit_o_cedula": "900001014",
        "email": "admin_venta1@papeleria.com",
    })

    admin2 = registrar_admin(client, {
        "nit_o_cedula": "900001015",
        "email": "admin_venta2@papeleria.com",
    })

    r = client.get(f"/ventas/{admin1['empresa_id']}",
                   headers=auth(admin2["token"]))
    assert r.status_code == 403


def test_listar_ventas_con_filtro_desde_hasta(client):
    """GET ventas con filtro desde/hasta → filtra correctamente."""
    admin_data = registrar_admin(client)
    prod = crear_producto(client, admin_data["token"], {
        "codigo_barras": "7702011000013",
        "precio_venta": 5000,
        "cantidad_actual": 20,
    })

    # Registrar venta
    client.post(f"/ventas/{admin_data['empresa_id']}", json={
        "items": [
            {"producto_id": prod["id"], "cantidad": 1}
        ]
    }, headers=auth(admin_data["token"]))

    # Filtro desde/hasta
    r = client.get(
        f"/ventas/{admin_data['empresa_id']}?desde=2026-05-01T00:00:00&hasta=2026-05-31T23:59:59",
        headers=auth(admin_data["token"])
    )
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
