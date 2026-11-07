"""Public facade for pos_ventas bounded context."""
from uuid import UUID
from sqlalchemy.orm import Session

from app import models
from app.pos_ventas.api.contracts import SaleSummaryDTO
from app.pos_ventas.internal import service as _internal_service
from app.schemas.venta import VentaCrear


class VentasFacade:
    """Public entry point for POS sales operations."""

    @staticmethod
    def registrar_venta_atomica(
        empresa_id: UUID,
        data: VentaCrear,
        current_user: models.Usuario,
        db: Session,
        commit: bool = True,
    ) -> SaleSummaryDTO:
        """Execute an atomic POS checkout transaction."""
        return _internal_service.execute_checkout(
            empresa_id=empresa_id,
            data=data,
            current_user=current_user,
            db=db,
            commit=commit,
        )
