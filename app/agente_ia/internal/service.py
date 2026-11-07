"""Internal orchestrator bridge for agente_ia."""
from sqlalchemy.orm import Session

from app import models
from app.services.agente.agent_orchestrator import AgentOrchestrator

_orchestrator = AgentOrchestrator()


async def process_turn(
    mensaje: str,
    current_user: models.Usuario,
    db: Session,
    conversation_id: str | None = None,
) -> dict:
    """Delegate natural-language turn processing to AgentOrchestrator."""
    return await _orchestrator.procesar_mensaje(
        mensaje=mensaje,
        current_user=current_user,
        db=db,
        conversation_id=conversation_id,
    )
