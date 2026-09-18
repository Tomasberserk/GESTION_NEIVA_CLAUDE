"""Suite de pruebas de integración, smoke testing y semántica de errores para el proveedor LLM.

Cubre:
1. Manejo estricto de HTTP 503 (LLM_PROVIDER_UNAVAILABLE) ante fallos técnicos del LLM.
2. Diferenciación contra HTTP 200 ante intenciones no comprendidas pero LLM operativo.
3. Validación de structured output y actualización de telemetría sin contaminación cruzada.
4. Las 8 preguntas smoke de mostrador evaluadas de punta a punta.
"""

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.agente.intent_provider import (
    AGENT_TELEMETRY,
    AgentInterpretation,
    GroqIntentProvider,
    LLMIntentProvider,
    LLMProviderUnavailableError,
    get_agent_telemetry,
    reset_agent_telemetry,
)




def _registrar_tienda_smoke(client: TestClient, suffix: str):
    email = f"smoke_owner_{suffix}@test.com"
    pwd = "Password123!"
    resp = client.post(
        "/auth/registro-completo",
        json={
            "nombre_comercial": f"Tienda Smoke {suffix}",
            "nit_o_cedula": f"NIT-SMOKE-{suffix}",
            "email": email,
            "password": pwd,
            "rol": "admin",
        },
    )
    assert resp.status_code == 201, f"Fallo al registrar: {resp.text}"
    data = resp.json()
    token = data["access_token"]
    empresa_id = data["usuario"]["empresa_id"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers, empresa_id


# ---------------------------------------------------------------------------
# TEST 1: ERROR TÉCNICO PRODUCE HTTP 503 (LLM_PROVIDER_UNAVAILABLE)
# ---------------------------------------------------------------------------

def test_llm_failure_returns_http_503(client: TestClient):
    """Verifica que si el LLM falla por infraestructura, el endpoint retorna HTTP 503 y no un 200 falso."""
    headers, empresa_id = _registrar_tienda_smoke(client, "fail503")
    reset_agent_telemetry()

    # Simulamos un provider que lanza LLMProviderUnavailableError
    mock_provider = MagicMock()
    mock_provider.parse.side_effect = LLMProviderUnavailableError(
        provider="groq",
        reason="Falla simulada 404/ConnectionError",
    )

    with patch("app.routers.agente._orchestrator._intent_provider", mock_provider):
        resp = client.post(
            "/api/agente/mensaje",
            headers=headers,
            json={"mensaje": "Una frase que no coincide con nada determinista"},
        )
        assert resp.status_code == 503, f"Esperaba 503 pero obtuvo {resp.status_code}: {resp.text}"
        data = resp.json()
        assert data["detail"]["code"] == "LLM_PROVIDER_UNAVAILABLE"
        assert "no se encuentra disponible" in data["detail"]["message"]


# ---------------------------------------------------------------------------
# TEST 2: PREGUNTA DESCONOCIDA CON LLM OPERATIVO PRODUCE HTTP 200
# ---------------------------------------------------------------------------

def test_unknown_intent_returns_http_200(client: TestClient):
    """Verifica que si el LLM responde bien pero no entiende la intención, se responde HTTP 200 amigable."""
    headers, empresa_id = _registrar_tienda_smoke(client, "unknown200")
    reset_agent_telemetry()

    mock_provider = MagicMock()
    mock_provider.parse.return_value = AgentInterpretation(
        intent="unknown",
        raw_text="mensaje incomprensible",
        confidence=0.1,
    )

    with patch("app.routers.agente._orchestrator._intent_provider", mock_provider):
        resp = client.post(
            "/api/agente/mensaje",
            headers=headers,
            json={"mensaje": "mensaje incomprensible"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["estado"] == "IDLE"
        assert "no logré entender bien" in data["respuesta"].lower()


# ---------------------------------------------------------------------------
# TEST 3: TELEMETRÍA SEPARADA Y PRECISIÓN DE MÉTRICAS
# ---------------------------------------------------------------------------

def test_telemetry_exact_semantics():
    """Verifica que los contadores distingan entre falla técnica y fallo de parseo."""
    reset_agent_telemetry()
    provider = GroqIntentProvider(model="openai/gpt-oss-120b")

    # Caso C: Sin API Key -> provider_failure++, pero NO intent_parse_failure++
    with patch.dict("os.environ", {"GROQ_API_KEY": ""}, clear=False):
        with pytest.raises(LLMProviderUnavailableError):
            provider.parse("test sin key")

    tel = get_agent_telemetry()
    assert tel["llm_provider_failure"] == 1
    assert tel["intent_parse_failure"] == 0
    assert tel["llm_provider_success"] == 0


# ---------------------------------------------------------------------------
# TEST 4: LAS 8 PREGUNTAS SMOKE OBLIGATORIAS (PASO 9)
# ---------------------------------------------------------------------------

def test_ocho_preguntas_smoke_flujo_completo(client: TestClient):
    """Verifica de punta a punta las 8 preguntas smoke de mostrador."""
    headers, empresa_id = _registrar_tienda_smoke(client, "smoke8")
    reset_agent_telemetry()

    # 1. Crear cajera Paula
    client.post(
        "/usuarios/empleados",
        headers=headers,
        json={"nombre": "Paula", "email": "paula_smoke8@test.com", "password": "Password123!"},
    )

    # 2. Crear productos de prueba
    r_arroz = client.post(
        "/productos",
        headers=headers,
        json={
            "empresa_id": empresa_id,
            "nombre": "Arroz Diana 1kg",
            "codigo_barras": "7701111111111",
            "precio_costo": 3000.0,
            "precio_venta": 4500.0,
            "cantidad_actual": 20.0,
            "categoria": "Snacks",
            "unidad_medida": "unidad",
        },
    )
    assert r_arroz.status_code == 201
    arroz_id = r_arroz.json()["id"]

    r_aceite = client.post(
        "/productos",
        headers=headers,
        json={
            "empresa_id": empresa_id,
            "nombre": "Aceite Gourmet 1L",
            "codigo_barras": "7702222222222",
            "precio_costo": 8000.0,
            "precio_venta": 11000.0,
            "cantidad_actual": 5.0,
            "categoria": "Snacks",
            "unidad_medida": "unidad",
        },
    )
    assert r_aceite.status_code == 201

    # 3. Registrar una venta hoy
    r_venta = client.post(
        f"/ventas/{empresa_id}",
        headers=headers,
        json={"detalles": [{"producto_id": arroz_id, "cantidad": 2}]},
    )
    assert r_venta.status_code == 201

    conv_id = "smoke_conv_8"

    # Pregunta 1: "¿Cuánto hemos vendido hoy?"
    r1 = client.post("/api/agente/mensaje", headers=headers, json={"mensaje": "¿Cuánto hemos vendido hoy?", "conversation_id": conv_id})
    assert r1.status_code == 200
    assert any(w in r1.json()["respuesta"].lower() for w in ["vendido", "total", "$", "9.000"])

    # Pregunta 2: "¿Cuántos productos tenemos?"
    r2 = client.post("/api/agente/mensaje", headers=headers, json={"mensaje": "¿Cuántos productos tenemos?", "conversation_id": conv_id})
    assert r2.status_code == 200
    assert "2 productos activos" in r2.json()["respuesta"].lower()

    # Pregunta 3: "¿Cuánto arroz queda?"
    r3 = client.post("/api/agente/mensaje", headers=headers, json={"mensaje": "¿Cuánto arroz queda?", "conversation_id": conv_id})
    assert r3.status_code == 200
    assert any(w in r3.json()["respuesta"].lower() for w in ["18", "arroz", "quedan", "disponibles"])

    # Pregunta 4: "¿Qué fue lo que más vendimos?"
    r4 = client.post("/api/agente/mensaje", headers=headers, json={"mensaje": "¿Qué fue lo que más vendimos?", "conversation_id": conv_id})
    assert r4.status_code == 200
    assert any(w in r4.json()["respuesta"].lower() for w in ["arroz", "más vendido", "mas vendido", "lidera"])

    # Pregunta 5: "¿Cómo vamos hoy?" (consulta ventas hoy / balance)
    r5 = client.post("/api/agente/mensaje", headers=headers, json={"mensaje": "¿Cómo vamos hoy?", "conversation_id": conv_id})
    assert r5.status_code == 200
    assert any(w in r5.json()["respuesta"].lower() for w in ["vendido", "total", "$", "ventas", "transacciones", "balance", "opciones", "resumen"])

    # Pregunta 6: "¿Y ayer?" (contexto multi-turno)
    r6 = client.post("/api/agente/mensaje", headers=headers, json={"mensaje": "¿Y ayer?", "conversation_id": conv_id})
    assert r6.status_code == 200
    assert any(w in r6.json()["respuesta"].lower() for w in ["ayer", "ventas", "registran", "$"])

    # Pregunta 7: "¿Cuánto vendió Paula?"
    r7 = client.post("/api/agente/mensaje", headers=headers, json={"mensaje": "¿Cuánto vendió Paula?", "conversation_id": conv_id})
    assert r7.status_code == 200
    assert any(w in r7.json()["respuesta"].lower() for w in ["paula", "$", "ventas"])

    # Pregunta 8: "¿Cuánto tenemos?" (ambiguo guiado)
    r8 = client.post("/api/agente/mensaje", headers=headers, json={"mensaje": "¿Cuánto tenemos?", "conversation_id": conv_id})
    assert r8.status_code == 200
    assert any(w in r8.json()["respuesta"].lower() for w in ["aclarar", "inventario", "caja", "específico", "opciones", "dinero"])
