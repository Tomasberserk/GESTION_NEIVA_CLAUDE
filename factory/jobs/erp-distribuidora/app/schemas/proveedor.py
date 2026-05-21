from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class ProveedorCrear(BaseModel):
    nit_o_cedula: str
    razon_social: str
    contacto_nombre: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None

    @field_validator("nit_o_cedula")
    @classmethod
    def nit_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El NIT o cédula no puede estar vacío")
        return v

    @field_validator("razon_social")
    @classmethod
    def razon_no_vacia(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("La razón social no puede estar vacía")
        return v


class ProveedorActualizar(BaseModel):
    nit_o_cedula: Optional[str] = None
    razon_social: Optional[str] = None
    contacto_nombre: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None


class ProveedorRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    nit_o_cedula: str
    razon_social: str
    contacto_nombre: Optional[str]
    telefono: Optional[str]
    email: Optional[str]
    direccion: Optional[str]
    created_at: datetime
    is_active: bool
