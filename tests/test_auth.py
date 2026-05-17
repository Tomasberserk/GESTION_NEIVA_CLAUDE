"""
Tests de autenticación — Sprint 3
Cubre: registro-completo, login, /me  (happy path + error paths)
"""

# Payload base reutilizado en todos los tests que necesitan un usuario previo.
# Cada test recibe una BD vacía (fixture client), así que no hay colisiones.
_REGISTRO = {
    "nombre_comercial": "Tienda Test",
    "nit_o_cedula": "900100200",
    "email": "test@tienda.com",
    "password": "password123",
    "rol": "admin",
}


# ---------------------------------------------------------------------------
# POST /auth/registro-completo
# ---------------------------------------------------------------------------

def test_registro_completo_exitoso(client):
    r = client.post("/auth/registro-completo", json=_REGISTRO)

    assert r.status_code == 201
    body = r.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["usuario"]["email"] == _REGISTRO["email"]
    assert body["usuario"]["rol"] == "admin"
    assert "empresa_id" in body["usuario"]


def test_registro_email_duplicado(client):
    # Primer registro — debe tener éxito
    client.post("/auth/registro-completo", json=_REGISTRO)

    # Segundo registro con el mismo email (NIT diferente para aislar la causa)
    segundo = {**_REGISTRO, "nit_o_cedula": "900100201"}
    r = client.post("/auth/registro-completo", json=segundo)

    # El servicio devuelve 409 Conflict cuando el email ya existe
    assert r.status_code == 409
    assert "registrado" in r.json()["detail"].lower()


# ---------------------------------------------------------------------------
# POST /token
# ---------------------------------------------------------------------------

def test_login_exitoso(client):
    client.post("/auth/registro-completo", json=_REGISTRO)

    r = client.post("/token", json={
        "email": _REGISTRO["email"],
        "password": _REGISTRO["password"],
    })

    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["usuario"]["email"] == _REGISTRO["email"]


def test_login_password_incorrecto(client):
    client.post("/auth/registro-completo", json=_REGISTRO)

    r = client.post("/token", json={
        "email": _REGISTRO["email"],
        "password": "contraseña_incorrecta",
    })

    assert r.status_code == 401
    # El mensaje es genérico para no revelar si el email existe
    assert "credenciales" in r.json()["detail"].lower()


# ---------------------------------------------------------------------------
# GET /me
# ---------------------------------------------------------------------------

def test_me_con_token(client):
    reg = client.post("/auth/registro-completo", json=_REGISTRO)
    token = reg.json()["access_token"]

    r = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert r.status_code == 200
    body = r.json()
    assert body["email"] == _REGISTRO["email"]
    assert body["rol"] == "admin"
    assert "empresa_id" in body
    assert body["is_active"] is True


def test_me_sin_token(client):
    r = client.get("/me")

    assert r.status_code == 401
