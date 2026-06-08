# ERP Monolith Integration — Backend Phase 1: Models & Migration

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge the 5 ERP Distribuidora models into `app/models.py`, remove the deprecated SSO/Factory Launcher infrastructure, extend the `UnidadMedida` enum with distributor units, and apply Alembic migration 008 that transforms the live database.

**Architecture:** Monolith SaaS — the ERP modules (Proveedores, Compras, CxP) live in the same FastAPI app and PostgreSQL database as the POS core, both scoped by `empresa_id`. Plan-gating (`basic` vs `medium`) will be enforced in route dependencies in Phase 2. This phase only handles the DB layer.

**Tech Stack:** FastAPI · SQLAlchemy sync · PostgreSQL 16 · Alembic (raw SQL pattern) · Python 3.11 · `.venv/` in repo root

---

## File Map

| File | Action | What changes |
|------|--------|-------------|
| `app/models.py` | Modify | Add 4 enums + 5 models + extend UnidadMedida; remove SSOToken; remove factory fields from Empresa; add back-refs to Usuario and Producto |
| `app/main.py` | Modify | Remove `sso` from imports and `app.include_router(sso.router)` |
| `app/routers/superadmin.py` | Modify | Remove `actualizar_factory_config` endpoint; remove factory fields from `listar_empresas` response; replace with `actualizar_plan` endpoint |
| `app/schemas/soporte.py` | Modify | Remove factory fields from `EmpresaAdminOut`; remove `ActualizarFactoryConfig`; add `ActualizarPlan` |
| `app/routers/sso.py` | Delete | Entire file — was only for Factory Launcher |
| `app/schemas/sso.py` | Delete | Entire file — was only for Factory Launcher |
| `tests/test_sso.py` | Delete | Tests for deleted SSO feature |
| `alembic/versions/008_erp_monolito.py` | Create | Migration: drop sso + factory cols, extend enum, create 5 new tables |

---

## Task 1: Update app/models.py

**Files:**
- Modify: `app/models.py`

**Background:** Current `app/models.py` (365–404) has `SSOToken` (table: `sso_tokens`) and `Empresa` has three factory-launcher columns (lines 107–110: `factory_upgrade_solicitado`, `factory_url`, `factory_trial_expires_at`). The ERP distribuidora models live in `factory/jobs/erp-distribuidora/app/models.py` — we port them into the main models. `UnidadMedida` (lines 29–33) gains 5 new values. `Usuario` gains a `compras` back-ref. `Produto` gains a `detalles_compra` back-ref. The new ERP enum columns use `String(50)` (not `SAEnum`) to match the ERP's existing service code which does string comparisons like `estado == "PENDIENTE"`.

- [ ] **Step 1: Verify baseline — all current tests pass**

```powershell
.venv\Scripts\python -m pytest tests/ -v --tb=short -q
```
Expected: 16+ tests passing, 0 failures. If anything fails, stop and fix before continuing.

- [ ] **Step 2: Rewrite app/models.py with merged content**

Replace the entire content of `app/models.py` with:

```python
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
    compras           = relationship("Compra", back_populates="proveedor", passive_deletes=True)
    cuentas_por_pagar = relationship("CuentaPorPagar", back_populates="proveedor", passive_deletes=True)

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
    compra_id         = Column(UUID(as_uuid=True), ForeignKey("compras.id", ondelete="RESTRICT"), nullable=False)
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
```

- [ ] **Step 3: Verify models.py imports cleanly**

```powershell
.venv\Scripts\python -c "from app.models import Empresa, Proveedor, Compra, DetalleCompra, CuentaPorPagar, AbonoCuentaPorPagar, MetodoPagoCompra, EstadoCompra; print('OK')"
```
Expected: `OK`

- [ ] **Step 4: Commit models change**

```powershell
git add app/models.py
git commit -m "feat(models): merge ERP models (Proveedor, Compra, CxP, Abono), extend UnidadMedida, remove SSOToken + factory fields"
```

---

## Task 2: Remove SSO infrastructure (keeps app bootable)

**Files:**
- Modify: `app/main.py`
- Modify: `app/routers/superadmin.py`
- Modify: `app/schemas/soporte.py`
- Delete: `app/routers/sso.py`
- Delete: `app/schemas/sso.py`
- Delete: `tests/test_sso.py`

**Background:** `app/routers/sso.py` does `from app import models` and then accesses `models.SSOToken` — which no longer exists after Task 1. The app will fail to start. `app/routers/superadmin.py` lines 66–68 set `factory_upgrade_solicitado`, `factory_url`, `factory_trial_expires_at` on the response object, and line 109–132 is the `actualizar_factory_config` endpoint — all must be removed. The Factory Config endpoint gets replaced by `PUT /empresas/{id}/plan` which changes the empresa's plan directly (the new way to upgrade to medium).

- [ ] **Step 1: Update app/main.py — remove sso router**

Change line 10 of `app/main.py` from:
```python
from app.routers import auth, dashboard, empresas, productos, reportes, ventas, superadmin, soporte, sso
```
to:
```python
from app.routers import auth, dashboard, empresas, productos, reportes, ventas, superadmin, soporte
```

Remove line 70:
```python
app.include_router(sso.router)
```

- [ ] **Step 2: Update app/schemas/soporte.py — remove factory fields, add ActualizarPlan**

Replace the contents of `app/schemas/soporte.py` with:

```python
from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MensajeOut(BaseModel):
    id: UUID
    remitente_rol: str
    remitente_email: str
    mensaje: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TicketCrear(BaseModel):
    asunto: str
    mensaje: str


class TicketResponder(BaseModel):
    mensaje: str


class TicketListOut(BaseModel):
    id: UUID
    asunto: str
    estado: str
    created_at: datetime
    updated_at: datetime
    empresa_id: UUID

    model_config = {"from_attributes": True}


class TicketOut(TicketListOut):
    mensajes: list[MensajeOut] = []


class EmpresaAdminOut(BaseModel):
    id: UUID
    nombre_comercial: str
    nit_o_cedula: str
    plan: str
    is_active: bool
    trial_expires_at: Optional[datetime]
    total_usuarios: int

    model_config = {"from_attributes": True}


class ActualizarTrial(BaseModel):
    trial_expires_at: datetime


class ActualizarEstado(BaseModel):
    is_active: bool


class ActualizarPlan(BaseModel):
    plan: str  # "basic" | "medium" | "premium"
```

- [ ] **Step 3: Update app/routers/superadmin.py — remove factory endpoint, fix listar_empresas, add plan endpoint**

Replace the `listar_empresas` function (lines 34–70) so it no longer sets factory fields in the response:

```python
@router.get("/empresas", response_model=list[EmpresaAdminOut])
def listar_empresas(
    db: Session = Depends(get_db),
    _: None = Depends(_check_superadmin),
):
    from sqlalchemy import func

    counts = dict(
        db.query(models.Usuario.empresa_id, func.count(models.Usuario.id))
        .group_by(models.Usuario.empresa_id)
        .all()
    )

    empresas = db.query(models.Empresa).order_by(models.Empresa.created_at.desc()).all()

    return [
        EmpresaAdminOut(
            id=e.id,
            nombre_comercial=e.nombre_comercial,
            nit_o_cedula=e.nit_o_cedula,
            plan=e.plan.value if e.plan else "basic",
            is_active=e.is_active,
            trial_expires_at=e.trial_expires_at,
            total_usuarios=counts.get(e.id, 0),
        )
        for e in empresas
    ]
```

Remove the entire `actualizar_factory_config` function (lines 109–132).

Add this new endpoint after `actualizar_estado`:

```python
@router.put("/empresas/{empresa_id}/plan")
def actualizar_plan(
    empresa_id: UUID,
    data: ActualizarPlan,
    db: Session = Depends(get_db),
    _: None = Depends(_check_superadmin),
):
    """
    Cambia el plan de una empresa (basic → medium → premium).
    Activa/desactiva los módulos ERP en el frontend automáticamente.
    """
    from app.models import PlanEmpresa
    try:
        nuevo_plan = PlanEmpresa(data.plan)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plan inválido. Valores permitidos: {[p.value for p in PlanEmpresa]}",
        )
    empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    empresa.plan = nuevo_plan
    db.commit()
    return {"mensaje": "Plan actualizado", "plan": empresa.plan.value}
```

Update the import at the top of `app/routers/superadmin.py` — change `ActualizarFactoryConfig` to `ActualizarPlan`:

```python
from app.schemas.soporte import (
    ActualizarEstado,
    ActualizarPlan,
    ActualizarTrial,
    EmpresaAdminOut,
    TicketListOut,
    TicketResponder,
)
```

- [ ] **Step 4: Delete the three SSO files**

```powershell
Remove-Item app\routers\sso.py
Remove-Item app\schemas\sso.py
Remove-Item tests\test_sso.py
```

- [ ] **Step 5: Verify app loads cleanly**

```powershell
.venv\Scripts\python -c "from app.main import app; print('App loaded OK')"
```
Expected: `App loaded OK` with no import errors.

- [ ] **Step 6: Run remaining tests**

```powershell
.venv\Scripts\python -m pytest tests/ -v --tb=short
```
Expected: `test_auth.py`, `test_soporte_crm.py`, `test_owasp_security.py` all pass. `test_sso.py` no longer exists. Fix any failures before continuing.

- [ ] **Step 7: Commit SSO cleanup**

```powershell
git add app/main.py app/routers/superadmin.py app/schemas/soporte.py
git rm app/routers/sso.py app/schemas/sso.py tests/test_sso.py
git commit -m "chore(cleanup): remove SSO/Factory Launcher — replaced by native ERP plan upgrade"
```

---

## Task 3: Create migration 008_erp_monolito.py

**Files:**
- Create: `alembic/versions/008_erp_monolito.py`

**Background:** The live DB after migration 007 has:
- `sso_tokens` table → must DROP
- `empresas` columns: `factory_upgrade_solicitado`, `factory_url`, `factory_trial_expires_at` → must DROP
- `unidadmedida` PostgreSQL enum with values `unidad, gramo, libra, kilo` → extend with 5 new values
- No ERP tables → must CREATE 5 tables

Pattern used: raw SQL via `conn.execute(sa.text(...))`, same as migrations 003–007. PostgreSQL 16 allows `ALTER TYPE ... ADD VALUE IF NOT EXISTS` inside a transaction.

- [ ] **Step 1: Create alembic/versions/008_erp_monolito.py**

```python
"""erp_monolito

Revision ID: 008
Revises: 007
Create Date: 2026-06-03

Integra ERP Distribuidora en monolito SaaS:
- Elimina tabla sso_tokens y campos factory_launcher de empresas
- Extiende enum unidadmedida con unidades de distribuidora (caja, bulto, kg, litro, metro)
- Crea tablas: proveedores, compras, detalle_compras, cuentas_por_pagar, abonos_cuentas_por_pagar
"""
from alembic import op
import sqlalchemy as sa


revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Eliminar infraestructura SSO/Factory Launcher
    conn.execute(sa.text("DROP TABLE IF EXISTS sso_tokens CASCADE"))
    conn.execute(sa.text(
        "ALTER TABLE empresas DROP COLUMN IF EXISTS factory_upgrade_solicitado"
    ))
    conn.execute(sa.text(
        "ALTER TABLE empresas DROP COLUMN IF EXISTS factory_url"
    ))
    conn.execute(sa.text(
        "ALTER TABLE empresas DROP COLUMN IF EXISTS factory_trial_expires_at"
    ))

    # 2. Extender enum unidadmedida con unidades ERP
    # En PostgreSQL 16, ALTER TYPE ... ADD VALUE IF NOT EXISTS se puede ejecutar
    # dentro de una transacción; los nuevos valores son visibles tras el COMMIT.
    for valor in ("caja", "bulto", "kg", "litro", "metro"):
        conn.execute(sa.text(
            f"ALTER TYPE unidadmedida ADD VALUE IF NOT EXISTS '{valor}'"
        ))

    # 3. Tabla proveedores
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id uuid NOT NULL DEFAULT gen_random_uuid(),
            empresa_id uuid NOT NULL,
            nit_o_cedula varchar(50) NOT NULL,
            razon_social varchar(150) NOT NULL,
            contacto_nombre varchar(100),
            telefono varchar(50),
            email varchar(255),
            direccion varchar(255),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            is_active boolean NOT NULL DEFAULT true,
            PRIMARY KEY (id),
            UNIQUE (empresa_id, nit_o_cedula),
            FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_proveedores_empresa ON proveedores (empresa_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_proveedores_razon_social ON proveedores (razon_social)"
    ))

    # 4. Tabla compras
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS compras (
            id uuid NOT NULL DEFAULT gen_random_uuid(),
            empresa_id uuid NOT NULL,
            proveedor_id uuid NOT NULL,
            usuario_id uuid,
            numero_factura varchar(100),
            fecha_compra timestamptz NOT NULL DEFAULT now(),
            metodo_pago varchar(50) NOT NULL DEFAULT 'EFECTIVO',
            fecha_vencimiento timestamptz,
            estado varchar(50) NOT NULL DEFAULT 'PAGADA',
            total numeric(12, 2) NOT NULL DEFAULT 0.00,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            is_active boolean NOT NULL DEFAULT true,
            PRIMARY KEY (id),
            FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE,
            FOREIGN KEY (proveedor_id) REFERENCES proveedores(id) ON DELETE RESTRICT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_compras_empresa ON compras (empresa_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_compras_proveedor ON compras (proveedor_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_compras_fecha ON compras (fecha_compra)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_compras_estado ON compras (estado)"
    ))

    # 5. Tabla detalle_compras
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS detalle_compras (
            id uuid NOT NULL DEFAULT gen_random_uuid(),
            compra_id uuid NOT NULL,
            producto_id uuid NOT NULL,
            cantidad numeric(10, 3) NOT NULL,
            precio_costo numeric(12, 2) NOT NULL,
            subtotal numeric(12, 2) NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            is_active boolean NOT NULL DEFAULT true,
            PRIMARY KEY (id),
            FOREIGN KEY (compra_id) REFERENCES compras(id) ON DELETE CASCADE,
            FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE RESTRICT
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_detalle_compra_compra ON detalle_compras (compra_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_detalle_compra_producto ON detalle_compras (producto_id)"
    ))

    # 6. Tabla cuentas_por_pagar
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS cuentas_por_pagar (
            id uuid NOT NULL DEFAULT gen_random_uuid(),
            empresa_id uuid NOT NULL,
            compra_id uuid NOT NULL,
            proveedor_id uuid NOT NULL,
            monto_total numeric(12, 2) NOT NULL,
            saldo_pendiente numeric(12, 2) NOT NULL,
            fecha_vencimiento timestamptz NOT NULL,
            estado varchar(50) NOT NULL DEFAULT 'PENDIENTE',
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            is_active boolean NOT NULL DEFAULT true,
            PRIMARY KEY (id),
            FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE,
            FOREIGN KEY (compra_id) REFERENCES compras(id) ON DELETE RESTRICT,
            FOREIGN KEY (proveedor_id) REFERENCES proveedores(id) ON DELETE RESTRICT
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_cuentas_pagar_empresa ON cuentas_por_pagar (empresa_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_cuentas_pagar_proveedor ON cuentas_por_pagar (proveedor_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_cuentas_pagar_estado ON cuentas_por_pagar (estado)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_cuentas_pagar_vencimiento ON cuentas_por_pagar (fecha_vencimiento)"
    ))

    # 7. Tabla abonos_cuentas_por_pagar
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS abonos_cuentas_por_pagar (
            id uuid NOT NULL DEFAULT gen_random_uuid(),
            cuenta_por_pagar_id uuid NOT NULL,
            monto numeric(12, 2) NOT NULL,
            fecha_abono timestamptz NOT NULL DEFAULT now(),
            metodo_pago varchar(50) NOT NULL DEFAULT 'EFECTIVO',
            nota varchar(500),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            is_active boolean NOT NULL DEFAULT true,
            PRIMARY KEY (id),
            FOREIGN KEY (cuenta_por_pagar_id) REFERENCES cuentas_por_pagar(id) ON DELETE CASCADE
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_abonos_cxp ON abonos_cuentas_por_pagar (cuenta_por_pagar_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_abonos_fecha ON abonos_cuentas_por_pagar (fecha_abono)"
    ))


def downgrade() -> None:
    conn = op.get_bind()

    conn.execute(sa.text("DROP TABLE IF EXISTS abonos_cuentas_por_pagar CASCADE"))
    conn.execute(sa.text("DROP TABLE IF EXISTS cuentas_por_pagar CASCADE"))
    conn.execute(sa.text("DROP TABLE IF EXISTS detalle_compras CASCADE"))
    conn.execute(sa.text("DROP TABLE IF EXISTS compras CASCADE"))
    conn.execute(sa.text("DROP TABLE IF EXISTS proveedores CASCADE"))

    # PostgreSQL no soporta DROP VALUE en enums — los valores nuevos quedan tras downgrade.

    # Restaurar infraestructura SSO/Factory Launcher
    conn.execute(sa.text(
        "ALTER TABLE empresas ADD COLUMN IF NOT EXISTS "
        "factory_upgrade_solicitado boolean NOT NULL DEFAULT false"
    ))
    conn.execute(sa.text(
        "ALTER TABLE empresas ADD COLUMN IF NOT EXISTS factory_url varchar(500)"
    ))
    conn.execute(sa.text(
        "ALTER TABLE empresas ADD COLUMN IF NOT EXISTS "
        "factory_trial_expires_at timestamp with time zone"
    ))
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS sso_tokens (
            id uuid NOT NULL,
            empresa_id uuid NOT NULL,
            usuario_id uuid NOT NULL,
            token varchar(64) NOT NULL,
            expires_at timestamp with time zone NOT NULL,
            usado boolean NOT NULL DEFAULT false,
            created_at timestamp with time zone NOT NULL DEFAULT now(),
            PRIMARY KEY (id),
            UNIQUE (token),
            FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_sso_tokens_token ON sso_tokens (token)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_sso_tokens_empresa ON sso_tokens (empresa_id)"
    ))
```

- [ ] **Step 2: Verify migration file compiles**

```powershell
.venv\Scripts\python -m py_compile alembic\versions\008_erp_monolito.py; echo "syntax OK"
```
Expected: `syntax OK`

- [ ] **Step 3: Check Docker is running and apply migration**

```powershell
docker compose ps
```
Expected: PostgreSQL container shows `Up`. If not, run `docker compose up -d` first.

```powershell
.venv\Scripts\alembic upgrade head
```
Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade 007 -> 008, erp_monolito
```
If the ALTER TYPE fails with "cannot be executed from a function or multi-command string", it means your PostgreSQL version needs autocommit mode — fix by wrapping the ALTER TYPE block with:
```python
with op.get_context().autocommit_block():
    for valor in ("caja", "bulto", "kg", "litro", "metro"):
        op.execute(f"ALTER TYPE unidadmedida ADD VALUE IF NOT EXISTS '{valor}'")
```
Then re-run `alembic upgrade head`.

- [ ] **Step 4: Verify the new tables exist and sso_tokens is gone**

```powershell
.venv\Scripts\python -c "
from app.database import engine
from sqlalchemy import inspect, text
insp = inspect(engine)
tables = set(insp.get_table_names())
expected = ['proveedores', 'compras', 'detalle_compras', 'cuentas_por_pagar', 'abonos_cuentas_por_pagar']
for t in expected:
    print(f'  OK  {t}' if t in tables else f'  MISSING  {t}')
print(f'  REMOVED  sso_tokens' if 'sso_tokens' not in tables else f'  STILL EXISTS  sso_tokens — fix downgrade order')

with engine.connect() as c:
    result = c.execute(text(\"SELECT unnest(enum_range(NULL::unidadmedida))::text\")).fetchall()
    vals = [r[0] for r in result]
    print(f'  unidadmedida values: {vals}')
    for v in ['caja', 'bulto', 'kg', 'litro', 'metro']:
        print(f'  OK  {v} in enum' if v in vals else f'  MISSING  {v} from enum')
"
```
Expected:
```
  OK  proveedores
  OK  compras
  OK  detalle_compras
  OK  cuentas_por_pagar
  OK  abonos_cuentas_por_pagar
  REMOVED  sso_tokens
  unidadmedida values: ['unidad', 'gramo', 'libra', 'kilo', 'caja', 'bulto', 'kg', 'litro', 'metro']
  OK  caja in enum
  OK  bulto in enum
  OK  kg in enum
  OK  litro in enum
  OK  metro in enum
```

- [ ] **Step 5: Run all tests**

```powershell
.venv\Scripts\python -m pytest tests/ -v --tb=short
```
Expected: All pass. If `test_soporte_crm.py` fails because of the `EmpresaAdminOut` schema change (removed factory fields), check `conftest.py` for fixtures that set factory fields and remove them.

- [ ] **Step 6: Start the server and hit /health**

```powershell
.venv\Scripts\uvicorn app.main:app --reload --port 8000
```
In a second terminal:
```powershell
Invoke-RestMethod http://localhost:8000/health
```
Expected: `status: ok  version: 2.0.0`

- [ ] **Step 7: Commit migration**

```powershell
git add alembic\versions\008_erp_monolito.py
git commit -m "feat(db): migration 008 — ERP monolith (5 new tables, drop SSO, extend unidadmedida enum)"
```

---

## Self-Review

**Spec coverage check:**

| Sprint 7.8 Requirement | Covered by |
|------------------------|-----------|
| Fusionar modelos Proveedor, Compra, CxP en models | Task 1 |
| Remover SSOToken | Task 1 |
| Eliminar factory fields de Empresa | Task 1 + Task 2 |
| Crear migración Alembic nuevas tablas | Task 3 |
| Reemplazar factory-config endpoint por plan endpoint | Task 2 |
| Verificar tests pasan | Task 2 Step 6, Task 3 Step 5 |

**Scope deferred to Phase 2 (not in this plan):**
- Copiar y adaptar schemas Pydantic del ERP (`app/schemas/proveedor.py`, `compra.py`, `cuenta_por_pagar.py`, `abono.py`)
- Registrar routers de compras, proveedores, CxP en `app/main.py`
- Frontend: copiar componentes y páginas del ERP
- Frontend: sidebar condicional por plan
- Tests de integración ERP (`tests/test_erp_flows.py`)

**No placeholders:** All steps contain exact code or exact commands with expected output.

**Type consistency:** `DetalleCompra` uses `back_populates="detalles_compra"` which matches `Producto.detalles_compra`. `Compra.usuario` uses `back_populates="compras"` which matches `Usuario.compras`. All relationship names are consistent throughout.
