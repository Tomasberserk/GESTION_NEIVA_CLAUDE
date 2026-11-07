"""Internal read projections for reportes_analytics."""
from uuid import UUID
from sqlalchemy.orm import Session

from app.pos_ventas.api.facade import VentasFacade
from app.reportes_analytics.api.contracts import DailyMetricsDTO


def get_daily_summary(empresa_id: UUID, ventas_hoy: int, ingresos_hoy: float) -> DailyMetricsDTO:
    """Build an immutable daily summary projection DTO."""
    _ = VentasFacade
    return DailyMetricsDTO(
        empresa_id=empresa_id,
        ventas_hoy=ventas_hoy,
        ingresos_hoy=ingresos_hoy,
    )
