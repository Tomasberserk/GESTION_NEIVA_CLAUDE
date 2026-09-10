"""Router HTTP para el Agente Inteligente de Gestión Neiva.

Expone el endpoint delgado POST /api/agente/mensaje que delega toda la lógica
al AgentOrchestrator, validando la identidad del usuario y empresa mediante JWT.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.dependencies import get_current_user
from app.services.agente.agent_orchestrator import AgentOrchestrator
from app.services.agente.session_store import SessionStoreUnavailableError

router = APIRouter(prefix="/agente", tags=["Agente IA"])

# Instancia reutilizable del orquestador
_orchestrator = AgentOrchestrator()


class MensajeAgenteEntrada(BaseModel):
    mensaje: str = Field(..., min_length=1, description="Texto o comando del usuario")
    conversation_id: str | None = Field(None, description="ID de conversación opcional para contexto continuo")


class MensajeAgenteRespuesta(BaseModel):
    conversation_id: str
    estado: str
    respuesta: str
    datos: dict[str, Any] | None = None
    clarification: dict[str, Any] | None = None
    command_id: str | None = None
    preview: dict[str, Any] | None = None
    resultado: dict[str, Any] | None = None
    idempotente: bool = False


@router.post(
    "/mensaje",
    response_model=MensajeAgenteRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Enviar mensaje al Agente Inteligente",
)
async def enviar_mensaje(
    payload: MensajeAgenteEntrada,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """Procesa un comando en lenguaje natural, manteniendo sesión y FSM."""
    try:
        resultado = await _orchestrator.procesar_mensaje(
            mensaje=payload.mensaje,
            current_user=current_user,
            db=db,
            conversation_id=payload.conversation_id,
        )
        return resultado
    except SessionStoreUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio de sesiones del agente está temporalmente no disponible. Intente de nuevo en unos segundos.",
        ) from exc
