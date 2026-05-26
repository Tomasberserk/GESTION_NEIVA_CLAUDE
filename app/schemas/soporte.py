# app/schemas/soporte.py
from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MensajeOut(BaseModel):
    id: UUID
    remitente_rol: str
    remitente_email: str
    mensaje: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TicketCrear(BaseModel):
    asunto: str
    mensaje: str


class TicketResponder(BaseModel):
    mensaje: str


class TicketListOut(BaseModel):
    id: UUID
    asunto: str
    estado: str
    created_at: datetime
    updated_at: datetime
    empresa_id: UUID

    model_config = {"from_attributes": True}


class TicketOut(TicketListOut):
    mensajes: list[MensajeOut] = []


class EmpresaAdminOut(BaseModel):
    id: UUID
    nombre_comercial: str
    nit_o_cedula: str
    plan: str
    is_active: bool
    trial_expires_at: Optional[datetime]
    total_usuarios: int

    model_config = {"from_attributes": True}


class ActualizarTrial(BaseModel):
    trial_expires_at: datetime


class ActualizarEstado(BaseModel):
    is_active: bool
