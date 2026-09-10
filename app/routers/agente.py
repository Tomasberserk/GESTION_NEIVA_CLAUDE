"""Router HTTP para el Agente Inteligente de Gestión Neiva.

Expone el endpoint delgado POST /api/agente/mensaje que delega toda la lógica
al AgentOrchestrator, validando la identidad del usuario y empresa mediante JWT.
"""

import os
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
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


@router.post(
    "/transcribir-audio",
    status_code=status.HTTP_200_OK,
    summary="Transcribir fragmento de audio (fallback para navegadores móviles)",
)
async def transcribir_audio(
    audio: UploadFile = File(...),
    current_user: models.Usuario = Depends(get_current_user),
):
    """Fallback STT: recibe audio en formato Opus/WebM y devuelve el texto transcrito."""
    audio_bytes = await audio.read()
    if not audio_bytes or len(audio_bytes) < 100:
        return {"texto": ""}

    # 1. Intentar con Groq Whisper (ultra-rápido ~150ms)
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            transcription = client.audio.transcriptions.create(
                file=(audio.filename or "voz.webm", audio_bytes),
                model="whisper-large-v3",
                language="es",
            )
            return {"texto": transcription.text.strip()}
        except Exception as exc:
            pass

    # 2. Fallback con Google Gemini
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=google_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content([
                "Transcribe de forma literal y exacta en español este audio de un tendero colombiano. Devuelve ÚNICAMENTE el texto transcrito, sin explicaciones ni comillas.",
                {"mime_type": audio.content_type or "audio/webm", "data": audio_bytes},
            ])
            return {"texto": (response.text or "").strip()}
        except Exception as exc:
            pass

    return {"texto": ""}
