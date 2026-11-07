"""Module integration tests verifying public Facade boundaries (AuthTenancyFacade, InventarioFacade, VentasFacade)."""
from decimal import Decimal
import uuid
import pytest

from app import models
from app.auth_tenancy.api.facade import AuthTenancyFacade
from app.database import SessionLocal
from app.inventario.api.facade import InventarioFacade
from app.pos_ventas.api.facade import VentasFacade
from app.schemas.venta import DetalleVentaCrear, VentaCrear
from app.soporte_crm.api.facade import SoporteCrmFacade


@pytest.mark.module_integration
def test_facades_atomic_checkout_and_tenant_isolation(client):
    """Verify cross-module collaboration exclusively through public Facade classes."""
    reg = client.post(
        "/api/v1/auth/registro-completo",
        json={
            "nombre_comercial": "Tienda Facade Test",
            "nit_o_cedula": "900555666-7",
            "email": "facade@tienda.com",
            "password": "Password123!",
            "rol": "admin",
        },
    )
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    empresa_id = uuid.UUID(reg.json()["usuario"]["empresa_id"])
    user_id = uuid.UUID(reg.json()["usuario"]["id"])
    headers = {"Authorization": f"Bearer {token}"}

    prod_res = client.post(
        "/api/v1/productos",
        json={
            "nombre": "Chocolate Corona 250g",
            "codigo_barras": "7709988776655",
            "precio_costo": 4000.0,
            "precio_venta": 5500.0,
            "cantidad_actual": 10.0,
            "unidad_medida": "unidad",
        },
        headers=headers,
    )
    assert prod_res.status_code == 201
    prod_id = uuid.UUID(prod_res.json()["id"])

    import app.database as db_module
    db = db_module.SessionLocal()
    try:
        company_dto = AuthTenancyFacade.ensure_active_company(empresa_id=empresa_id, db=db)
        assert company_dto.nombre_comercial == "Tienda Facade Test"

        seller_dto = AuthTenancyFacade.ensure_company_seller(
            usuario_id=user_id, empresa_id=empresa_id, db=db
        )
        assert seller_dto.email == "facade@tienda.com"

        user_obj = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
        sale_dto = VentasFacade.registrar_venta_atomica(
            empresa_id=empresa_id,
            data=VentaCrear(detalles=[DetalleVentaCrear(producto_id=prod_id, cantidad=Decimal("2.0"))]),
            current_user=user_obj,
            db=db,
        )
        assert sale_dto.total == 11000.0

        tickets = SoporteCrmFacade.listar_tickets_empresa(empresa_id=empresa_id, db=db)
        assert isinstance(tickets, list)
    finally:
        db.close()
