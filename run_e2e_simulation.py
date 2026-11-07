"""
End-to-End (E2E) Business Journey Simulator — Gestion Neiva Cloud
Executes the complete multi-tenant store lifecycle:
1. Deep API Healthcheck (/api/v1/health)
2. Store & Admin Registration (/api/v1/auth/registro-completo)
3. Product Catalog Creation (/api/v1/productos)
4. Atomic POS Checkout (/api/v1/ventas/{empresa_id})
5. In-App Conversational AI Agent Restock FSM (/api/v1/agente/mensaje)
6. Consolidated Financial Dashboard Verification (/api/v1/dashboard/{empresa_id})
"""
import os
import uuid

os.environ["DATABASE_URL"] = "sqlite:///./test_e2e.db"
os.environ.setdefault("SECRET_KEY", "e2e-simulation-secret-key-not-for-production")

from fastapi.testclient import TestClient
from sqlalchemy import CHAR, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.database import Base, engine
from app.main import app
from app.services.agente.session_store import InMemorySessionStore, set_session_store_instance


class _SQLiteGUID(TypeDecorator):
    """Platform-independent GUID type for SQLite E2E runs."""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID())
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return str(value)
        if not isinstance(value, uuid.UUID):
            return str(uuid.UUID(value)).replace("-", "")
        return str(value).replace("-", "")

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            return uuid.UUID(str(value))
        return value


def run_e2e() -> None:
    """Execute the full E2E store workflow and assert every stage."""
    print("=" * 70)
    print("STARTING END-TO-END (E2E) SIMULATION — GESTION NEIVA CLOUD")
    print("=" * 70)

    for table in Base.metadata.tables.values():
        for column in table.columns:
            if isinstance(column.type, PG_UUID):
                column.type = _SQLiteGUID()

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    set_session_store_instance(InMemorySessionStore())

    try:
        with TestClient(app) as client:
            # 1. Deep Healthcheck
            print("\n[1] Verifying API healthcheck (/api/v1/health)...")
            res = client.get("/api/v1/health")
            assert res.status_code == 200, f"Healthcheck failed: {res.text}"
            print(f"   [OK] API Status: {res.json()}")

            # 2. Store & Admin Registration
            print("\n[2] Registering new store tenant and administrator user...")
            random_id = str(uuid.uuid4())[:8]
            email = f"store_neiva_{random_id}@comercio.co"
            nit = f"900{random_id}-1"

            res_reg = client.post(
                "/api/v1/auth/registro-completo",
                json={
                    "nombre_comercial": f"Supertienda Neiva {random_id}",
                    "nit_o_cedula": nit,
                    "email": email,
                    "password": "PasswordPro2026!",
                    "rol": "admin",
                },
            )
            assert res_reg.status_code == 201, f"Store registration failed: {res_reg.text}"
            data_auth = res_reg.json()
            token = data_auth["access_token"]
            empresa_id = data_auth["usuario"]["empresa_id"]
            headers = {"Authorization": f"Bearer {token}"}
            print(f"   [OK] Store tenant created. ID: {empresa_id}")
            print("   [OK] Administrator authenticated and JWT issued.")

            # 3. Product Catalog Creation
            print("\n[3] Loading initial product inventory...")
            res_prod1 = client.post(
                "/api/v1/productos",
                json={
                    "nombre": "Cafe Especial Huila 500g",
                    "codigo_barras": f"7701{random_id}",
                    "precio_costo": 12000.0,
                    "precio_venta": 18500.0,
                    "cantidad_actual": 20.0,
                    "unidad_medida": "unidad",
                },
                headers=headers,
            )
            assert res_prod1.status_code == 201, f"Failed creating product 1: {res_prod1.text}"
            prod1 = res_prod1.json()
            prod1_id = prod1["id"]
            print(
                f"   [OK] Product 1 created: {prod1['nombre']} | "
                f"Stock: {prod1['cantidad_actual']} | Price: ${prod1['precio_venta']}"
            )

            res_prod2 = client.post(
                "/api/v1/productos",
                json={
                    "nombre": "Achiras Tradicionales 200g",
                    "codigo_barras": f"7702{random_id}",
                    "precio_costo": 4500.0,
                    "precio_venta": 7000.0,
                    "cantidad_actual": 50.0,
                    "unidad_medida": "unidad",
                },
                headers=headers,
            )
            assert res_prod2.status_code == 201, f"Failed creating product 2: {res_prod2.text}"
            prod2 = res_prod2.json()
            prod2_id = prod2["id"]
            print(
                f"   [OK] Product 2 created: {prod2['nombre']} | "
                f"Stock: {prod2['cantidad_actual']} | Price: ${prod2['precio_venta']}"
            )

            # 4. Atomic POS Sale Checkout
            print("\n[4] Executing atomic POS sale checkout...")
            res_venta = client.post(
                f"/api/v1/ventas/{empresa_id}",
                json={
                    "detalles": [
                        {"producto_id": prod1_id, "cantidad": 3.0},
                        {"producto_id": prod2_id, "cantidad": 5.0},
                    ]
                },
                headers=headers,
            )
            assert res_venta.status_code == 201, f"POS sale failed: {res_venta.text}"
            venta = res_venta.json()
            expected_total = (3 * 18500.0) + (5 * 7000.0)
            assert float(venta["total"]) == expected_total
            print(f"   [OK] Sale processed. Sale ID: {venta['venta_id']}")
            print(f"   [OK] Total charged: ${venta['total']} (Expected: ${expected_total})")

            res_inv = client.get("/api/v1/productos", headers=headers)
            assert res_inv.status_code == 200
            updated_stock = {p["id"]: p["cantidad_actual"] for p in res_inv.json()["inventario"]}
            assert updated_stock[prod1_id] == 17.0
            assert updated_stock[prod2_id] == 45.0
            print("   [OK] Stock deducted atomically: Cafe=17.0 (was 20), Achiras=45.0 (was 50)")

            # 5. In-App Conversational AI Agent Restock FSM
            print("\n[5] Testing In-App Conversational AI Agent restock workflow...")
            conv_id = f"e2e_conv_{random_id}"
            res_agent_preview = client.post(
                "/api/v1/agente/mensaje",
                json={
                    "mensaje": "hoy me reabasteci de 10 Cafe Especial Huila 500g, pero el precio costo incremento y ahora vale 12500",
                    "conversation_id": conv_id,
                },
                headers=headers,
            )
            assert res_agent_preview.status_code == 200, res_agent_preview.text
            preview_body = res_agent_preview.json()
            assert preview_body["estado"] == "READY_TO_CONFIRM", preview_body
            print(f"   [OK] Agent FSM preview ready: state={preview_body['estado']}")

            res_agent_confirm = client.post(
                "/api/v1/agente/mensaje",
                json={"mensaje": "sí", "conversation_id": conv_id},
                headers=headers,
            )
            assert res_agent_confirm.status_code == 200, res_agent_confirm.text
            confirm_body = res_agent_confirm.json()
            assert confirm_body["estado"] == "EXECUTED", confirm_body
            print(f"   [OK] Agent FSM restock executed: state={confirm_body['estado']}")

            res_inv2 = client.get("/api/v1/productos", headers=headers)
            final_cafe_stock = next(
                p["cantidad_actual"]
                for p in res_inv2.json()["inventario"]
                if p["id"] == prod1_id
            )
            assert final_cafe_stock == 27.0, f"Restock failed: {final_cafe_stock}"
            print("   [OK] Cafe stock updated by AI Agent: 27.0 (was 17.0)")

            # 6. Financial Dashboard Metrics
            print("\n[6] Validating consolidated metrics on Financial Dashboard...")
            res_dash = client.get(f"/api/v1/dashboard/{empresa_id}", headers=headers)
            assert res_dash.status_code == 200, f"Dashboard error: {res_dash.text}"
            dash = res_dash.json()
            print(f"   [OK] Sales today: {dash['ventas_hoy']}")
            print(f"   [OK] Revenue today: ${dash['ingresos_hoy']}")

            print("\n" + "=" * 70)
            print("ALL END-TO-END (E2E) TESTS PASSED SUCCESSFULLY! (100% OK)")
            print("=" * 70)
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
        if os.path.exists("./test_e2e.db"):
            try:
                os.remove("./test_e2e.db")
            except OSError:
                pass


if __name__ == "__main__":
    run_e2e()
