from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class EmpresaCrear(BaseModel):
    nombre_comercial: str
    nit_o_cedula: str

    @field_validator("nombre_comercial")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre comercial no puede estar vacío")
        return v

    @field_validator("nit_o_cedula")
    @classmethod
    def nit_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El NIT/Cédula no puede estar vacío")
        return v


class EmpresaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nombre_comercial: str
    nit_o_cedula: str
    created_at: datetime
    is_active: bool
