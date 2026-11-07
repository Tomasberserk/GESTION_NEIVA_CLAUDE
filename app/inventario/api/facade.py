"""Public facade for inventario bounded context."""
from decimal import Decimal
from uuid import UUID
from sqlalchemy.orm import Session

from app.inventario.api.contracts import StockDeductionResultDTO
from app.inventario.internal import service as _internal_service


class InventarioFacade:
    """Public entry point for cross-module inventory operations."""

    @staticmethod
    def validar_y_descontar_stock_atomic(
        empresa_id: UUID,
        producto_id: UUID,
        cantidad: Decimal,
        db: Session,
    ) -> StockDeductionResultDTO:
        """Lock product row (SELECT FOR UPDATE), validate stock, and deduct quantity."""
        return _internal_service.lock_and_deduct_stock(
            empresa_id=empresa_id,
            producto_id=producto_id,
            cantidad=cantidad,
            db=db,
        )
