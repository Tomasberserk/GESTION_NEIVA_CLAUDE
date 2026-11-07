"""Public API for pos_ventas module."""
from app.pos_ventas.api.contracts import SaleSummaryDTO
from app.pos_ventas.api.facade import VentasFacade

__all__ = ["SaleSummaryDTO", "VentasFacade"]
