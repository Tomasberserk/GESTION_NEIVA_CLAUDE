from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, field_validator

UNIDADES = Literal["unidad", "gramo", "libra", "kilo"]


class ProductoCrear(BaseModel):
    nombre: str
    codigo_barras: str
    precio_costo: Decimal = Decimal("0.00")
    precio_venta: Decimal = Decimal("0.00")
    cantidad_actual: Decimal = Decimal("0.000")
    unidad_medida: UNIDADES = "unidad"
    fecha_vencimiento: Optional[date] = None
    empresa_id: UUID

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

    @field_validator("precio_costo", "precio_venta")
    @classmethod
    def precio_no_negativo(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("El precio no puede ser negativo")
        return v

    @field_validator("cantidad_actual")
    @classmethod
    def stock_no_negativo(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("El stock inicial no puede ser negativo")
        return v


class ProductoActualizar(BaseModel):
    """Todos los campos son opcionales: solo se actualizan los enviados."""
    nombre: Optional[str] = None
    codigo_barras: Optional[str] = None
    precio_costo: Optional[Decimal] = None
    precio_venta: Optional[Decimal] = None
    cantidad_actual: Optional[Decimal] = None
    unidad_medida: Optional[UNIDADES] = None
    fecha_vencimiento: Optional[date] = None
    foto_url: Optional[str] = None

    @field_validator("precio_costo", "precio_venta")
    @classmethod
    def precio_no_negativo(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("El precio no puede ser negativo")
        return v

    @field_validator("cantidad_actual")
    @classmethod
    def stock_no_negativo(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("El stock no puede ser negativo")
        return v


class ProductoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    nombre: str
    codigo_barras: str
    precio_costo: float
    precio_venta: float
    cantidad_actual: float
    unidad_medida: str
    fecha_vencimiento: Optional[date]
    foto_url: Optional[str]
    created_at: datetime
    is_active: bool


class InventarioRespuesta(BaseModel):
    """Respuesta de GET /productos/{empresa_id}"""
    tienda: str
    total_items: int
    inventario: List[ProductoRespuesta]
