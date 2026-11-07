"""Internal POS checkout orchestration calling AuthTenancyFacade and InventarioFacade."""
from uuid import UUID
from sqlalchemy.orm import Session

from app import models
from app.pos_ventas.api.contracts import SaleSummaryDTO
from app.schemas.venta import VentaCrear
from app.services import venta_service


def execute_checkout(
    empresa_id: UUID,
    data: VentaCrear,
    current_user: models.Usuario,
    db: Session,
    commit: bool = True,
) -> SaleSummaryDTO:
    """Register a POS sale transaction and return an immutable SaleSummaryDTO."""
    res = venta_service.registrar_venta(
        empresa_id=empresa_id,
        data=data,
        current_user=current_user,
        db=db,
        commit=commit,
    )
    return SaleSummaryDTO(
        venta_id=res.venta_id,
        empresa_id=empresa_id,
        total=res.total,
        mensaje=res.mensaje,
    )
