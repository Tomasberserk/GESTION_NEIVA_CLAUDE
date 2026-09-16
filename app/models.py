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
    PRO     = "pro"
    MEDIUM  = "medium"
    PREMIUM = "premium"


class UnidadMedida(str, enum.Enum):
    UNIDAD = "unidad"
    GRAMO  = "gramo"
    LIBRA  = "libra"
    KILO   = "kilo"
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
    is_active = Column(Boolean, default=True, server_default="true", nullable=False)


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
    agent_commands    = relationship("AgentCommand",    back_populates="empresa", cascade="all, delete-orphan")

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
    nombre = Column(String(100), nullable=True)
    telefono_whatsapp = Column(String(20), nullable=True, unique=True)

    empresa = relationship("Empresa", back_populates="usuarios")
    ventas  = relationship("Venta", back_populates="usuario")

    __table_args__ = (
        Index("idx_usuarios_email", "email"),
    )

    def __repr__(self) -> str:
        return f"<Usuario {self.email!r} nombre={self.nombre!r} rol={self.rol}>"


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
    codigo_barras = Column(String(100), nullable=False)
    nombre = Column(String(150), nullable=False)
    precio_costo = Column(Numeric(12, 2), nullable=False)
    precio_venta = Column(Numeric(12, 2), nullable=False)
    cantidad_actual = Column(Numeric(10, 3), nullable=False, default=0.0)
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
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
    )
    vendedor_nombre_snapshot = Column(String(100), nullable=True)

    empresa  = relationship("Empresa", back_populates="ventas")
    usuario  = relationship("Usuario", back_populates="ventas")
    detalles = relationship("DetalleVenta", back_populates="venta", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_ventas_empresa_fecha", "empresa_id", "fecha_venta"),
        Index("idx_ventas_usuario_id", "usuario_id"),
    )

    def __repr__(self) -> str:
        return f"<Venta id={self.id} total={self.total} usuario_id={self.usuario_id}>"


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
# Agente IA — Transacciones e Idempotencia
# ---------------------------------------------------------------------------

class AgentCommand(AuditMixin, Base):
    __tablename__ = "agent_commands"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id      = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False)
    conversation_id = Column(String(100), nullable=False)
    command_id      = Column(String(100), nullable=False)
    action          = Column(String(50), nullable=False)
    payload         = Column(Text, nullable=True)  # JSON string
    status          = Column(String(30), nullable=False, default="PENDIENTE")  # PENDIENTE, EJECUTADO, RECHAZADO, INVALIDADO
    result          = Column(Text, nullable=True)   # JSON string
    executed_at     = Column(DateTime(timezone=True), nullable=True)

    empresa = relationship("Empresa", back_populates="agent_commands")

    __table_args__ = (
        UniqueConstraint("empresa_id", "command_id", name="uq_empresa_command_id"),
        Index("idx_agent_commands_empresa", "empresa_id"),
        Index("idx_agent_commands_command", "command_id"),
        Index("idx_agent_commands_conversation", "conversation_id"),
    )

    def __repr__(self) -> str:
        return f"<AgentCommand {self.command_id} [{self.status}]>"

