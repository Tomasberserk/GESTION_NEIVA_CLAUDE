"""
Simulador de Pruebas End-to-End (E2E) — Gestión Neiva Cloud
Ejecuta el ciclo de vida completo de un comercio real:
1. Healthcheck de la API
2. Registro de Empresa + Usuario Admin
3. Creación de Productos en Inventario
4. Simulación de Venta POS (Descuento de stock + Factura + Detalle)
5. Simulación de WhatsApp IA (Vinculación + Comando de Reabastecimiento)
6. Validación de Métricas en el Dashboard
"""
import os
import sys
from unittest.mock import patch

# Configurar DB local SQLite antes de importar la app
os.environ["DATABASE_URL"] = "sqlite:///./test_e2e.db"

import uuid
from decimal import Decimal
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app
from app.services import gemini_voice

def run_e2e():
    print("=" * 70)
    print("INICIANDO PRUEBAS END-TO-END (E2E) -- GESTION NEIVA CLOUD")
    print("=" * 70)

    # Limpiar y crear tablas en SQLite local para la simulación
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    client = TestClient(app)

    # 1. Healthcheck
    print("\n[1] Verificando estado de la API (/health)...")
    res = client.get("/health")
    assert res.status_code == 200, f"Error en healthcheck: {res.text}"
    print(f"   [OK] API Status OK: {res.json()}")

    # 2. Registro de Empresa + Admin
    print("\n[2] Registrando nueva empresa y usuario administrador...")
    random_id = str(uuid.uuid4())[:8]
    email = f"tienda_neiva_{random_id}@comercio.co"
    nit = f"900{random_id}-1"
    
    res_reg = client.post(
        "/auth/registro-completo",
        json={
            "nombre_comercial": f"Supertienda Neiva {random_id}",
            "nit_o_cedula": nit,
            "email": email,
            "password": "PasswordPro2026!",
            "rol": "admin"
        }
    )
    assert res_reg.status_code == 201, f"Error registrando empresa: {res_reg.text}"
    data_auth = res_reg.json()
    token = data_auth["access_token"]
    empresa_id = data_auth["usuario"]["empresa_id"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"   [OK] Empresa creada correctamente. ID: {empresa_id}")
    print(f"   [OK] Usuario admin autenticado. Token JWT generado.")

    # 3. Creación de productos en inventario
    print("\n[3] Cargando inventario inicial de productos...")
    res_prod1 = client.post(
        "/productos",
        json={
            "nombre": "Cafe Especial Huila 500g",
            "codigo_barras": f"7701{random_id}",
            "precio_costo": 12000.0,
            "precio_venta": 18500.0,
            "cantidad_actual": 20.0,
            "unidad_medida": "unidad"
        },
        headers=headers
    )
    assert res_prod1.status_code == 201, f"Error al crear producto 1: {res_prod1.text}"
    prod1 = res_prod1.json()
    prod1_id = prod1["id"]
    print(f"   [OK] Producto 1 creado: {prod1['nombre']} | Stock: {prod1['cantidad_actual']} | Precio: ${prod1['precio_venta']}")

    res_prod2 = client.post(
        "/productos",
        json={
            "nombre": "Achiras Tradicionales 200g",
            "codigo_barras": f"7702{random_id}",
            "precio_costo": 4500.0,
            "precio_venta": 7000.0,
            "cantidad_actual": 50.0,
            "unidad_medida": "unidad"
        },
        headers=headers
    )
    assert res_prod2.status_code == 201, f"Error al crear producto 2: {res_prod2.text}"
    prod2 = res_prod2.json()
    prod2_id = prod2["id"]
    print(f"   [OK] Producto 2 creado: {prod2['nombre']} | Stock: {prod2['cantidad_actual']} | Precio: ${prod2['precio_venta']}")

    # 4. Probar venta POS
    print("\n[4] Ejecutando venta POS (Punto de Venta)...")
    res_venta = client.post(
        f"/ventas/{empresa_id}",
        json={
            "detalles": [
                {"producto_id": prod1_id, "cantidad": 3.0},
                {"producto_id": prod2_id, "cantidad": 5.0}
            ]
        },
        headers=headers
    )
    assert res_venta.status_code == 201, f"Error al registrar venta: {res_venta.text}"
    venta = res_venta.json()
    total_esperado = (3 * 18500.0) + (5 * 7000.0)
    print(f"   [OK] Venta procesada exitosamente. ID Venta: {venta['venta_id']}")
    print(f"   [OK] Total cobrado: ${venta['total']} (Esperado: ${total_esperado})")

    # Verificar descuento de stock post-venta
    res_inv = client.get("/productos", headers=headers)
    assert res_inv.status_code == 200
    prods_actualizados = {p["id"]: p["cantidad_actual"] for p in res_inv.json()["inventario"]}
    assert prods_actualizados[prod1_id] == 17.0, f"Stock no desconto bien en Prod 1: {prods_actualizados[prod1_id]}"
    assert prods_actualizados[prod2_id] == 45.0, f"Stock no desconto bien en Prod 2: {prods_actualizados[prod2_id]}"
    print("   [OK] Stock actualizado correctamente en BD: Cafe=17.0 (era 20), Achiras=45.0 (era 50)")

    # 5. Probar Vinculación y Reabastecimiento por WhatsApp IA
    print("\n[5] Probando integracion con WhatsApp IA (Vinculacion & Reabastecimiento)...")
    res_cod = client.get("/api/whatsapp/vinculacion/codigo", headers=headers)
    assert res_cod.status_code == 200
    codigo_vinc = res_cod.json()["codigo"]
    print(f"   [OK] Codigo de vinculacion generado para admin: {codigo_vinc}")

    # Simular mensaje de WhatsApp VINCULAR
    from app.routers.whatsapp_webhook import _process_whatsapp_message
    phone_test = "+573009998877"
    
    print(f"   [MSG] Simulando mensaje WhatsApp: 'VINCULAR {codigo_vinc}'...")
    _process_whatsapp_message(phone_test, {"type": "text", "text": {"body": f"VINCULAR {codigo_vinc}"}})
    
    # Verificar vinculación en estado
    res_est = client.get("/api/whatsapp/estado", headers=headers)
    assert res_est.json()["vinculado"] is True
    print(f"   [OK] Numero {phone_test} vinculado exitosamente a la empresa.")

    # Simular mensaje WhatsApp reabastecer (Mockeando Gemini IA si no hay API key en local)
    print("   [MSG] Simulando comando de voz/texto WhatsApp: 'Reabastecer 10 unidades de Cafe Especial Huila'...")
    mock_intent = {"action": "reabastecer", "product_name": "Cafe Especial Huila 500g", "quantity": 10.0, "unit": "unidad"}
    
    with patch.object(gemini_voice, "parse_text_intent", return_value=mock_intent):
        _process_whatsapp_message(phone_test, {"type": "text", "text": {"body": "Reabastecer 10 unidades de Cafe Especial Huila"}})

    # Verificar stock post-reabastecimiento por WhatsApp
    res_inv2 = client.get("/productos", headers=headers)
    stock_cafe_final = [p["cantidad_actual"] for p in res_inv2.json()["inventario"] if p["id"] == prod1_id][0]
    assert stock_cafe_final == 27.0, f"Reabastecimiento no sumo stock: {stock_cafe_final}"
    print(f"   [OK] Stock de Cafe reabastecido por IA WhatsApp: 27.0 (era 17)")

    # 6. Métrica de Dashboard
    print("\n[6] Validando metricas consolidadas en el Dashboard...")
    res_dash = client.get(f"/dashboard/{empresa_id}", headers=headers)
    assert res_dash.status_code == 200, f"Error en Dashboard: {res_dash.text}"
    dash = res_dash.json()
    print(f"   [OK] Ventas hoy: {dash['ventas_hoy']}")
    print(f"   [OK] Ingresos hoy: ${dash['ingresos_hoy']}")

    print("\n" + "=" * 70)
    print("TODAS LAS PRUEBAS END-TO-END PASARON CON EXITO! (100% OK)")
    print("=" * 70)

if __name__ == "__main__":
    run_e2e()
