"""Public facade for soporte_crm bounded context."""
from uuid import UUID
from sqlalchemy.orm import Session

from app.soporte_crm.api.contracts import TicketSummaryDTO
from app.soporte_crm.internal import service as _internal_service


class SoporteCrmFacade:
    """Public entry point for customer support operations."""

    @staticmethod
    def listar_tickets_empresa(empresa_id: UUID, db: Session) -> list[TicketSummaryDTO]:
        """Return active ticket summaries for the specified tenant."""
        return _internal_service.list_active_tickets_for_company(empresa_id=empresa_id, db=db)
