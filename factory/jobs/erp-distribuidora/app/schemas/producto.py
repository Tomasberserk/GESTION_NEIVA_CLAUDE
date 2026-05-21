from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_validator


class ProductoCrear(BaseModel):
    nombre: str
    codigo_barras: str
    precio_costo: Decimal = Decimal("0.00")
    precio_venta: Decimal = Decimal("0.00")
    cantidad_actual: Decimal = Decimal("0.000")
    unidad_medida: str = "UNIDAD"
    categoria: Optional[str] = None
    empresa_id: Optional[UUID] = None

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre del producto no puede estar vacío")
        return v

    @field_validator("codigo_barras")
    @classmethod
    def codigo_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El código de barras no puede estar vacío")
        return v

    @field_validator("precio_costo", "precio_venta", "cantidad_actual")
    @classmethod
    def no_negativo(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("El valor no puede ser negativo")
        return v


class ProductoActualizar(BaseModel):
    nombre: Optional[str] = None
    codigo_barras: Optional[str] = None
    precio_costo: Optional[Decimal] = None
    precio_venta: Optional[Decimal] = None
    cantidad_actual: Optional[Decimal] = None
    unidad_medida: Optional[str] = None
    categoria: Optional[str] = None
    foto_url: Optional[str] = None

    @field_validator("precio_costo", "precio_venta", "cantidad_actual")
    @classmethod
    def no_negativo(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("El valor no puede ser negativo")
        return v


class ProductoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    nombre: str
    codigo_barras: str
    precio_costo: Decimal
    precio_venta: Decimal
    cantidad_actual: Decimal
    unidad_medida: str
    categoria: Optional[str]
    foto_url: Optional[str]
    created_at: datetime
    is_active: bool
