import uuid
import enum
from sqlalchemy import (
    Column, String, Integer, Numeric, Boolean, Date, Text,
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
    ADMIN = "admin"
    TENDERO = "tendero"


class PlanEmpresa(str, enum.Enum):
    BASIC = "basic"
    MEDIUM = "medium"
    PREMIUM = "premium"


class UnidadMedida(str, enum.Enum):
    UNIDAD = "unidad"
    GRAMO = "gramo"
    LIBRA = "libra"
    KILO = "kilo"


class CategoriaProducto(str, enum.Enum):
    BEBIDAS   = "Bebidas"
    SNACKS    = "Snacks"
    ASEO      = "Aseo"
    LACTEOS   = "Lacteos"
    LIMPIEZA  = "Limpieza"
    PANADERIA = "Panaderia"


class EstadoTicket(str, enum.Enum):
    ABIERTO = "abierto"
    RESPONDIDO = "respondido"
    CERRADO = "cerrado"


# ---------------------------------------------------------------------------
# AuditMixin
# ---------------------------------------------------------------------------

class AuditMixin:
    """
    Campos de auditoría heredados por todas las tablas principales.

    - created_at  : timestamp de inserción, asignado por el servidor de BD.
    - updated_at  : timestamp de última modificación. El ORM lo actualiza
                    vía onupdate; el trigger de BD lo mantiene para updates
                    que no pasen por el ORM.
    - is_active   : flag para Soft Delete. Nunca se borra físicamente un
                    registro: se pone is_active=False.
    """
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),  # ORM-level; el trigger cubre updates directos en BD
        nullable=False,
    )
    is_active = Column(
        Boolean,
        server_default="true",
        nullable=False,
    )


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

    # Relaciones (cascade: si se borra la empresa, se borran sus hijos)
    usuarios = relationship(
        "Usuario",
        back_populates="empresa",
        cascade="all, delete-orphan",
    )
    productos = relationship(
        "Producto",
        back_populates="empresa",
        cascade="all, delete-orphan",
    )
    ventas = relationship(
        "Venta",
        back_populates="empresa",
        cascade="all, delete-orphan",
    )
    soporte_tickets = relationship(
        "SoporteTicket",
        back_populates="empresa",
        cascade="all, delete-orphan",
    )

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

    empresa = relationship("Empresa", back_populates="usuarios")

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
    detalles_venta = relationship(
        "DetalleVenta",
        back_populates="producto",
        passive_deletes=True,
    )

    __table_args__ = (
        UniqueConstraint("empresa_id", "codigo_barras", name="uq_producto_empresa_barras"),
        Index("idx_productos_empresa", "empresa_id"),
    )

    def __repr__(self) -> str:
        return f"<Producto {self.nombre!r} stock={self.cantidad_actual}>"


# ---------------------------------------------------------------------------
# Venta (documento maestro de transacción POS)
# ---------------------------------------------------------------------------

class Venta(AuditMixin, Base):
    __tablename__ = "ventas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
    )
    # fecha_venta es el momento de negocio de la venta (puede diferir de
    # created_at en escenarios de venta offline o corrección manual)
    fecha_venta = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    total = Column(Numeric(10, 2), nullable=False, server_default="0.00")

    empresa = relationship("Empresa", back_populates="ventas")
    detalles = relationship(
        "DetalleVenta",
        back_populates="venta",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_ventas_empresa_fecha", "empresa_id", "fecha_venta"),
    )

    def __repr__(self) -> str:
        return f"<Venta id={self.id} total={self.total}>"


# ---------------------------------------------------------------------------
# DetalleVenta (línea de producto dentro de una venta)
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
        # RESTRICT: no permite borrar un producto que ya fue vendido
        ForeignKey("productos.id", ondelete="RESTRICT"),
        nullable=False,
    )
    cantidad = Column(Numeric(10, 3), nullable=False)
    # Snapshot del precio en el momento de la venta; no cambia si el
    # precio del producto se modifica después
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_venta")

    __table_args__ = (
        Index("idx_detalles_venta_venta_id", "venta_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<DetalleVenta venta={self.venta_id} "
            f"producto={self.producto_id} qty={self.cantidad}>"
        )


# ---------------------------------------------------------------------------
# SoporteTicket (hilo de conversación de soporte)
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

    empresa = relationship("Empresa", back_populates="soporte_tickets")
    usuario = relationship("Usuario")
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
# SoporteMensaje (mensaje individual dentro de un ticket)
# ---------------------------------------------------------------------------

class SoporteMensaje(Base):
    __tablename__ = "soporte_mensajes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(
        UUID(as_uuid=True),
        ForeignKey("soporte_tickets.id", ondelete="CASCADE"),
        nullable=False,
    )
    remitente_rol = Column(String(30), nullable=False)   # 'superadmin' | 'usuario'
    remitente_email = Column(String(255), nullable=False)
    mensaje = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    ticket = relationship("SoporteTicket", back_populates="mensajes")

    __table_args__ = (
        Index("idx_soporte_mensajes_ticket", "ticket_id"),
    )

    def __repr__(self) -> str:
        return f"<SoporteMensaje rol={self.remitente_rol!r}>"
