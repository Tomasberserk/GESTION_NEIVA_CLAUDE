"""Immutable DTO contracts exposed by pos_ventas."""
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SaleSummaryDTO:
    """Immutable summary of a completed POS sale transaction."""

    venta_id: UUID
    empresa_id: UUID
    total: float
    mensaje: str
