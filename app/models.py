import uuid
import enum
from sqlalchemy import (
    Column, String, Integer, Numeric, Boolean,
    DateTime, ForeignKey, Enum as SAEnum, Index,
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
        SAEnum(RolUsuario, name="rolusuario"),
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
    # Único globalmente en el legado; candidato a único-por-empresa en v2
    codigo_barras = Column(String(20), unique=True, nullable=False)
    precio_costo = Column(Numeric(10, 2), server_default="0.00", nullable=False)
    precio_venta = Column(Numeric(10, 2), server_default="0.00", nullable=False)
    cantidad_actual = Column(Integer, server_default="0", nullable=False)
    foto_url = Column(String, nullable=True)

    empresa = relationship("Empresa", back_populates="productos")
    # passive_deletes=True porque ON DELETE RESTRICT en la FK debe dispararse
    # antes de que el ORM intente cualquier acción en cascada
    detalles_venta = relationship(
        "DetalleVenta",
        back_populates="producto",
        passive_deletes=True,
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
    cantidad = Column(Integer, nullable=False)
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
