import pytest
from conftest import registrar_admin, auth


def test_registro_exitoso(client):
    """Registro exitoso → 201, campos correctos."""
    payload = {
        "nombre_comercial": "Papelería Nueva",
        "nit_o_cedula": "900001002",
        "email": "test@papeleria.com",
        "password": "testpass123",
        "rol": "admin",
    }
    r = client.post("/auth/registro", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["usuario"]["email"] == "test@papeleria.com"
    assert body["usuario"]["rol"] == "admin"
    assert "empresa_id" in body["usuario"]
    assert "id" in body["usuario"]
    assert "created_at" in body["usuario"]
    assert body["usuario"]["is_active"] is True


def test_registro_email_duplicado(client):
    """Registro email duplicado → 409."""
    payload = {
        "nombre_comercial": "Papelería 1",
        "nit_o_cedula": "900001003",
        "email": "dup@papeleria.com",
        "password": "testpass123",
        "rol": "admin",
    }
    r1 = client.post("/auth/registro", json=payload)
    assert r1.status_code == 201

    payload["nit_o_cedula"] = "900001004"
    r2 = client.post("/auth/registro", json=payload)
    assert r2.status_code == 409


def test_registro_nit_duplicado(client):
    """Registro NIT duplicado → 409."""
    payload = {
        "nombre_comercial": "Papelería A",
        "nit_o_cedula": "900001005",
        "email": "email1@papeleria.com",
        "password": "testpass123",
        "rol": "admin",
    }
    r1 = client.post("/auth/registro", json=payload)
    assert r1.status_code == 201

    payload["email"] = "email2@papeleria.com"
    r2 = client.post("/auth/registro", json=payload)
    assert r2.status_code == 409


def test_login_exitoso(client):
    """Login exitoso → 200, token + usuario."""
    admin_data = registrar_admin(client)

    r = client.post("/auth/login", json={
        "email": "admin@papeleria.com",
        "password": "testpass123",
    })
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["usuario"]["email"] == "admin@papeleria.com"
    assert body["usuario"]["id"] == admin_data["usuario_id"]


def test_login_password_incorrecto(client):
    """Login password incorrecto → 401."""
    registrar_admin(client)

    r = client.post("/auth/login", json={
        "email": "admin@papeleria.com",
        "password": "wrongpassword",
    })
    assert r.status_code == 401


def test_token_endpoint_alias(client):
    """Alias POST /token → 200."""
    registrar_admin(client)

    r = client.post("/token", json={
        "email": "admin@papeleria.com",
        "password": "testpass123",
    })
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body


def test_get_me_con_token(client):
    """GET /auth/me con token → 200."""
    admin_data = registrar_admin(client)

    r = client.get("/auth/me", headers=auth(admin_data["token"]))
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == "admin@papeleria.com"
    assert body["id"] == admin_data["usuario_id"]
    assert body["rol"] == "admin"


def test_get_me_sin_token(client):
    """GET /auth/me sin token → 401."""
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_get_me_token_invalido(client):
    """GET /auth/me token inválido → 401."""
    r = client.get("/auth/me", headers=auth("token_invalido_12345"))
    assert r.status_code == 401
