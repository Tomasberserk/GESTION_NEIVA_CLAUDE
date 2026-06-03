from uuid import UUID
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator, computed_field


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
    plan: str
    trial_expires_at: Optional[datetime] = None
    created_at: datetime
    is_active: bool
    factory_upgrade_solicitado: bool = False
    factory_url: Optional[str] = None
    factory_trial_expires_at: Optional[datetime] = None

    @computed_field
    @property
    def dias_trial_restantes(self) -> int | None:
        if self.trial_expires_at is None:
            return None
        delta = self.trial_expires_at - datetime.now(timezone.utc)
        return max(0, delta.days)

    @computed_field
    @property
    def factory_activa(self) -> bool:
        if not self.factory_url:
            return False
        if self.factory_trial_expires_at is None:
            return True
        exp = self.factory_trial_expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        return exp > datetime.now(timezone.utc)
