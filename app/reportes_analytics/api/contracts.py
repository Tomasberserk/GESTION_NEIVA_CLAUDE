"""Immutable DTO contracts exposed by reportes_analytics."""
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DailyMetricsDTO:
    """Consolidated daily financial metrics for a tenant store."""

    empresa_id: UUID
    ventas_hoy: int
    ingresos_hoy: float
