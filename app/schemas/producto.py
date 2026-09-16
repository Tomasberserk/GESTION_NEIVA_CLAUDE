from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, field_validator

UNIDADES    = Literal["unidad", "gramo", "libra", "kilo", "caja", "bulto", "kg", "litro", "metro"]
CATEGORIAS  = Literal["Bebidas", "Snacks", "Aseo", "Lacteos", "Limpieza", "Panaderia"]


class ProductoCrear(BaseModel):
    nombre: str
    codigo_barras: str
    precio_costo: Decimal = Decimal("0.00")
    precio_venta: Decimal = Decimal("0.00")
    cantidad_actual: Decimal = Decimal("0.000")
    unidad_medida: UNIDADES = "unidad"
    fecha_vencimiento: Optional[date] = None
    categoria: Optional[CATEGORIAS] = None
    empresa_id: Optional[UUID] = None  # Inyectado por el router desde JWT

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
    categoria: Optional[CATEGORIAS] = None
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


class ProductoBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    nombre: str
    codigo_barras: str
    precio_venta: float
    cantidad_actual: float
    unidad_medida: str
    fecha_vencimiento: Optional[date]
    categoria: Optional[str]
    foto_url: Optional[str]
    created_at: datetime
    is_active: bool


class ProductoAdminOut(ProductoBase):
    """Schema para administradores: incluye precio de costo y margen."""
    precio_costo: float


class ProductoCajeroOut(ProductoBase):
    """Schema estricto para cajeros/vendedores: CERO exposicion de precio_costo."""
    pass


# Retrocompatibilidad para imports existentes
ProductoRespuesta = ProductoAdminOut


class InventarioAdminRespuesta(BaseModel):
    """Respuesta para administradores con costos."""
    tienda: str
    total_items: int
    inventario: List[ProductoAdminOut]


class InventarioCajeroRespuesta(BaseModel):
    """Respuesta para cajeros/vendedores sin costos."""
    tienda: str
    total_items: int
    inventario: List[ProductoCajeroOut]


InventarioRespuesta = InventarioAdminRespuesta
