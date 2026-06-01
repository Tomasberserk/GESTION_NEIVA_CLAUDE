import os
import pytest
from unittest.mock import patch


def test_cabeceras_de_seguridad_owasp(client):
    """
    Valida la inyección correcta de cabeceras de seguridad HTTP recomendadas por OWASP (A02:2025).
    """
    res = client.get("/health")
    assert res.status_code == 200

    headers = res.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert "Strict-Transport-Security" in headers
    assert "no-store" in headers.get("Cache-Control", "")


def test_complejidad_password_registro(client):
    """
    Valida la regla de complejidad de contraseñas de OWASP (A07:2025).
    """
    # 1. Contraseña débil (solo letras) -> debe fallar con HTTP 422
    res_debil1 = client.post(
        "/auth/registro-completo",
        json={
            "nombre_comercial": "Mi Tienda Debil",
            "nit_o_cedula": "111-debil",
            "email": "debil1@tienda.com",
            "password": "sololetras",
            "rol": "admin"
        }
    )
    assert res_debil1.status_code == 422
    assert "La contraseña debe incluir al menos una letra mayúscula" in res_debil1.text

    # 2. Contraseña sin número ni carácter especial -> debe fallar con HTTP 422
    res_debil2 = client.post(
        "/auth/registro-completo",
        json={
            "nombre_comercial": "Mi Tienda Debil",
            "nit_o_cedula": "112-debil",
            "email": "debil2@tienda.com",
            "password": "PasswordSinEspecial",
            "rol": "admin"
        }
    )
    assert res_debil2.status_code == 422

    # 3. Contraseña fuerte -> debe registrar exitosamente (HTTP 201)
    res_fuerte = client.post(
        "/auth/registro-completo",
        json={
            "nombre_comercial": "Mi Tienda Fuerte",
            "nit_o_cedula": "113-fuerte",
            "email": "fuerte@tienda.com",
            "password": "SecurePass123!",
            "rol": "admin"
        }
    )
    assert res_fuerte.status_code == 201
    data = res_fuerte.json()
    assert "access_token" in data


def test_auditoria_de_seguridad_logging(client):
    """
    Valida que los eventos de autenticación escriban correctamente en el registro de auditoría (A09:2025).
    """
    log_file = "security_audit.log"
    # Borrar archivo si ya existe para empezar limpio
    if os.path.exists(log_file):
        try:
            os.remove(log_file)
        except Exception:
            pass

    # Intentar login con credenciales incorrectas para disparar LOGIN_FAILED
    res_login = client.post(
        "/token",
        json={
            "email": "intruso@test.com",
            "password": "FakePassword123!"
        }
    )
    assert res_login.status_code == 401

    # Verificar que se haya creado el archivo y contenga el evento
    assert os.path.exists(log_file)
    with open(log_file, "r", encoding="utf-8") as f:
        log_content = f.read()
        assert "LOGIN_FAILED" in log_content
        assert "intruso@test.com" in log_content
