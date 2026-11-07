"""Public API for inventario module."""
from app.inventario.api.contracts import StockDeductionResultDTO
from app.inventario.api.facade import InventarioFacade

__all__ = ["InventarioFacade", "StockDeductionResultDTO"]
