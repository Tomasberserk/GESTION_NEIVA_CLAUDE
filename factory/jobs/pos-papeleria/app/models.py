import uuid
import enum
from sqlalchemy import (
    Column, String, Integer, Numeric, Boolean,
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


class UnidadMedida(str, enum.Enum):
    UNIDAD  = "unidad"
    PAQUETE = "paquete"


class CategoriaProducto(str, enum.Enum):
    UTILES_ESCOLARES = "Utiles escolares"
    PAPEL_Y_RESMAS   = "Papel y resmas"
    TECNOLOGIA       = "Tecnologia"
    SERVICIOS        = "Servicios"
    MISCELANEA       = "Miscelanea"


# ---------------------------------------------------------------------------
# AuditMixin — heredado por todas las tablas
# ---------------------------------------------------------------------------

class AuditMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_active  = Column(Boolean, default=True, server_default="1", nullable=False)


# ---------------------------------------------------------------------------
# Empresa (raíz del árbol multi-tenant)
# ---------------------------------------------------------------------------

class Empresa(AuditMixin, Base):
    __tablename__ = "empresas"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre_comercial = Column(String(150), nullable=False)
    nit_o_cedula     = Column(String(50), unique=True, nullable=False)
    plan             = Column(String(50), nullable=False, server_default="basic")

    usuarios = relationship("Usuario", back_populates="empresa", cascade="all, delete-orphan")
    productos = relationship("Producto", back_populates="empresa", cascade="all, delete-orphan")
    ventas   = relationship("Venta",    back_populates="empresa", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Empresa {self.nombre_comercial!r}>"


# ---------------------------------------------------------------------------
# Usuario
# ---------------------------------------------------------------------------

class Usuario(AuditMixin, Base):
    __tablename__ = "usuarios"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email           = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    empresa_id      = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False)
    rol             = Column(
        SAEnum(RolUsuario, name="rolusuario", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=RolUsuario.TENDERO,
    )

    empresa = relationship("Empresa", back_populates="usuarios")
    ventas  = relationship("Venta",   back_populates="usuario")

    __table_args__ = (
        Index("idx_usuarios_email",   "email"),
        Index("idx_usuarios_empresa", "empresa_id"),
    )

    def __repr__(self) -> str:
        return f"<Usuario {self.email!r} rol={self.rol}>"


# ---------------------------------------------------------------------------
# Producto
# Diferencias vs Gestión Neiva:
#   - cantidad_actual: Integer (no Numeric — papelería opera en unidades enteras)
#   - stock_minimo: nuevo campo configurable por producto (default 5)
#   - unidad_medida: solo UNIDAD y PAQUETE (sin gramo/libra/kilo)
#   - categoria: papelería-specific, NOT NULL
#   - sin fecha_vencimiento
# ---------------------------------------------------------------------------

class Producto(AuditMixin, Base):
    __tablename__ = "productos"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id     = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False)
    nombre         = Column(String(255), nullable=False)
    codigo_barras  = Column(String(50), nullable=False)
    precio_costo   = Column(Numeric(10, 2), server_default="0.00", nullable=False)
    precio_venta   = Column(Numeric(10, 2), server_default="0.00", nullable=False)
    cantidad_actual = Column(Integer, server_default="0", nullable=False)
    unidad_medida  = Column(
        SAEnum(UnidadMedida, name="unidadmedida", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        server_default="unidad",
    )
    categoria = Column(
        SAEnum(CategoriaProducto, name="categoriaproducto", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    stock_minimo = Column(Integer, server_default="5", nullable=False)
    foto_url     = Column(String, nullable=True)

    empresa       = relationship("Empresa", back_populates="productos")
    detalles_venta = relationship("DetalleVenta", back_populates="producto", passive_deletes=True)

    __table_args__ = (
        UniqueConstraint("empresa_id", "codigo_barras", name="uq_producto_empresa_barras"),
        Index("idx_productos_empresa",   "empresa_id"),
        # cubre la query WHERE empresa_id=X AND cantidad_actual <= stock_minimo
        Index("idx_productos_stock_bajo", "empresa_id", "cantidad_actual", "stock_minimo"),
    )

    def __repr__(self) -> str:
        return f"<Producto {self.nombre!r} stock={self.cantidad_actual}>"


# ---------------------------------------------------------------------------
# Venta (documento maestro)
# Diferencia vs Gestión Neiva: usuario_id NOT NULL con FK RESTRICT
# ---------------------------------------------------------------------------

class Venta(AuditMixin, Base):
    __tablename__ = "ventas"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id",  ondelete="CASCADE"),  nullable=False)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id",  ondelete="RESTRICT"), nullable=False)
    fecha_venta = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    total      = Column(Numeric(10, 2), server_default="0.00", nullable=False)

    empresa  = relationship("Empresa",  back_populates="ventas")
    usuario  = relationship("Usuario",  back_populates="ventas")
    detalles = relationship("DetalleVenta", back_populates="venta", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_ventas_empresa_fecha", "empresa_id", "fecha_venta"),
        Index("idx_ventas_usuario",       "usuario_id"),
    )

    def __repr__(self) -> str:
        return f"<Venta id={self.id} total={self.total}>"


# ---------------------------------------------------------------------------
# DetalleVenta (línea de producto dentro de una venta)
# ---------------------------------------------------------------------------

class DetalleVenta(AuditMixin, Base):
    __tablename__ = "detalles_venta"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    venta_id      = Column(UUID(as_uuid=True), ForeignKey("ventas.id",    ondelete="CASCADE"),  nullable=False)
    producto_id   = Column(UUID(as_uuid=True), ForeignKey("productos.id", ondelete="RESTRICT"), nullable=False)
    cantidad      = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal      = Column(Numeric(10, 2), nullable=False)

    venta   = relationship("Venta",   back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_venta")

    __table_args__ = (
        Index("idx_detalles_venta_venta_id", "venta_id"),
    )

    def __repr__(self) -> str:
        return f"<DetalleVenta venta={self.venta_id} producto={self.producto_id} qty={self.cantidad}>"
