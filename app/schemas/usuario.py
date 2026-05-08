from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.models import RolUsuario


class UsuarioCrear(BaseModel):
    email: EmailStr
    password: str
    empresa_id: UUID
    rol: RolUsuario = RolUsuario.TENDERO

    @field_validator("password")
    @classmethod
    def password_minimo(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v


class UsuarioRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    empresa_id: UUID
    rol: RolUsuario
    created_at: datetime
    is_active: bool


class UsuarioCrearConEmpresa(BaseModel):
    """Schema para registro atómico de empresa + usuario en un solo endpoint."""
    nombre_comercial: str
    nit_o_cedula: str
    email: EmailStr
    password: str
    rol: RolUsuario = RolUsuario.ADMIN

    @field_validator("nombre_comercial")
    @classmethod
    def nombre_empresa_valido(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre comercial no puede estar vacío")
        if len(v) > 150:
            raise ValueError("El nombre comercial no puede exceder 150 caracteres")
        return v

    @field_validator("nit_o_cedula")
    @classmethod
    def nit_valido(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El NIT/Cédula no puede estar vacío")
        if len(v) > 50:
            raise ValueError("El NIT/Cédula no puede exceder 50 caracteres")
        return v

    @field_validator("password")
    @classmethod
    def password_minimo(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v


class LoginForm(BaseModel):
    email: EmailStr
    password: str


class TokenRespuesta(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioRespuesta
