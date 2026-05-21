from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


class AbonoCrear(BaseModel):
    monto: Decimal
    metodo_pago: str = "EFECTIVO"
    nota: Optional[str] = None

    @field_validator("monto")
    @classmethod
    def monto_mayor_que_cero(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("El monto del abono debe ser mayor que cero")
        return v

    @field_validator("metodo_pago")
    @classmethod
    def metodo_pago_valido(cls, v: str) -> str:
        v = v.upper()
        if v not in ["EFECTIVO", "TRANSFERENCIA", "CHEQUE"]:
            raise ValueError("El método de pago del abono debe ser EFECTIVO, TRANSFERENCIA o CHEQUE")
        return v


class AbonoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    cuenta_por_pagar_id: UUID
    monto: Decimal
    fecha_abono: datetime
    metodo_pago: str
    nota: Optional[str]
