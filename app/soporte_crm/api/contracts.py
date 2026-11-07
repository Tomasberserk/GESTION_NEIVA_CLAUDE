"""Immutable DTO contracts exposed by soporte_crm."""
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class TicketSummaryDTO:
    """Immutable summary of a customer support ticket."""

    id: UUID
    empresa_id: UUID
    asunto: str
    estado: str
