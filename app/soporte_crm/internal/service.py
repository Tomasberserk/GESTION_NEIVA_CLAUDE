"""Internal support ticket operations."""
from uuid import UUID
from sqlalchemy.orm import Session

from app import models
from app.soporte_crm.api.contracts import TicketSummaryDTO


def list_active_tickets_for_company(empresa_id: UUID, db: Session) -> list[TicketSummaryDTO]:
    """Return active support tickets for a given company."""
    rows = (
        db.query(models.SoporteTicket)
        .filter(
            models.SoporteTicket.empresa_id == empresa_id,
            models.SoporteTicket.is_active.is_(True),
        )
        .all()
    )
    return [
        TicketSummaryDTO(
            id=row.id,
            empresa_id=row.empresa_id,
            asunto=row.asunto,
            estado=row.estado.value if hasattr(row.estado, "value") else str(row.estado),
        )
        for row in rows
    ]
