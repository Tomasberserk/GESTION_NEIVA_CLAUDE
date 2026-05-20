from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, field_validator

UNIDADES: type = Literal["unidad", "paquete"]
CATEGORIAS: type = Literal[
    "Utiles escolares",
    "Papel y resmas",
    "Tecnologia",
    "Servicios",
    "Miscelanea",
]


class ProductoCrear(BaseModel):
    nombre: str
    codigo_barras: str
    precio_costo: Decimal = Decimal("0.00")
    precio_venta: Decimal = Decimal("0.00")
    cantidad_actual: int = 0
    unidad_medida: UNIDADES = "unidad"
    categoria: CATEGORIAS
    stock_minimo: int = 5
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

    @field_validator("precio_costo", "precio_venta")
    @classmethod
    def precio_no_negativo(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("El precio no puede ser negativo")
        return v

    @field_validator("cantidad_actual", "stock_minimo")
    @classmethod
    def entero_no_negativo(cls, v: int) -> int:
        if v < 0:
            raise ValueError("El valor no puede ser negativo")
        return v


class ProductoActualizar(BaseModel):
    """Todos los campos son opcionales: solo se actualizan los enviados."""
    nombre: Optional[str] = None
    codigo_barras: Optional[str] = None
    precio_costo: Optional[Decimal] = None
    precio_venta: Optional[Decimal] = None
    cantidad_actual: Optional[int] = None
    unidad_medida: Optional[UNIDADES] = None
    categoria: Optional[CATEGORIAS] = None
    stock_minimo: Optional[int] = None
    foto_url: Optional[str] = None

    @field_validator("precio_costo", "precio_venta")
    @classmethod
    def precio_no_negativo(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("El precio no puede ser negativo")
        return v

    @field_validator("cantidad_actual", "stock_minimo")
    @classmethod
    def entero_no_negativo(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("El valor no puede ser negativo")
        return v


class ProductoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    nombre: str
    codigo_barras: str
    precio_costo: float
    precio_venta: float
    cantidad_actual: int
    unidad_medida: str
    categoria: str
    stock_minimo: int
    foto_url: Optional[str]
    created_at: datetime
    is_active: bool


class InventarioRespuesta(BaseModel):
    tienda: str
    total_items: int
    inventario: List[ProductoRespuesta]
