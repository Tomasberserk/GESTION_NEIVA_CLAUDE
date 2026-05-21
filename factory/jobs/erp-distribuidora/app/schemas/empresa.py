from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class EmpresaCrear(BaseModel):
    nombre_comercial: str
    nit_o_cedula: str
    plan: str = "medium"


class EmpresaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nombre_comercial: str
    nit_o_cedula: str
    plan: str
    created_at: datetime
    is_active: bool
