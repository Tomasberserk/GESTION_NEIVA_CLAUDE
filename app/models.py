import uuid
import enum
from sqlalchemy import (
    Column, String, Numeric, Boolean, Date, Text,
    DateTime, ForeignKey, Enum as SAEnum, Index, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class RolUsuario(str, enum.Enum):
    ADMIN   = "admin"
    TENDERO = "tendero"


class PlanEmpresa(str, enum.Enum):
    BASIC   = "basic"
    MEDIUM  = "medium"
    PREMIUM = "premium"


class UnidadMedida(str, enum.Enum):
    UNIDAD = "unidad"
    GRAMO  = "gramo"
    LIBRA  = "libra"
    KILO   = "kilo"
    # ERP Distribuidora units — Sprint 7.8
    CAJA   = "caja"
    BULTO  = "bulto"
    KG     = "kg"
    LITRO  = "litro"
    METRO  = "metro"


class CategoriaProducto(str, enum.Enum):
    BEBIDAS   = "Bebidas"
    SNACKS    = "Snacks"
    ASEO      = "Aseo"
    LACTEOS   = "Lacteos"
    LIMPIEZA  = "Limpieza"
    PANADERIA = "Panaderia"


class EstadoTicket(str, enum.Enum):
    ABIERTO    = "abierto"
    RESPONDIDO = "respondido"
    CERRADO    = "cerrado"


class RemitenteRol(str, enum.Enum):
    SUPERADMIN = "superadmin"
    USUARIO    = "usuario"


# ERP Distribuidora enums — Sprint 7.8 (columns stored as String(50) for
# compatibility with existing compra_service string comparisons)
class MetodoPagoCompra(str, enum.Enum):
    EFECTIVO      = "EFECTIVO"
    CREDITO       = "CREDITO"
    TRANSFERENCIA = "TRANSFERENCIA"


class EstadoCompra(str, enum.Enum):
    PAGADA    = "PAGADA"
    PENDIENTE = "PENDIENTE"
    ANULADA   = "ANULADA"


class EstadoCuentaPorPagar(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    PAGADA    = "PAGADA"
    VENCIDA   = "VENCIDA"


class MetodoPagoAbono(str, enum.Enum):
    EFECTIVO      = "EFECTIVO"
    TRANSFERENCIA = "TRANSFERENCIA"
    CHEQUE        = "CHEQUE"


# ---------------------------------------------------------------------------
# AuditMixin
# ---------------------------------------------------------------------------

class AuditMixin:
    """created_at/updated_at/is_active inherited by all main tables."""
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    is_active = Column(Boolean, server_default="true", nullable=False)


# ---------------------------------------------------------------------------
# Empresa (raíz del árbol multi-tenant)
# ---------------------------------------------------------------------------

class Empresa(AuditMixin, Base):
    __tablename__ = "empresas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre_comercial = Column(String(150), nullable=False)
    nit_o_cedula = Column(String(50), unique=True, nullable=False)
    plan = Column(
        SAEnum(PlanEmpresa, name="planempresa", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        server_default="basic",
    )
    trial_expires_at = Column(DateTime(timezone=True), nullable=True)

    usuarios          = relationship("Usuario",        back_populates="empresa", cascade="all, delete-orphan")
    productos         = relationship("Producto",       back_populates="empresa", cascade="all, delete-orphan")
    ventas            = relationship("Venta",          back_populates="empresa", cascade="all, delete-orphan")
    soporte_tickets   = relationship("SoporteTicket",  back_populates="empresa", cascade="all, delete-orphan")
    proveedores       = relationship("Proveedor",      back_populates="empresa", cascade="all, delete-orphan")
    compras           = relationship("Compra",         back_populates="empresa", cascade="all, delete-orphan")
    cuentas_por_pagar = relationship("CuentaPorPagar", back_populates="empresa", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Empresa {self.nombre_comercial!r}>"


# ---------------------------------------------------------------------------
# Usuario
# ---------------------------------------------------------------------------

class Usuario(AuditMixin, Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    empresa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
    )
    rol = Column(
        SAEnum(RolUsuario, name="rolusuario", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=RolUsuario.TENDERO,
    )
    telefono_whatsapp = Column(String(20), nullable=True, unique=True)

    empresa = relationship("Empresa", back_populates="usuarios")
    compras = relationship("Compra", back_populates="usuario")

    __table_args__ = (
        Index("idx_usuarios_email", "email"),
    )

    def __repr__(self) -> str:
        return f"<Usuario {self.email!r} rol={self.rol}>"


# ---------------------------------------------------------------------------
# Producto
# ---------------------------------------------------------------------------

class Producto(AuditMixin, Base):
    __tablename__ = "productos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
    )
    nombre = Column(String, nullable=False)
    codigo_barras = Column(String(50), nullable=False)
    precio_costo = Column(Numeric(10, 2), server_default="0.00", nullable=False)
    precio_venta = Column(Numeric(10, 2), server_default="0.00", nullable=False)
    cantidad_actual = Column(Numeric(10, 3), server_default="0.000", nullable=False)
    unidad_medida = Column(
        SAEnum(UnidadMedida, name="unidadmedida", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        server_default="unidad",
    )
    fecha_vencimiento = Column(Date, nullable=True)
    categoria = Column(
        SAEnum(CategoriaProducto, name="categoriaproducto", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    foto_url = Column(String, nullable=True)

    empresa = relationship("Empresa", back_populates="productos")
    detalles_venta = relationship("DetalleVenta", back_populates="producto", passive_deletes=True)
    detalles_compra = relationship("DetalleCompra", back_populates="producto", passive_deletes=True)

    __table_args__ = (
        UniqueConstraint("empresa_id", "codigo_barras", name="uq_producto_empresa_barras"),
        Index("idx_productos_empresa", "empresa_id"),
    )

    def __repr__(self) -> str:
        return f"<Producto {self.nombre!r} stock={self.cantidad_actual}>"


# ---------------------------------------------------------------------------
# Venta
# ---------------------------------------------------------------------------

class Venta(AuditMixin, Base):
    __tablename__ = "ventas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
    )
    fecha_venta = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    total = Column(Numeric(10, 2), nullable=False, server_default="0.00")

    empresa  = relationship("Empresa", back_populates="ventas")
    detalles = relationship("DetalleVenta", back_populates="venta", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_ventas_empresa_fecha", "empresa_id", "fecha_venta"),
    )

    def __repr__(self) -> str:
        return f"<Venta id={self.id} total={self.total}>"


# ---------------------------------------------------------------------------
# DetalleVenta
# ---------------------------------------------------------------------------

class DetalleVenta(AuditMixin, Base):
    __tablename__ = "detalles_venta"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    venta_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ventas.id", ondelete="CASCADE"),
        nullable=False,
    )
    producto_id = Column(
        UUID(as_uuid=True),
        ForeignKey("productos.id", ondelete="RESTRICT"),
        nullable=False,
    )
    cantidad = Column(Numeric(10, 3), nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    venta    = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_venta")

    __table_args__ = (
        Index("idx_detalles_venta_venta_id", "venta_id"),
    )

    def __repr__(self) -> str:
        return f"<DetalleVenta venta={self.venta_id} producto={self.producto_id} qty={self.cantidad}>"


# ---------------------------------------------------------------------------
# SoporteTicket
# ---------------------------------------------------------------------------

class SoporteTicket(AuditMixin, Base):
    __tablename__ = "soporte_tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
    )
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False,
    )
    asunto = Column(String(150), nullable=False)
    estado = Column(
        SAEnum(EstadoTicket, name="estadoticket", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        server_default="abierto",
    )

    empresa  = relationship("Empresa", back_populates="soporte_tickets")
    usuario  = relationship("Usuario", foreign_keys=[usuario_id], viewonly=True)
    mensajes = relationship(
        "SoporteMensaje",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="SoporteMensaje.created_at",
    )

    __table_args__ = (
        Index("idx_soporte_tickets_empresa", "empresa_id"),
    )

    def __repr__(self) -> str:
        return f"<SoporteTicket {self.asunto!r} estado={self.estado}>"


# ---------------------------------------------------------------------------
# SoporteMensaje
# ---------------------------------------------------------------------------

class SoporteMensaje(Base):
    __tablename__ = "soporte_mensajes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(
        UUID(as_uuid=True),
        ForeignKey("soporte_tickets.id", ondelete="CASCADE"),
        nullable=False,
    )
    remitente_rol = Column(
        SAEnum(RemitenteRol, name="remitenterol", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    remitente_email = Column(String(255), nullable=False)
    mensaje = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    ticket = relationship("SoporteTicket", back_populates="mensajes")

    __table_args__ = (
        Index("idx_soporte_mensajes_ticket", "ticket_id"),
    )

    def __repr__(self) -> str:
        return f"<SoporteMensaje rol={self.remitente_rol!r}>"


# ---------------------------------------------------------------------------
# ERP Distribuidora — Sprint 7.8
# ---------------------------------------------------------------------------

class Proveedor(AuditMixin, Base):
    __tablename__ = "proveedores"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id      = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False)
    nit_o_cedula    = Column(String(50), nullable=False)
    razon_social    = Column(String(150), nullable=False)
    contacto_nombre = Column(String(100), nullable=True)
    telefono        = Column(String(50), nullable=True)
    email           = Column(String(255), nullable=True)
    direccion       = Column(String(255), nullable=True)

    empresa           = relationship("Empresa", back_populates="proveedores")
    compras           = relationship("Compra", back_populates="proveedor")
    cuentas_por_pagar = relationship("CuentaPorPagar", back_populates="proveedor")

    __table_args__ = (
        UniqueConstraint("empresa_id", "nit_o_cedula", name="uq_proveedor_empresa_nit"),
        Index("idx_proveedores_empresa", "empresa_id"),
        Index("idx_proveedores_razon_social", "razon_social"),
    )

    def __repr__(self) -> str:
        return f"<Proveedor {self.razon_social!r} NIT={self.nit_o_cedula}>"


class Compra(AuditMixin, Base):
    __tablename__ = "compras"

    id                = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id        = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False)
    proveedor_id      = Column(UUID(as_uuid=True), ForeignKey("proveedores.id", ondelete="RESTRICT"), nullable=False)
    usuario_id        = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    numero_factura    = Column(String(100), nullable=True)
    fecha_compra      = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metodo_pago       = Column(String(50), nullable=False, default="EFECTIVO")
    fecha_vencimiento = Column(DateTime(timezone=True), nullable=True)
    estado            = Column(String(50), nullable=False, default="PAGADA")
    total             = Column(Numeric(12, 2), server_default="0.00", nullable=False)

    empresa          = relationship("Empresa", back_populates="compras")
    proveedor        = relationship("Proveedor", back_populates="compras")
    usuario          = relationship("Usuario", back_populates="compras")
    detalles         = relationship("DetalleCompra", back_populates="compra", cascade="all, delete-orphan")
    cuenta_por_pagar = relationship("CuentaPorPagar", back_populates="compra", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_compras_empresa", "empresa_id"),
        Index("idx_compras_proveedor", "proveedor_id"),
        Index("idx_compras_fecha", "fecha_compra"),
        Index("idx_compras_estado", "estado"),
    )

    def __repr__(self) -> str:
        return f"<Compra id={self.id} total={self.total}>"


class DetalleCompra(AuditMixin, Base):
    __tablename__ = "detalle_compras"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    compra_id    = Column(UUID(as_uuid=True), ForeignKey("compras.id", ondelete="CASCADE"), nullable=False)
    producto_id  = Column(UUID(as_uuid=True), ForeignKey("productos.id", ondelete="RESTRICT"), nullable=False)
    cantidad     = Column(Numeric(10, 3), nullable=False)
    precio_costo = Column(Numeric(12, 2), nullable=False)
    subtotal     = Column(Numeric(12, 2), nullable=False)

    compra   = relationship("Compra", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_compra")

    __table_args__ = (
        Index("idx_detalle_compra_compra", "compra_id"),
        Index("idx_detalle_compra_producto", "producto_id"),
    )

    def __repr__(self) -> str:
        return f"<DetalleCompra compra={self.compra_id} producto={self.producto_id}>"


class CuentaPorPagar(AuditMixin, Base):
    __tablename__ = "cuentas_por_pagar"

    id                = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id        = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False)
    compra_id         = Column(UUID(as_uuid=True), ForeignKey("compras.id", ondelete="CASCADE"), nullable=False)
    proveedor_id      = Column(UUID(as_uuid=True), ForeignKey("proveedores.id", ondelete="RESTRICT"), nullable=False)
    monto_total       = Column(Numeric(12, 2), nullable=False)
    saldo_pendiente   = Column(Numeric(12, 2), nullable=False)
    fecha_vencimiento = Column(DateTime(timezone=True), nullable=False)
    estado            = Column(String(50), nullable=False, default="PENDIENTE")

    empresa   = relationship("Empresa", back_populates="cuentas_por_pagar")
    compra    = relationship("Compra", back_populates="cuenta_por_pagar")
    proveedor = relationship("Proveedor", back_populates="cuentas_por_pagar")
    abonos    = relationship("AbonoCuentaPorPagar", back_populates="cuenta_por_pagar", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_cuentas_pagar_empresa", "empresa_id"),
        Index("idx_cuentas_pagar_proveedor", "proveedor_id"),
        Index("idx_cuentas_pagar_estado", "estado"),
        Index("idx_cuentas_pagar_vencimiento", "fecha_vencimiento"),
    )

    def __repr__(self) -> str:
        return f"<CuentaPorPagar id={self.id} saldo={self.saldo_pendiente}>"


class AbonoCuentaPorPagar(AuditMixin, Base):
    __tablename__ = "abonos_cuentas_por_pagar"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cuenta_por_pagar_id = Column(UUID(as_uuid=True), ForeignKey("cuentas_por_pagar.id", ondelete="CASCADE"), nullable=False)
    monto               = Column(Numeric(12, 2), nullable=False)
    fecha_abono         = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metodo_pago         = Column(String(50), nullable=False, default="EFECTIVO")
    nota                = Column(String(500), nullable=True)

    cuenta_por_pagar = relationship("CuentaPorPagar", back_populates="abonos")

    __table_args__ = (
        Index("idx_abonos_cxp", "cuenta_por_pagar_id"),
        Index("idx_abonos_fecha", "fecha_abono"),
    )

    def __repr__(self) -> str:
        return f"<Abono id={self.id} monto={self.monto}>"
