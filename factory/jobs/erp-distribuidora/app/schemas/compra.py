from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_validator


class DetalleCompraCrear(BaseModel):
    producto_id: UUID
    cantidad: Decimal
    precio_costo: Decimal

    @field_validator("cantidad", "precio_costo")
    @classmethod
    def mayor_que_cero(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("La cantidad y el precio de costo deben ser mayores que cero")
        return v


class CompraCrear(BaseModel):
    proveedor_id: UUID
    numero_factura: Optional[str] = None
    metodo_pago: str = "EFECTIVO"
    fecha_vencimiento: Optional[datetime] = None
    items: List[DetalleCompraCrear]

    @field_validator("items")
    @classmethod
    def items_no_vacio(cls, v: List[DetalleCompraCrear]) -> List[DetalleCompraCrear]:
        if not v:
            raise ValueError("La compra debe incluir al menos un producto")
        return v

    @field_validator("metodo_pago")
    @classmethod
    def metodo_pago_valido(cls, v: str) -> str:
        v = v.upper()
        if v not in ["EFECTIVO", "CREDITO", "TRANSFERENCIA"]:
            raise ValueError("El método de pago debe ser EFECTIVO, CREDITO o TRANSFERENCIA")
        return v


class DetalleCompraRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    producto_id: UUID
    nombre: Optional[str] = None  # Se llenará en servicio con el nombre del producto
    cantidad: Decimal
    precio_costo: Decimal
    subtotal: Decimal


class CompraRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    numero_factura: Optional[str]
    fecha_compra: datetime
    metodo_pago: str
    fecha_vencimiento: Optional[datetime]
    estado: str
    total: Decimal
    detalles: List[DetalleCompraRespuesta]
    cuenta_por_pagar_id: Optional[UUID] = None
