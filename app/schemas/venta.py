from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import List
from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class DetalleVentaCrear(BaseModel):
    producto_id: UUID
    cantidad: int

    @field_validator("cantidad")
    @classmethod
    def cantidad_positiva(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        return v


class VentaCrear(BaseModel):
    detalles: List[DetalleVentaCrear]

    @field_validator("detalles")
    @classmethod
    def carrito_no_vacio(cls, v: List[DetalleVentaCrear]) -> List[DetalleVentaCrear]:
        if not v:
            raise ValueError("El carrito no puede estar vacío")
        return v


class DetalleVentaRespuesta(BaseModel):
    """
    producto_nombre se extrae del objeto ORM via model_validator.
    El service debe hacer joinedload(DetalleVenta.producto) antes
    de serializar para que este campo esté disponible.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    producto_id: UUID
    cantidad: int
    precio_unitario: float
    subtotal: float
    producto_nombre: str

    @model_validator(mode="before")
    @classmethod
    def _extraer_producto_nombre(cls, data):
        # Si viene directo del ORM (no es dict), extraemos producto.nombre
        if not isinstance(data, dict):
            return {
                "id": data.id,
                "producto_id": data.producto_id,
                "cantidad": data.cantidad,
                "precio_unitario": float(data.precio_unitario),
                "subtotal": float(data.subtotal),
                "producto_nombre": (
                    data.producto.nombre if data.producto else ""
                ),
            }
        return data


class VentaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    fecha_venta: datetime
    total: float
    detalles: List[DetalleVentaRespuesta]


class VentaResumen(BaseModel):
    """Respuesta inmediata después de registrar una venta."""
    mensaje: str
    total: float
    venta_id: UUID
