"""Public facade for reportes_analytics bounded context."""
from uuid import UUID

from app.reportes_analytics.api.contracts import DailyMetricsDTO
from app.reportes_analytics.internal import service as _internal_service


class ReportesFacade:
    """Public entry point for financial analytics and reporting projections."""

    @staticmethod
    def construir_resumen_diario(
        empresa_id: UUID,
        ventas_hoy: int,
        ingresos_hoy: float,
    ) -> DailyMetricsDTO:
        """Return an immutable DailyMetricsDTO snapshot."""
        return _internal_service.get_daily_summary(
            empresa_id=empresa_id,
            ventas_hoy=ventas_hoy,
            ingresos_hoy=ingresos_hoy,
        )
