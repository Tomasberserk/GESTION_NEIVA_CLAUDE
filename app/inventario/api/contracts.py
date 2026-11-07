"""Immutable DTO contracts exposed by inventario."""
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class StockDeductionResultDTO:
    """Snapshot returned after locking and deducting product inventory."""

    producto_id: UUID
    nombre: str
    precio_unitario: Decimal
    cantidad_descontada: Decimal
    subtotal: Decimal
    stock_restante: Decimal
