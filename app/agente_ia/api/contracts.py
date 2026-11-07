"""Immutable DTO contracts exposed by agente_ia."""
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AgentTurnResponseDTO:
    """Immutable response contract for a conversational agent turn."""

    conversation_id: str
    estado: str
    respuesta: str
    datos: dict[str, Any] | None = None
