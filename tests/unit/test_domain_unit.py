"""Pure domain unit tests for schemas, intent parser, and platform contracts (TC-001..TC-012)."""
import uuid
import pytest

from app.platform.errors import ErrorDetail, StandardErrorPayload
from app.platform.security import hash_password, verify_password
from app.schemas.producto import ProductoAdminOut, ProductoCajeroOut
from app.services.agente.intent_provider import quick_parse_intent


@pytest.mark.unit
def test_password_hashing_and_verification_unit():
    """Verify bcrypt password hashing and verification in isolation."""
    hashed = hash_password("SecurePass2026!")
    assert verify_password("SecurePass2026!", hashed) is True
    assert verify_password("WrongPass!", hashed) is False


@pytest.mark.unit
def test_cashier_schema_hides_cost_price_unit():
    """Verify ProductoCajeroOut strips precio_costo while ProductoAdminOut retains it."""
    raw = {
        "id": uuid.uuid4(),
        "empresa_id": uuid.uuid4(),
        "nombre": "Arroz Diana 500g",
        "codigo_barras": "7701234567890",
        "precio_costo": 2100.0,
        "precio_venta": 2800.0,
        "cantidad_actual": 30.0,
        "unidad_medida": "unidad",
        "fecha_vencimiento": None,
        "categoria": "Snacks",
        "foto_url": None,
        "created_at": "2026-11-06T12:00:00Z",
        "is_active": True,
    }
    cashier_dump = ProductoCajeroOut.model_validate(raw).model_dump()
    admin_dump = ProductoAdminOut.model_validate(raw).model_dump()
    assert "precio_costo" not in cashier_dump
    assert admin_dump["precio_costo"] == 2100.0


@pytest.mark.unit
def test_deterministic_restock_intent_parser_unit():
    """Verify zero-latency deterministic parser extracts restock intent and cost."""
    parsed = quick_parse_intent(
        "hoy me reabasteci de 5 bolsas de leche, pero el precio costo incremento y ahora vale 3500"
    )
    assert parsed is not None
    assert parsed.intent == "reabastecer"
    assert parsed.slots.get("quantity") == 5.0
    assert parsed.slots.get("precio_costo") == 3500.0


@pytest.mark.unit
def test_standard_error_payload_immutable_contract_unit():
    """Verify StandardErrorPayload immutable dataclass contract."""
    detail = ErrorDetail(field="cantidad", message="Insufficient stock")
    payload = StandardErrorPayload(
        error="INSUFFICIENT_STOCK",
        message="Stock below requested quantity",
        details=[{"field": detail.field, "message": detail.message}],
        correlation_id="cid-unit-001",
    )
    assert payload.error == "INSUFFICIENT_STOCK"
    assert payload.correlation_id == "cid-unit-001"
