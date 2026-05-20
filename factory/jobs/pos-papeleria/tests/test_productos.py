from conftest import registrar_admin, registrar_tendero, auth, crear_producto


def test_admin_puede_crear_producto(client):
    admin_data = registrar_admin(client)

    payload = {
        "nombre": "Cuaderno espiral",
        "codigo_barras": "7702011000001",
        "precio_costo": 2500,
        "precio_venta": 4000,
        "cantidad_actual": 15,
        "stock_minimo": 5,
        "categoria": "Utiles escolares",
        "unidad_medida": "unidad",
    }
    r = client.post("/productos/", json=payload, headers=auth(admin_data["token"]))
    assert r.status_code == 201
    body = r.json()
    assert body["nombre"] == "Cuaderno espiral"
    assert body["codigo_barras"] == "7702011000001"
    assert "id" in body


def test_tendero_no_puede_crear_producto(client):
    admin_data = registrar_admin(client)
    tendero = registrar_tendero(client, admin_data["token"], admin_data["empresa_id"],
                                email="tendero_crear@papeleria.com")

    payload = {
        "nombre": "Cuaderno",
        "codigo_barras": "7702011000002",
        "precio_costo": 2500,
        "precio_venta": 4000,
        "cantidad_actual": 15,
        "stock_minimo": 5,
        "categoria": "Utiles escolares",
        "unidad_medida": "unidad",
    }
    r = client.post("/productos/", json=payload, headers=auth(tendero["token"]))
    assert r.status_code == 403


def test_barcode_duplicado_misma_empresa(client):
    admin_data = registrar_admin(client)
    crear_producto(client, admin_data["token"], {"codigo_barras": "7702011000003"})

    r = client.post("/productos/", json={
        "nombre": "Otro producto",
        "codigo_barras": "7702011000003",
        "precio_costo": 1000,
        "precio_venta": 2000,
        "cantidad_actual": 10,
        "stock_minimo": 5,
        "categoria": "Miscelanea",
        "unidad_medida": "unidad",
    }, headers=auth(admin_data["token"]))
    assert r.status_code == 409


def test_mismo_barcode_distinta_empresa(client):
    admin1 = registrar_admin(client, {"nit_o_cedula": "900001010", "email": "admin1@papeleria.com"})
    admin2 = registrar_admin(client, {"nit_o_cedula": "900001011", "email": "admin2@papeleria.com"})

    crear_producto(client, admin1["token"], {"codigo_barras": "7702011000004"})

    r = client.post("/productos/", json={
        "nombre": "Cuaderno otra empresa",
        "codigo_barras": "7702011000004",
        "precio_costo": 3000,
        "precio_venta": 5000,
        "cantidad_actual": 25,
        "stock_minimo": 5,
        "categoria": "Utiles escolares",
        "unidad_medida": "unidad",
    }, headers=auth(admin2["token"]))
    assert r.status_code == 201


def test_listar_productos_propia_empresa(client):
    admin_data = registrar_admin(client)
    crear_producto(client, admin_data["token"], {"codigo_barras": "7702011000005"})
    crear_producto(client, admin_data["token"], {
        "nombre": "Bolígrafo",
        "codigo_barras": "7702011000006",
        "precio_costo": 500,
        "precio_venta": 1000,
        "cantidad_actual": 100,
        "stock_minimo": 20,
        "categoria": "Utiles escolares",
        "unidad_medida": "unidad",
    })

    r = client.get(f"/productos/{admin_data['empresa_id']}", headers=auth(admin_data["token"]))
    assert r.status_code == 200
    body = r.json()
    assert "tienda" in body
    assert "total_items" in body
    assert "inventario" in body
    assert len(body["inventario"]) == 2
    assert body["total_items"] == 2


def test_listar_productos_otra_empresa(client):
    admin1 = registrar_admin(client, {"nit_o_cedula": "900001012", "email": "admin_otra1@papeleria.com"})
    admin2 = registrar_admin(client, {"nit_o_cedula": "900001013", "email": "admin_otra2@papeleria.com"})

    r = client.get(f"/productos/{admin1['empresa_id']}", headers=auth(admin2["token"]))
    assert r.status_code == 403


def test_actualizar_producto_admin(client):
    admin_data = registrar_admin(client)
    prod = crear_producto(client, admin_data["token"], {"codigo_barras": "7702011000007"})

    r = client.put(f"/productos/{prod['id']}", json={
        "nombre": "Cuaderno actualizado",
        "precio_venta": 6000,
    }, headers=auth(admin_data["token"]))
    assert r.status_code == 200
    body = r.json()
    assert body["nombre"] == "Cuaderno actualizado"
    assert body["precio_venta"] == 6000


def test_eliminar_producto_admin(client):
    admin_data = registrar_admin(client)
    prod = crear_producto(client, admin_data["token"], {"codigo_barras": "7702011000008"})

    r = client.delete(f"/productos/{prod['id']}", headers=auth(admin_data["token"]))
    assert r.status_code == 200

    r_list = client.get(f"/productos/{admin_data['empresa_id']}", headers=auth(admin_data["token"]))
    inventario = r_list.json()["inventario"]
    assert not any(p["id"] == prod["id"] for p in inventario)


def test_tendero_no_puede_eliminar_producto(client):
    admin_data = registrar_admin(client)
    prod = crear_producto(client, admin_data["token"], {"codigo_barras": "7702011000009"})
    tendero = registrar_tendero(client, admin_data["token"], admin_data["empresa_id"],
                                email="tendero_del@papeleria.com")

    r = client.delete(f"/productos/{prod['id']}", headers=auth(tendero["token"]))
    assert r.status_code == 403
