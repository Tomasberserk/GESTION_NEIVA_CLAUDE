from conftest import registrar_admin, registrar_tendero, auth


def test_admin_lista_usuarios_empresa(client):
    admin_data = registrar_admin(client)

    r = client.get(f"/usuarios/{admin_data['empresa_id']}", headers=auth(admin_data["token"]))
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert len(body) >= 1
    assert any(u["id"] == admin_data["usuario_id"] for u in body)


def test_tendero_no_puede_listar_usuarios(client):
    admin_data = registrar_admin(client)
    tendero = registrar_tendero(client, admin_data["token"], admin_data["empresa_id"],
                                email="tendero_list@papeleria.com")

    r = client.get(f"/usuarios/{admin_data['empresa_id']}", headers=auth(tendero["token"]))
    assert r.status_code == 403


def test_admin_crea_cajero(client):
    """empresa_id del body se sobreescribe con el empresa_id del JWT."""
    admin_data = registrar_admin(client)

    r = client.post("/usuarios/", json={
        "email": "cajero@papeleria.com",
        "password": "cajeropass123",
        "empresa_id": str(admin_data["empresa_id"]),
        "rol": "tendero",
    }, headers=auth(admin_data["token"]))
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "cajero@papeleria.com"
    assert body["rol"] == "tendero"
    assert body["empresa_id"] == admin_data["empresa_id"]


def test_soft_delete_usuario(client):
    admin_data = registrar_admin(client)
    tendero = registrar_tendero(client, admin_data["token"], admin_data["empresa_id"],
                                email="tendero_del@papeleria.com")

    r = client.delete(f"/usuarios/{tendero['id']}", headers=auth(admin_data["token"]))
    assert r.status_code == 200

    r_list = client.get(f"/usuarios/{admin_data['empresa_id']}", headers=auth(admin_data["token"]))
    assert r_list.status_code == 200
    assert not any(u["id"] == tendero["id"] for u in r_list.json())


def test_no_puede_eliminarse_a_si_mismo(client):
    admin_data = registrar_admin(client)

    r = client.delete(f"/usuarios/{admin_data['usuario_id']}", headers=auth(admin_data["token"]))
    assert r.status_code == 400
