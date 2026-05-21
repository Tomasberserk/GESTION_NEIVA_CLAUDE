from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ProveedorMinimo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    razon_social: str
    telefono: Optional[str] = None


class CuentaPorPagarRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    compra_id: UUID
    monto_total: Decimal
    saldo_pendiente: Decimal
    fecha_vencimiento: datetime
    estado: str
    proveedor: ProveedorMinimo
    dias_para_vencimiento: Optional[int] = None
