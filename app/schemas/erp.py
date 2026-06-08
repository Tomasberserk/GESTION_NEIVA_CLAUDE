from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


# ── Proveedor ──────────────────────────────────────────────────────────────────

class ProveedorCrear(BaseModel):
    nit_o_cedula: str
    razon_social: str
    contacto_nombre: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None

    @field_validator("nit_o_cedula")
    @classmethod
    def nit_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El NIT o cédula no puede estar vacío")
        return v

    @field_validator("razon_social")
    @classmethod
    def razon_no_vacia(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("La razón social no puede estar vacía")
        return v


class ProveedorActualizar(BaseModel):
    nit_o_cedula: Optional[str] = None
    razon_social: Optional[str] = None
    contacto_nombre: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None


class ProveedorRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    nit_o_cedula: str
    razon_social: str
    contacto_nombre: Optional[str]
    telefono: Optional[str]
    email: Optional[str]
    direccion: Optional[str]
    created_at: datetime
    is_active: bool


# ── Compra ─────────────────────────────────────────────────────────────────────

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
    nombre: Optional[str] = None
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


# ── Cuenta por Pagar ───────────────────────────────────────────────────────────

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


# ── Abono ──────────────────────────────────────────────────────────────────────

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
