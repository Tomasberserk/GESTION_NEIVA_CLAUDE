import pytest
import os

SUPERADMIN_KEY = "test-super-key-123"


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("SUPERADMIN_KEY", SUPERADMIN_KEY)


def test_superadmin_empresas_sin_key_retorna_403(client, monkeypatch):
    monkeypatch.setenv("SUPERADMIN_KEY", SUPERADMIN_KEY)
    resp = client.get("/superadmin/empresas")
    assert resp.status_code == 403


def test_superadmin_empresas_key_invalida_retorna_403(client, monkeypatch):
    monkeypatch.setenv("SUPERADMIN_KEY", SUPERADMIN_KEY)
    resp = client.get("/superadmin/empresas", headers={"x-superadmin-key": "wrong"})
    assert resp.status_code == 403


def test_superadmin_empresas_con_key_valida_retorna_200(client, monkeypatch):
    monkeypatch.setenv("SUPERADMIN_KEY", SUPERADMIN_KEY)
    resp = client.get("/superadmin/empresas", headers={"x-superadmin-key": SUPERADMIN_KEY})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


# ─────────────────────────────────────────────
# Fixtures de empresa + usuario para tests de soporte
# ─────────────────────────────────────────────

def _registrar_empresa_y_usuario(client, suffix: str) -> dict:
    """Crea empresa y admin, retorna headers de autenticación."""
    reg_resp = client.post("/auth/registro-completo", json={
        "nombre_comercial": f"Tienda {suffix}",
        "nit_o_cedula": f"9000{suffix}",
        "email": f"admin{suffix}@test.com",
        "password": "Test123456!",
        "rol": "admin",
    })
    assert reg_resp.status_code == 201, reg_resp.json()
    token = reg_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_usuario_puede_crear_ticket(client):
    headers = _registrar_empresa_y_usuario(client, "crm1")
    resp = client.post("/soporte/tickets", json={
        "asunto": "Error en inventario",
        "mensaje": "No puedo agregar productos",
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["asunto"] == "Error en inventario"
    assert data["estado"] == "abierto"


def test_usuario_puede_listar_sus_tickets(client):
    headers = _registrar_empresa_y_usuario(client, "crm2")
    client.post("/soporte/tickets", json={
        "asunto": "Consulta de prueba",
        "mensaje": "Mensaje inicial",
    }, headers=headers)
    resp = client.get("/soporte/tickets", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_superadmin_ve_todos_los_tickets(client, monkeypatch):
    monkeypatch.setenv("SUPERADMIN_KEY", SUPERADMIN_KEY)
    headers_a = _registrar_empresa_y_usuario(client, "crm3")
    headers_b = _registrar_empresa_y_usuario(client, "crm4")
    client.post("/soporte/tickets", json={"asunto": "Ticket A", "mensaje": "msg"}, headers=headers_a)
    client.post("/soporte/tickets", json={"asunto": "Ticket B", "mensaje": "msg"}, headers=headers_b)
    resp = client.get("/superadmin/tickets", headers={"x-superadmin-key": SUPERADMIN_KEY})
    assert resp.status_code == 200
    asuntos = [t["asunto"] for t in resp.json()]
    assert "Ticket A" in asuntos
    assert "Ticket B" in asuntos


def test_flujo_completo_ticket_respuesta(client, monkeypatch):
    monkeypatch.setenv("SUPERADMIN_KEY", SUPERADMIN_KEY)
    headers = _registrar_empresa_y_usuario(client, "crm5")
    # 1. Usuario abre ticket
    create_resp = client.post("/soporte/tickets", json={
        "asunto": "Duda de facturación",
        "mensaje": "¿Cómo exporto el reporte?",
    }, headers=headers)
    assert create_resp.status_code == 201
    ticket_id = create_resp.json()["id"]

    # 2. Superadmin responde
    admin_resp = client.post(
        f"/superadmin/tickets/{ticket_id}/responder",
        json={"mensaje": "Ve a Reportes > Exportar Excel."},
        headers={"x-superadmin-key": SUPERADMIN_KEY},
    )
    assert admin_resp.status_code == 200

    # 3. Usuario ve la respuesta en el hilo
    detail_resp = client.get(f"/soporte/tickets/{ticket_id}", headers=headers)
    assert detail_resp.status_code == 200
    data = detail_resp.json()
    assert data["estado"] == "respondido"
    assert len(data["mensajes"]) == 2
    assert data["mensajes"][1]["remitente_rol"] == "superadmin"
