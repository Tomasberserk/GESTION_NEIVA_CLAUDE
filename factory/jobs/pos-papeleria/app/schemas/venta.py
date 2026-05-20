from uuid import UUID
from datetime import datetime
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
    # "items" según api-contracts.md (OBS-02: diferente a "detalles" de Gestión Neiva)
    items: List[DetalleVentaCrear]

    @field_validator("items")
    @classmethod
    def carrito_no_vacio(cls, v: List[DetalleVentaCrear]) -> List[DetalleVentaCrear]:
        if not v:
            raise ValueError("El carrito no puede estar vacío")
        return v


class DetalleVentaRespuesta(BaseModel):
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
        if not isinstance(data, dict):
            return {
                "id": data.id,
                "producto_id": data.producto_id,
                "cantidad": data.cantidad,
                "precio_unitario": float(data.precio_unitario),
                "subtotal": float(data.subtotal),
                "producto_nombre": data.producto.nombre if data.producto else "",
            }
        return data


class VentaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    usuario_id: UUID
    usuario_email: str
    fecha_venta: datetime
    total: float
    detalles: List[DetalleVentaRespuesta]

    @model_validator(mode="before")
    @classmethod
    def _extraer_usuario_email(cls, data):
        if not isinstance(data, dict):
            return {
                "id": data.id,
                "empresa_id": data.empresa_id,
                "usuario_id": data.usuario_id,
                "usuario_email": data.usuario.email if data.usuario else "",
                "fecha_venta": data.fecha_venta,
                "total": float(data.total),
                "detalles": data.detalles,
            }
        return data


class VentaResumen(BaseModel):
    """Respuesta inmediata tras registrar una venta."""
    mensaje: str
    total: float
    venta_id: UUID
