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
