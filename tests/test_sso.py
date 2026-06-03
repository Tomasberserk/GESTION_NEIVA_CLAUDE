"""
Tests de integración para el flujo Factory Launcher + SSO seguro (Sprint 7.8).

Cubre:
1. POST /soporte/solicitar-upgrade  — marca flag + crea ticket automático
2. PUT /superadmin/empresas/{id}/factory-config  — superadmin activa trial y URL
3. POST /sso/token  — genera token de un solo uso
4. GET /sso/login?token=  — canjea token, devuelve JWT + redirect_url
"""
import pytest
from datetime import datetime, timedelta, timezone

SUPERADMIN_KEY = "test-super-key-sso"


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("SUPERADMIN_KEY", SUPERADMIN_KEY)


# ─── helpers ─────────────────────────────────────────────────────────────────

def _registrar(client, suffix: str) -> tuple[dict, str]:
    """Crea empresa + admin. Devuelve (headers_jwt, empresa_id)."""
    resp = client.post("/auth/registro-completo", json={
        "nombre_comercial": f"Tienda SSO {suffix}",
        "nit_o_cedula": f"800{suffix}",
        "email": f"sso{suffix}@test.com",
        "password": "Test123456!",
        "rol": "admin",
    })
    assert resp.status_code == 201, resp.json()
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Obtener empresa_id desde el endpoint de superadmin
    empresas = client.get(
        "/superadmin/empresas",
        headers={"x-superadmin-key": SUPERADMIN_KEY},
    ).json()
    empresa = next(e for e in empresas if e["nit_o_cedula"] == f"800{suffix}")
    return headers, empresa["id"]


def _activar_factory(client, empresa_id: str, url: str = "https://erp.test.com") -> None:
    """Superadmin activa el trial y asigna URL de factory."""
    trial_dt = (datetime.now(timezone.utc) + timedelta(days=8)).isoformat()
    resp = client.put(
        f"/superadmin/empresas/{empresa_id}/factory-config",
        json={"factory_url": url, "factory_trial_expires_at": trial_dt},
        headers={"x-superadmin-key": SUPERADMIN_KEY},
    )
    assert resp.status_code == 200, resp.json()


# ─── solicitar-upgrade ───────────────────────────────────────────────────────

def test_solicitar_upgrade_crea_ticket_y_marca_flag(client):
    headers, empresa_id = _registrar(client, "u1")

    resp = client.post("/soporte/solicitar-upgrade", headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert "ticket_id" in data

    # Flag debe estar marcado en la empresa
    empresas = client.get(
        "/superadmin/empresas",
        headers={"x-superadmin-key": SUPERADMIN_KEY},
    ).json()
    empresa = next(e for e in empresas if e["id"] == empresa_id)
    assert empresa["factory_upgrade_solicitado"] is True

    # El ticket de soporte debe existir
    tickets = client.get("/soporte/tickets", headers=headers).json()
    assert any("upgrade" in t["asunto"].lower() for t in tickets)


def test_solicitar_upgrade_idempotente_devuelve_409(client):
    headers, _ = _registrar(client, "u2")
    client.post("/soporte/solicitar-upgrade", headers=headers)
    resp = client.post("/soporte/solicitar-upgrade", headers=headers)
    assert resp.status_code == 409


def test_solicitar_upgrade_sin_auth_retorna_401(client):
    resp = client.post("/soporte/solicitar-upgrade")
    assert resp.status_code == 401


# ─── superadmin factory-config ───────────────────────────────────────────────

def test_superadmin_factory_config_actualiza_empresa(client):
    _, empresa_id = _registrar(client, "u3")
    url = "https://erp-distribuidora.demo.com"
    trial_dt = (datetime.now(timezone.utc) + timedelta(days=8)).isoformat()

    resp = client.put(
        f"/superadmin/empresas/{empresa_id}/factory-config",
        json={"factory_url": url, "factory_trial_expires_at": trial_dt},
        headers={"x-superadmin-key": SUPERADMIN_KEY},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["factory_url"] == url

    empresas = client.get(
        "/superadmin/empresas",
        headers={"x-superadmin-key": SUPERADMIN_KEY},
    ).json()
    empresa = next(e for e in empresas if e["id"] == empresa_id)
    assert empresa["factory_url"] == url
    assert empresa["factory_trial_expires_at"] is not None


def test_superadmin_factory_config_sin_key_retorna_403(client):
    _, empresa_id = _registrar(client, "u4")
    resp = client.put(
        f"/superadmin/empresas/{empresa_id}/factory-config",
        json={"factory_url": "https://erp.test.com"},
    )
    assert resp.status_code == 403


# ─── SSO token generation ────────────────────────────────────────────────────

def test_sso_token_sin_factory_activa_retorna_403(client):
    headers, _ = _registrar(client, "u5")
    resp = client.post("/sso/token", headers=headers)
    assert resp.status_code == 403


def test_sso_token_genera_token_valido(client):
    headers, empresa_id = _registrar(client, "u6")
    _activar_factory(client, empresa_id)

    resp = client.post("/sso/token", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    assert len(data["token"]) == 32  # uuid4().hex
    assert "expires_at" in data


def test_sso_token_sin_auth_retorna_401(client):
    resp = client.post("/sso/token")
    assert resp.status_code == 401


# ─── SSO login (canje de token) ──────────────────────────────────────────────

def test_sso_login_retorna_jwt_y_redirect(client):
    headers, empresa_id = _registrar(client, "u7")
    _activar_factory(client, empresa_id, url="https://erp.test.com")

    token_resp = client.post("/sso/token", headers=headers).json()
    token = token_resp["token"]

    login_resp = client.get(f"/sso/login?token={token}")
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 10
    assert data["redirect_url"] == "https://erp.test.com"


def test_sso_login_token_es_de_un_solo_uso(client):
    headers, empresa_id = _registrar(client, "u8")
    _activar_factory(client, empresa_id)

    token = client.post("/sso/token", headers=headers).json()["token"]

    # Primer canje — debe funcionar
    assert client.get(f"/sso/login?token={token}").status_code == 200

    # Segundo canje — debe fallar
    assert client.get(f"/sso/login?token={token}").status_code == 401


def test_sso_login_token_invalido_retorna_401(client):
    resp = client.get("/sso/login?token=tokenfalsoymuylargo1234567890123456")
    assert resp.status_code == 401


def test_sso_login_token_vacio_retorna_422(client):
    resp = client.get("/sso/login")
    assert resp.status_code == 422
