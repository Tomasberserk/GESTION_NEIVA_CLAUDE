import pytest
from unittest.mock import MagicMock
from uuid import UUID

from app import models
from app.services import whatsapp_vinculacion, whatsapp_service, gemini_voice

SUPERADMIN_KEY = "test-super-key-123"


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    """Configura las variables de entorno necesarias para WhatsApp."""
    monkeypatch.setenv("SUPERADMIN_KEY", SUPERADMIN_KEY)
    monkeypatch.setenv("WHATSAPP_ACCESS_TOKEN", "fake_access_token")
    monkeypatch.setenv("WHATSAPP_PHONE_NUMBER_ID", "fake_phone_id")
    monkeypatch.setenv("WHATSAPP_VERIFY_TOKEN", "fake_verify_token")
    monkeypatch.setenv("GOOGLE_API_KEY", "fake_google_key")


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


# ---------------------------------------------------------------------------
# GET /api/whatsapp/webhook (Meta verification)
# ---------------------------------------------------------------------------

def test_webhook_verificacion_exitosa(client):
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "fake_verify_token",
        "hub.challenge": "123456789"
    }
    r = client.get("/api/whatsapp/webhook", params=params)
    assert r.status_code == 200
    assert r.text == "123456789"


def test_webhook_verificacion_fallida(client):
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "wrong_token",
        "hub.challenge": "123456789"
    }
    r = client.get("/api/whatsapp/webhook", params=params)
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# Endpoints de vinculación (estado, codigo, desvincular)
# ---------------------------------------------------------------------------

def test_estado_whatsapp_sin_token(client):
    r = client.get("/api/whatsapp/estado")
    assert r.status_code == 401


def test_estado_y_codigo_whatsapp_flujo(client):
    headers = _registrar_empresa_y_usuario(client, "wa1")

    # 1. Chequear estado inicial (no vinculado)
    r = client.get("/api/whatsapp/estado", headers=headers)
    assert r.status_code == 200
    assert r.json() == {"vinculado": False, "telefono": None}

    # 2. Generar código de vinculación
    r = client.get("/api/whatsapp/vinculacion/codigo", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["codigo"] is not None
    assert len(body["codigo"]) == 6
    assert body["expira_en"] == 600
    assert body["telefono_vinculado"] is None

    # Limpiar el código en el diccionario de prueba antes del final si fuera necesario
    code = body["codigo"]
    
    # 3. Vincular manualmente usando la función del servicio
    # (Simulando lo que haría la background task del webhook)
    # Obtenemos el usuario de la DB
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        user = db.query(models.Usuario).filter(models.Usuario.email == "adminwa1@test.com").first()
        assert user is not None
        
        # Ejecutamos la vinculación
        whatsapp_vinculacion.verificar_codigo(code, "573001234567", db)
        
        # Chequear que se guardó
        assert user.telefono_whatsapp == "573001234567"
    finally:
        db.close()

    # 4. Chequear estado actualizado
    r = client.get("/api/whatsapp/estado", headers=headers)
    assert r.status_code == 200
    assert r.json() == {"vinculado": True, "telefono": "573001234567"}

    # 5. Intentar generar código cuando ya está vinculado
    r = client.get("/api/whatsapp/vinculacion/codigo", headers=headers)
    assert r.status_code == 200
    assert r.json() == {
        "codigo": None,
        "expira_en": None,
        "telefono_vinculado": "573001234567"
    }

    # 6. Desvincular
    r = client.delete("/api/whatsapp/vinculacion", headers=headers)
    assert r.status_code == 200
    assert r.json() == {"detail": "WhatsApp desvinculado exitosamente"}

    # 7. Chequear estado final (no vinculado)
    r = client.get("/api/whatsapp/estado", headers=headers)
    assert r.json() == {"vinculado": False, "telefono": None}


# ---------------------------------------------------------------------------
# POST /api/whatsapp/webhook (Incoming messages)
# ---------------------------------------------------------------------------

def test_webhook_post_usuario_no_vinculado(client, monkeypatch):
    # Mock de send_text_message
    sent_messages = []
    def mock_send(phone, text):
        sent_messages.append((phone, text))
        return True
    monkeypatch.setattr(whatsapp_service, "send_text_message", mock_send)

    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "573009999999",
                        "type": "text",
                        "text": {"body": "Hola bot"}
                    }]
                }
            }]
        }]
    }

    r = client.post("/api/whatsapp/webhook", json=payload)
    assert r.status_code == 200
    
    # Dado que se ejecuta en BackgroundTasks, la petición retorna 200 inmediatamente.
    # Pero el TestClient corre las background tasks de forma síncrona antes de retornar.
    assert len(sent_messages) == 1
    phone, text = sent_messages[0]
    assert phone == "573009999999"
    assert "no está vinculado" in text


def test_webhook_post_flujo_vinculacion_exitoso(client, monkeypatch):
    headers = _registrar_empresa_y_usuario(client, "wa_flow")
    
    # Obtener el código de vinculación vía API
    r = client.get("/api/whatsapp/vinculacion/codigo", headers=headers)
    code = r.json()["codigo"]

    # Mock de send_text_message
    sent_messages = []
    def mock_send(phone, text):
        sent_messages.append((phone, text))
        return True
    monkeypatch.setattr(whatsapp_service, "send_text_message", mock_send)

    # Enviar comando de vinculación
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "573008888888",
                        "type": "text",
                        "text": {"body": f"VINCULAR {code}"}
                    }]
                }
            }]
        }]
    }

    r = client.post("/api/whatsapp/webhook", json=payload)
    assert r.status_code == 200
    
    # Verificar que el mensaje enviado fue de éxito
    assert len(sent_messages) == 1
    phone, text = sent_messages[0]
    assert phone == "573008888888"
    assert "vinculada exitosamente" in text

    # Verificar en la base de datos que el usuario está efectivamente vinculado
    r = client.get("/api/whatsapp/estado", headers=headers)
    assert r.json() == {"vinculado": True, "telefono": "573008888888"}


def test_webhook_post_usuario_vinculado_reabastecer(client, monkeypatch):
    headers = _registrar_empresa_y_usuario(client, "wa_action")
    
    # 1. Vincular el usuario manualmente
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        user = db.query(models.Usuario).filter(models.Usuario.email == "adminwa_action@test.com").first()
        user.telefono_whatsapp = "573007777777"
        
        # 2. Crear un producto de prueba en la base de datos
        producto = models.Producto(
            empresa_id=user.empresa_id,
            nombre="Gaseosa Coca-Cola 1.5L",
            codigo_barras="7701234567890",
            precio_costo=3500.0,
            precio_venta=4500.0,
            cantidad_actual=5.0,
            unidad_medida="unidad",
            categoria="Bebidas",
            is_active=True
        )
        db.add(producto)
        db.commit()
    finally:
        db.close()

    # Mocks
    sent_messages = []
    def mock_send(phone, text):
        sent_messages.append((phone, text))
        return True
    monkeypatch.setattr(whatsapp_service, "send_text_message", mock_send)

    def mock_parse_intent(text, product_names):
        assert "Gaseosa Coca-Cola 1.5L" in product_names
        return {
            "action": "reabastecer",
            "product_name": "Gaseosa Coca-Cola 1.5L",
            "quantity": 10,
            "confidence": 0.95,
            "unit": "unidad",
            "raw_text": text
        }
    monkeypatch.setattr(gemini_voice, "parse_text_intent", mock_parse_intent)

    # Petición webhook con texto
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "573007777777",
                        "type": "text",
                        "text": {"body": "Agregué 10 gaseosas de coca cola"}
                    }]
                }
            }]
        }]
    }

    r = client.post("/api/whatsapp/webhook", json=payload)
    assert r.status_code == 200

    # Verificar que responda con la confirmación de reabastecimiento
    assert len(sent_messages) == 1
    phone, text = sent_messages[0]
    assert phone == "573007777777"
    assert "reabastecido" in text.lower() or "coca-cola" in text.lower()

    # Verificar que el stock haya aumentado de 5 a 15
    db = SessionLocal()
    try:
        prod = db.query(models.Producto).filter(models.Producto.codigo_barras == "7701234567890").first()
        assert float(prod.cantidad_actual) == 15.0
    finally:
        db.close()
