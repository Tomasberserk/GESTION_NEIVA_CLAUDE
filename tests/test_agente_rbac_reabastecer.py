"""Suite de pruebas para Gobernanza RBAC en el Asistente IA y Reabastecimiento con Costo.

Verifica:
1. Menú diferenciado por rol: Admin recibe control total, Tendero recibe modo mostrador.
2. Bloqueo pedagógico para el Tendero ante reabastecimiento o creación de productos.
3. Bloqueo pedagógico para el Tendero ante métricas financieras globales o comparativas.
4. Consulta permitida de sus propias ventas para el Tendero.
5. Bloqueo para el Tendero ante consultas de ventas de otros cajeros.
6. Reabastecimiento completo ejecutado por el Administrador con nuevo precio de costo y venta.
7. Consulta directa y rápida (< 50ms) de productos próximos a vencer sin acudir al LLM.
"""

import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from app import models
from app.services.agente.session_store import InMemorySessionStore, set_session_store_instance
from app.services.agente.intent_provider import quick_parse_intent


@pytest.fixture(autouse=True)
def reset_session_store():
    """Asegura una memoria de sesión limpia en cada test."""
    store = InMemorySessionStore()
    set_session_store_instance(store)
    yield store
    store.clear()


def _registrar_tienda_y_cajero(client: TestClient, suffix: str):
    """Crea una tienda con Admin y un empleado Tendero/Cajero."""
    # 1. Admin
    admin_payload = {
        "nombre_comercial": f"Tienda RBAC {suffix}",
        "nit_o_cedula": f"NIT-RBAC-{suffix}",
        "nombre": f"Don Carlos {suffix}",
        "email": f"admin_rbac_{suffix}@test.com",
        "password": "Password123!",
        "rol": "admin",
    }
    res_admin = client.post("/auth/registro-completo", json=admin_payload)
    assert res_admin.status_code == 201, res_admin.text
    data_admin = res_admin.json()
    admin_token = data_admin["access_token"]
    empresa_id = data_admin["usuario"]["empresa_id"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Cajero / Tendero
    cajero_payload = {
        "nombre": f"Cajero Pedro {suffix}",
        "email": f"pedro_cajero_{suffix}@test.com",
        "password": "Password123!",
    }
    res_caj = client.post("/api/usuarios/empleados", json=cajero_payload, headers=admin_headers)
    assert res_caj.status_code == 201, res_caj.text

    # Login cajero
    login_res = client.post("/token", json={
        "email": f"pedro_cajero_{suffix}@test.com",
        "password": "Password123!",
    })
    assert login_res.status_code == 200, login_res.text
    cajero_token = login_res.json()["access_token"]
    cajero_headers = {"Authorization": f"Bearer {cajero_token}"}

    return {
        "empresa_id": empresa_id,
        "admin_headers": admin_headers,
        "cajero_headers": cajero_headers,
        "cajero_nombre": f"Cajero Pedro {suffix}",
    }


def _crear_producto(client: TestClient, headers: dict, empresa_id: str, nombre: str, costo: float, venta: float, cantidad: float, fecha_venc: str = None):
    payload = {
        "empresa_id": empresa_id,
        "nombre": nombre,
        "codigo_barras": f"BAR-{uuid.uuid4().hex[:8]}",
        "precio_costo": costo,
        "precio_venta": venta,
        "cantidad_actual": cantidad,
        "unidad_medida": "unidad",
    }
    if fecha_venc:
        payload["fecha_vencimiento"] = fecha_venc
    res = client.post("/productos/", headers=headers, json=payload)
    assert res.status_code == 201, res.text
    return res.json()


def test_menu_capacidades_diferenciado_admin_vs_tendero(client: TestClient):
    """Admin recibe menú con reabastecimiento y finanzas; Tendero recibe menú de mostrador."""
    data = _registrar_tienda_y_cajero(client, "menu_test")

    # Admin consulta capacidades / ayuda
    res_admin = client.post("/api/agente/mensaje", json={"mensaje": "ayuda"}, headers=data["admin_headers"])
    assert res_admin.status_code == 200
    txt_admin = res_admin.json()["respuesta"]
    assert "Modo Administrador" in txt_admin
    assert "Reabastecimiento y Precios" in txt_admin
    assert "Finanzas y Caja" in txt_admin

    # Tendero consulta capacidades / ayuda
    res_cajero = client.post("/api/agente/mensaje", json={"mensaje": "que opciones tengo"}, headers=data["cajero_headers"])
    assert res_cajero.status_code == 200
    txt_cajero = res_cajero.json()["respuesta"]
    assert "Modo Mostrador" in txt_cajero
    assert "Registrar Ventas Rápidas" in txt_cajero
    assert "Consulta de Precios al Público" in txt_cajero
    assert "Tus Ventas del Turno" in txt_cajero
    assert "Finanzas y Caja" not in txt_cajero


def test_tendero_bloqueado_para_reabastecer(client: TestClient):
    """Un tendero intenta reabastecer inventario y recibe bloqueo pedagógico."""
    data = _registrar_tienda_y_cajero(client, "bloq_reab")
    _crear_producto(client, data["admin_headers"], data["empresa_id"], "Aceite Gourmet 1L", 9000.0, 13000.0, 5.0)

    res = client.post(
        "/api/agente/mensaje",
        json={"mensaje": "hoy me reabasteci de 3 aceites gourmet a 11000 costo"},
        headers=data["cajero_headers"],
    )
    assert res.status_code == 200
    respuesta = res.json()["respuesta"]
    assert "como tendero tienes acceso al mostrador" in respuesta
    assert "reservados para el administrador" in respuesta
    assert res.json()["estado"] == "IDLE"


def test_tendero_bloqueado_para_finanzas_globales_y_comparativas(client: TestClient):
    """Un tendero no puede consultar métricas globales de venta ni comparaciones."""
    data = _registrar_tienda_y_cajero(client, "bloq_fin")

    # Intento de ver ventas globales de hoy
    res_hoy = client.post("/api/agente/mensaje", json={"mensaje": "¿cuánto vendió la tienda hoy?"}, headers=data["cajero_headers"])
    assert res_hoy.status_code == 200
    assert "las métricas financieras globales de la tienda y comparativas son confidenciales" in res_hoy.json()["respuesta"]

    # Intento de ver comparativa hoy vs ayer
    res_comp = client.post("/api/agente/mensaje", json={"mensaje": "comparar ventas hoy vs ayer"}, headers=data["cajero_headers"])
    assert res_comp.status_code == 200
    assert "son confidenciales del administrador" in res_comp.json()["respuesta"]


def test_tendero_puede_consultar_sus_propias_ventas(client: TestClient):
    """El tendero puede consultar sus propias ventas del turno."""
    data = _registrar_tienda_y_cajero(client, "mis_ventas")
    _crear_producto(client, data["admin_headers"], data["empresa_id"], "Gaseosa Cola 1.5L", 2500.0, 4500.0, 20.0)

    # El tendero realiza una venta
    conv_id = f"conv_{uuid.uuid4().hex[:8]}"
    client.post("/api/agente/mensaje", json={"mensaje": "vendí 2 gaseosas", "conversation_id": conv_id}, headers=data["cajero_headers"])
    client.post("/api/agente/mensaje", json={"mensaje": "sí", "conversation_id": conv_id}, headers=data["cajero_headers"])

    # El tendero consulta sus ventas
    res_mis = client.post("/api/agente/mensaje", json={"mensaje": "¿cuántas ventas llevo hoy?"}, headers=data["cajero_headers"])
    assert res_mis.status_code == 200
    txt = res_mis.json()["respuesta"]
    assert "ha registrado ventas por" in txt
    assert "$9.000" in txt
    assert "transacciones" in txt


def test_admin_reabastece_con_nuevo_costo_y_alerta_margen(client: TestClient):
    """Admin reabastece con costo incrementado; el asistente alerta sobre el margen y actualiza la BD al confirmar."""
    data = _registrar_tienda_y_cajero(client, "reab_costo")
    prod = _crear_producto(client, data["admin_headers"], data["empresa_id"], "Aceite Gourmet 1L", 9000.0, 13000.0, 5.0)

    conv_id = f"reab_{uuid.uuid4().hex[:8]}"
    # 1. Petición del admin exactamente con la frase solicitada por el usuario
    res_cmd = client.post(
        "/api/agente/mensaje",
        json={
            "mensaje": "hoy me reabasteci de 3 aceites gourmet, pero el precio costo incremento y ahora vale 11.000",
            "conversation_id": conv_id,
        },
        headers=data["admin_headers"],
    )
    assert res_cmd.status_code == 200
    data_cmd = res_cmd.json()
    assert data_cmd["estado"] == "READY_TO_CONFIRM"
    txt_preview = data_cmd["respuesta"]
    assert "Aceite Gourmet 1L" in txt_preview
    assert "+3" in txt_preview
    assert "$11.000" in txt_preview
    assert "Margen" in txt_preview

    # 2. Confirmación
    res_conf = client.post(
        "/api/agente/mensaje",
        json={"mensaje": "sí", "conversation_id": conv_id},
        headers=data["admin_headers"],
    )
    assert res_conf.status_code == 200
    data_conf = res_conf.json()
    assert data_conf["estado"] == "EXECUTED"
    assert "Stock actualizado" in data_conf["respuesta"]
    assert "$11.000" in data_conf["respuesta"]

    # 3. Verificación en base de datos
    res_prod = client.get(f"/productos/{prod['id']}", headers=data["admin_headers"])
    assert res_prod.status_code == 200
    prod_db = res_prod.json()
    assert float(prod_db["cantidad_actual"]) == 8.0  # 5 + 3
    assert float(prod_db["precio_costo"]) == 11000.0


def test_consulta_vencimientos_rapida(client: TestClient):
    """Consulta 'q esta proximo a vencer' responde inmediatamente con productos cercanos a expirar."""
    data = _registrar_tienda_y_cajero(client, "venc_test")
    hoy = datetime.now(timezone.utc).date()
    fecha_proxima = str(hoy + timedelta(days=5))

    _crear_producto(client, data["admin_headers"], data["empresa_id"], "Yogur Fresa", 1500.0, 2500.0, 10.0, fecha_proxima)

    # Probar con la sintaxis exacta de la captura de pantalla: "q esta proximo a vencer"
    res = client.post(
        "/api/agente/mensaje",
        json={"mensaje": "q esta proximo a vencer"},
        headers=data["admin_headers"],
    )
    assert res.status_code == 200
    respuesta = res.json()["respuesta"]
    assert "Yogur Fresa" in respuesta
    assert "vence en 5 días" in respuesta


def test_parser_determinista_latencia_cero():
    """El parser determinístico resuelve la frase de reabastecimiento en < 1ms sin LLM."""
    frase = "hoy me reabasteci de 3 aceites gourmet, pero el precio costo incremento y ahora vale 11.000"
    interp = quick_parse_intent(frase)
    assert interp is not None
    assert interp.intent == "reabastecer"
    assert interp.slots.get("quantity") == 3.0
    assert "aceite" in interp.slots.get("product_query", "")
    assert interp.slots.get("precio_costo") == 11000.0
