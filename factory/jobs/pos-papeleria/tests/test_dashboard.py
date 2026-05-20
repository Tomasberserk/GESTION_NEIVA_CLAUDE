import pytest
from conftest import registrar_admin, auth, crear_producto


def test_dashboard_propia_empresa(client):
    """Dashboard propia empresa → 200, campos: ventas_hoy, ingresos_hoy, total_productos_activos, stock_bajo."""
    admin_data = registrar_admin(client)
    crear_producto(client, admin_data["token"], {
        "codigo_barras": "7702011000020",
    })

    r = client.get(f"/dashboard/{admin_data['empresa_id']}",
                   headers=auth(admin_data["token"]))
    assert r.status_code == 200
    body = r.json()
    assert "ventas_hoy" in body
    assert "ingresos_hoy" in body
    assert "total_productos_activos" in body
    assert "stock_bajo" in body
    assert isinstance(body["stock_bajo"], list)


def test_dashboard_otra_empresa(client):
    """Dashboard otra empresa → 403."""
    admin1 = registrar_admin(client, {
        "nit_o_cedula": "900001016",
        "email": "admin_dash1@papeleria.com",
    })

    admin2 = registrar_admin(client, {
        "nit_o_cedula": "900001017",
        "email": "admin_dash2@papeleria.com",
    })

    r = client.get(f"/dashboard/{admin1['empresa_id']}",
                   headers=auth(admin2["token"]))
    assert r.status_code == 403


def test_stock_bajo_dinamico(client):
    """stock_bajo solo incluye productos donde cantidad_actual <= stock_minimo (dinámico)."""
    admin_data = registrar_admin(client)

    # Producto con stock bajo
    prod_bajo = crear_producto(client, admin_data["token"], {
        "codigo_barras": "7702011000021",
        "cantidad_actual": 3,
        "stock_minimo": 5,
    })

    # Producto con stock normal
    prod_normal = crear_producto(client, admin_data["token"], {
        "nombre": "Bolígrafo",
        "codigo_barras": "7702011000022",
        "cantidad_actual": 50,
        "stock_minimo": 5,
    })

    r = client.get(f"/dashboard/{admin_data['empresa_id']}",
                   headers=auth(admin_data["token"]))
    assert r.status_code == 200
    body = r.json()
    stock_bajo_ids = [p["id"] for p in body["stock_bajo"]]

    assert prod_bajo["id"] in stock_bajo_ids
    assert prod_normal["id"] not in stock_bajo_ids


def test_producto_stock_igual_minimo_en_bajo(client):
    """Producto con stock == stock_minimo aparece en stock_bajo."""
    admin_data = registrar_admin(client)

    prod = crear_producto(client, admin_data["token"], {
        "codigo_barras": "7702011000023",
        "cantidad_actual": 5,
        "stock_minimo": 5,
    })

    r = client.get(f"/dashboard/{admin_data['empresa_id']}",
                   headers=auth(admin_data["token"]))
    assert r.status_code == 200
    body = r.json()
    stock_bajo_ids = [p["id"] for p in body["stock_bajo"]]

    assert prod["id"] in stock_bajo_ids


def test_dashboard_actualiza_ventas_y_ingresos(client):
    """Después de venta, ventas_hoy e ingresos_hoy se actualizan."""
    admin_data = registrar_admin(client)
    prod = crear_producto(client, admin_data["token"], {
        "codigo_barras": "7702011000024",
        "precio_venta": 10000,
        "cantidad_actual": 20,
    })

    # Dashboard antes
    r_before = client.get(f"/dashboard/{admin_data['empresa_id']}",
                         headers=auth(admin_data["token"]))
    dash_before = r_before.json()
    ventas_antes = dash_before["ventas_hoy"]
    ingresos_antes = dash_before["ingresos_hoy"]

    # Realizar venta
    client.post(f"/ventas/{admin_data['empresa_id']}", json={
        "items": [
            {"producto_id": prod["id"], "cantidad": 2}
        ]
    }, headers=auth(admin_data["token"]))

    # Dashboard después
    r_after = client.get(f"/dashboard/{admin_data['empresa_id']}",
                        headers=auth(admin_data["token"]))
    dash_after = r_after.json()

    assert dash_after["ventas_hoy"] == ventas_antes + 1
    assert dash_after["ingresos_hoy"] == ingresos_antes + 20000
