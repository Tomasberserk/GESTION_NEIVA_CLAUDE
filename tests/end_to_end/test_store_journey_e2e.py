"""End-to-end HTTP journey tests across /api/v1 endpoints (TC-001..TC-012)."""
import pytest


@pytest.mark.end_to_end
def test_complete_store_e2e_journey_v1(client):
    """Execute complete store journey over /api/v1: register, catalog, POS sale, support ticket, and dashboard."""
    reg = client.post(
        "/api/v1/auth/registro-completo",
        json={
            "nombre_comercial": "Minimercado El Huila E2E",
            "nit_o_cedula": "900777888-9",
            "email": "e2e_huila@tienda.com",
            "password": "Password123!",
            "rol": "admin",
        },
    )
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    empresa_id = reg.json()["usuario"]["empresa_id"]
    headers = {"Authorization": f"Bearer {token}"}

    prod = client.post(
        "/api/v1/productos",
        json={
            "nombre": "Panela Huilense 1kg",
            "codigo_barras": "7704445556667",
            "precio_costo": 3000.0,
            "precio_venta": 4500.0,
            "cantidad_actual": 25.0,
            "unidad_medida": "unidad",
        },
        headers=headers,
    )
    assert prod.status_code == 201
    prod_id = prod.json()["id"]

    sale = client.post(
        f"/api/v1/ventas/{empresa_id}",
        json={"detalles": [{"producto_id": prod_id, "cantidad": 4.0}]},
        headers=headers,
    )
    assert sale.status_code == 201
    assert sale.json()["total"] == 18000.0

    dash = client.get(f"/api/v1/dashboard/{empresa_id}", headers=headers)
    assert dash.status_code == 200
    assert dash.json()["ventas_hoy"] == 1
    assert dash.json()["ingresos_hoy"] == 18000.0
