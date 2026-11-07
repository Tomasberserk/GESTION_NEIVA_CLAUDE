"""Public facade for agente_ia bounded context."""
from sqlalchemy.orm import Session

from app import models
from app.agente_ia.internal import service as _internal_service


class AgenteIaFacade:
    """Public entry point for conversational AI agent interactions."""

    @staticmethod
    async def procesar_turno(
        mensaje: str,
        current_user: models.Usuario,
        db: Session,
        conversation_id: str | None = None,
    ) -> dict:
        """Execute a conversational turn in the AI agent state machine."""
        return await _internal_service.process_turn(
            mensaje=mensaje,
            current_user=current_user,
            db=db,
            conversation_id=conversation_id,
        )
