"""Public API for soporte_crm module."""
from app.soporte_crm.api.contracts import TicketSummaryDTO
from app.soporte_crm.api.facade import SoporteCrmFacade

__all__ = ["SoporteCrmFacade", "TicketSummaryDTO"]
