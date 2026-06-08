# Super Admin Panel + Soporte CRM — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Añadir un Panel de Super Admin para controlar empresas/tenants y un sistema de soporte tipo inbox (CRM) bidireccional entre tenderos y el super admin.

**Architecture:** Dos nuevos routers FastAPI (`/superadmin` y `/soporte`) con dos nuevas tablas (`soporte_tickets`, `soporte_mensajes`). El super admin se autentica via header `x-superadmin-key`. El cliente usa el JWT existente. El frontend añade una página de soporte tipo Gmail para el tendero y una consola de administración con dos pestañas para el dueño de la plataforma.

**Tech Stack:** FastAPI + SQLAlchemy sync + Alembic + Pydantic v2 (backend) | React 19 JSX + TailwindCSS v4 + Lucide icons (frontend)

---

## Mapa de archivos

| Acción | Archivo |
|--------|---------|
| Modify | `app/models.py` — agregar enum `EstadoTicket`, modelos `SoporteTicket`, `SoporteMensaje`, relación en `Empresa` |
| Create | `alembic/versions/006_crear_tablas_soporte.py` — via autogenerate |
| Create | `app/schemas/soporte.py` — Pydantic schemas |
| Create | `app/routers/superadmin.py` — endpoints `/superadmin/*` |
| Create | `app/routers/soporte.py` — endpoints `/soporte/*` |
| Modify | `app/main.py` — registrar ambos routers |
| Modify | `frontend/src/components/layout/Sidebar.jsx` — añadir "Soporte Técnico" |
| Modify | `frontend/src/App.jsx` — rutas `/soporte` y `/superadmin` |
| Create | `frontend/src/pages/Soporte.jsx` — inbox del tendero |
| Create | `frontend/src/pages/SuperAdmin.jsx` — consola del administrador |
| Create | `tests/test_soporte_crm.py` — tests de integración |

---

## Task 1: Modelos SQLAlchemy

**Files:**
- Modify: `app/models.py`

- [ ] **Step 1: Agregar import de `Text` y el enum `EstadoTicket`**

En `app/models.py`, línea 4, añadir `Text` al import:

```python
from sqlalchemy import (
    Column, String, Integer, Numeric, Boolean, Date, Text,
    DateTime, ForeignKey, Enum as SAEnum, Index, UniqueConstraint,
)
```

Después de `class CategoriaProducto` (línea 43), agregar:

```python
class EstadoTicket(str, enum.Enum):
    ABIERTO = "abierto"
    RESPONDIDO = "respondido"
    CERRADO = "cerrado"
```

- [ ] **Step 2: Agregar modelos `SoporteTicket` y `SoporteMensaje` al final del archivo**

Añadir al final de `app/models.py` (después de `DetalleVenta`):

```python
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
```

- [ ] **Step 3: Añadir relación `soporte_tickets` en el modelo `Empresa`**

Dentro de la clase `Empresa` (después de la relación `ventas`), agregar:

```python
    soporte_tickets = relationship(
        "SoporteTicket",
        back_populates="empresa",
        cascade="all, delete-orphan",
    )
```

- [ ] **Step 4: Verificar que no hay errores de importación**

```powershell
.venv\Scripts\python.exe -c "from app.models import SoporteTicket, SoporteMensaje, EstadoTicket; print('OK')"
```

Esperado: `OK`

- [ ] **Step 5: Commit**

```bash
git add app/models.py
git commit -m "feat(models): add SoporteTicket and SoporteMensaje models"
```

---

## Task 2: Migración Alembic 006

**Files:**
- Create: `alembic/versions/006_crear_tablas_soporte.py` (auto-generado)

- [ ] **Step 1: Generar la migración**

```powershell
.venv\Scripts\alembic.exe revision --autogenerate -m "crear_tablas_soporte"
```

Esperado: archivo `alembic/versions/006_crear_tablas_soporte.py` creado (el número al inicio puede variar con el hash generado).

- [ ] **Step 2: Verificar el contenido del archivo generado**

Abrir el archivo creado y confirmar que `upgrade()` contiene:
- `op.create_table('soporte_tickets', ...)` con columnas `id`, `empresa_id`, `usuario_id`, `asunto`, `estado`, `created_at`, `updated_at`, `is_active`
- `op.create_table('soporte_mensajes', ...)` con columnas `id`, `ticket_id`, `remitente_rol`, `remitente_email`, `mensaje`, `created_at`

Si el autogenerate no detecta las tablas, agregar manualmente en `upgrade()`:

```python
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    op.create_table(
        'soporte_tickets',
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('empresa_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('asunto', sa.String(150), nullable=False),
        sa.Column('estado', sa.Enum('abierto', 'respondido', 'cerrado', name='estadoticket'), server_default='abierto', nullable=False),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_soporte_tickets_empresa', 'soporte_tickets', ['empresa_id'])

    op.create_table(
        'soporte_mensajes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ticket_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('remitente_rol', sa.String(30), nullable=False),
        sa.Column('remitente_email', sa.String(255), nullable=False),
        sa.Column('mensaje', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['ticket_id'], ['soporte_tickets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_soporte_mensajes_ticket', 'soporte_mensajes', ['ticket_id'])


def downgrade() -> None:
    op.drop_index('idx_soporte_mensajes_ticket', table_name='soporte_mensajes')
    op.drop_table('soporte_mensajes')
    op.drop_index('idx_soporte_tickets_empresa', table_name='soporte_tickets')
    op.drop_table('soporte_tickets')
    op.execute("DROP TYPE IF EXISTS estadoticket")
```

- [ ] **Step 3: Aplicar la migración**

```powershell
.venv\Scripts\alembic.exe upgrade head
```

Esperado: `Running upgrade ... -> ..., crear_tablas_soporte`

- [ ] **Step 4: Verificar que las tablas existen**

```powershell
.venv\Scripts\python.exe -c "
from app.database import engine
from sqlalchemy import inspect
insp = inspect(engine)
print(insp.get_table_names())
"
```

Esperado: lista que incluye `'soporte_tickets'` y `'soporte_mensajes'`.

- [ ] **Step 5: Commit**

```bash
git add alembic/versions/
git commit -m "feat(migration): 006 create soporte_tickets and soporte_mensajes tables"
```

---

## Task 3: Schemas Pydantic

**Files:**
- Create: `app/schemas/soporte.py`

- [ ] **Step 1: Crear el archivo de schemas**

```python
# app/schemas/soporte.py
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
```

- [ ] **Step 2: Verificar importación**

```powershell
.venv\Scripts\python.exe -c "from app.schemas.soporte import TicketCrear, TicketOut, EmpresaAdminOut; print('OK')"
```

Esperado: `OK`

- [ ] **Step 3: Commit**

```bash
git add app/schemas/soporte.py
git commit -m "feat(schemas): add soporte Pydantic schemas"
```

---

## Task 4: Router Super Admin

**Files:**
- Create: `app/routers/superadmin.py`

- [ ] **Step 1: Escribir test que falla primero**

Crear `tests/test_soporte_crm.py`:

```python
# tests/test_soporte_crm.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
SUPERADMIN_KEY = "test-super-key-123"


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("SUPERADMIN_KEY", SUPERADMIN_KEY)


def test_superadmin_empresas_sin_key_retorna_403():
    resp = client.get("/superadmin/empresas")
    assert resp.status_code == 403


def test_superadmin_empresas_key_invalida_retorna_403():
    resp = client.get("/superadmin/empresas", headers={"x-superadmin-key": "wrong"})
    assert resp.status_code == 403


def test_superadmin_empresas_con_key_valida_retorna_200():
    resp = client.get("/superadmin/empresas", headers={"x-superadmin-key": SUPERADMIN_KEY})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
```

- [ ] **Step 2: Correr test para verificar que falla (router no existe aún)**

```powershell
.venv\Scripts\pytest.exe tests/test_soporte_crm.py::test_superadmin_empresas_con_key_valida_retorna_200 -v
```

Esperado: FAIL con `404` o `ImportError`

- [ ] **Step 3: Crear el router**

```python
# app/routers/superadmin.py
import os
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas.soporte import (
    ActualizarEstado,
    ActualizarTrial,
    EmpresaAdminOut,
    TicketListOut,
    TicketOut,
    TicketResponder,
)

router = APIRouter(prefix="/superadmin", tags=["SuperAdmin"])

_SUPERADMIN_KEY = os.getenv("SUPERADMIN_KEY")


def _check_superadmin(x_superadmin_key: str = Header(alias="x-superadmin-key")):
    key = os.getenv("SUPERADMIN_KEY")
    if not key or x_superadmin_key != key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clave de superadmin inválida",
        )


@router.get("/empresas")
def listar_empresas(
    db: Session = Depends(get_db),
    _: None = Depends(_check_superadmin),
):
    empresas = db.query(models.Empresa).order_by(models.Empresa.created_at.desc()).all()
    result = []
    for e in empresas:
        total_usuarios = (
            db.query(models.Usuario)
            .filter(models.Usuario.empresa_id == e.id)
            .count()
        )
        result.append({
            "id": e.id,
            "nombre_comercial": e.nombre_comercial,
            "nit_o_cedula": e.nit_o_cedula,
            "plan": e.plan.value if e.plan else None,
            "is_active": e.is_active,
            "trial_expires_at": e.trial_expires_at,
            "total_usuarios": total_usuarios,
        })
    return result


@router.put("/empresas/{empresa_id}/trial")
def actualizar_trial(
    empresa_id: UUID,
    data: ActualizarTrial,
    db: Session = Depends(get_db),
    _: None = Depends(_check_superadmin),
):
    empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    empresa.trial_expires_at = data.trial_expires_at
    db.commit()
    return {"mensaje": "Trial actualizado", "trial_expires_at": empresa.trial_expires_at}


@router.put("/empresas/{empresa_id}/status")
def actualizar_estado(
    empresa_id: UUID,
    data: ActualizarEstado,
    db: Session = Depends(get_db),
    _: None = Depends(_check_superadmin),
):
    empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    empresa.is_active = data.is_active
    db.commit()
    return {"mensaje": "Estado actualizado", "is_active": empresa.is_active}


@router.get("/tickets", response_model=list[TicketListOut])
def listar_todos_tickets(
    db: Session = Depends(get_db),
    _: None = Depends(_check_superadmin),
):
    return (
        db.query(models.SoporteTicket)
        .filter(models.SoporteTicket.is_active.is_(True))
        .order_by(models.SoporteTicket.updated_at.desc())
        .all()
    )


@router.post("/tickets/{ticket_id}/responder")
def responder_ticket(
    ticket_id: UUID,
    data: TicketResponder,
    db: Session = Depends(get_db),
    _: None = Depends(_check_superadmin),
):
    ticket = db.query(models.SoporteTicket).filter(
        models.SoporteTicket.id == ticket_id,
        models.SoporteTicket.is_active.is_(True),
    ).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    mensaje = models.SoporteMensaje(
        ticket_id=ticket_id,
        remitente_rol="superadmin",
        remitente_email="soporte@gestionneiva.com",
        mensaje=data.mensaje,
    )
    ticket.estado = models.EstadoTicket.RESPONDIDO
    db.add(mensaje)
    db.commit()
    return {"mensaje": "Respuesta enviada"}
```

- [ ] **Step 4: Registrar router temporalmente en main.py para poder correr el test**

En `app/main.py`, agregar al bloque de imports:

```python
from app.routers import auth, dashboard, empresas, productos, reportes, ventas, superadmin, soporte
```

Y en el bloque de routers:

```python
app.include_router(superadmin.router)
app.include_router(soporte.router)
```

Nota: el router de soporte aún no existe — crear el archivo vacío primero:

```powershell
New-Item -ItemType File "app\routers\soporte.py"
```

Pegar en `app/routers/soporte.py` un router mínimo para que el import no falle:

```python
from fastapi import APIRouter
router = APIRouter(prefix="/soporte", tags=["Soporte"])
```

- [ ] **Step 5: Correr los 3 tests de superadmin**

```powershell
.venv\Scripts\pytest.exe tests/test_soporte_crm.py -v -k "superadmin"
```

Esperado: 3 PASSED

- [ ] **Step 6: Commit**

```bash
git add app/routers/superadmin.py app/routers/soporte.py app/main.py tests/test_soporte_crm.py
git commit -m "feat(router): add superadmin router with empresa control and CRM endpoints"
```

---

## Task 5: Router Soporte (usuario)

**Files:**
- Modify: `app/routers/soporte.py`

- [ ] **Step 1: Añadir tests para el router de soporte**

Añadir al final de `tests/test_soporte_crm.py`:

```python
import os

# ─────────────────────────────────────────────
# Fixtures de empresa + usuario para tests de soporte
# ─────────────────────────────────────────────

def _registrar_empresa_y_usuario(suffix: str) -> dict:
    """Crea empresa y admin, retorna headers de autenticación."""
    reg_resp = client.post("/auth/registro", json={
        "empresa": {
            "nombre_comercial": f"Tienda {suffix}",
            "nit_o_cedula": f"9000{suffix}",
        },
        "usuario": {
            "email": f"admin{suffix}@test.com",
            "password": "Test123456!",
        },
    })
    assert reg_resp.status_code == 201, reg_resp.json()
    token_resp = client.post("/token", data={
        "username": f"admin{suffix}@test.com",
        "password": "Test123456!",
    })
    assert token_resp.status_code == 200
    token = token_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_usuario_puede_crear_ticket():
    headers = _registrar_empresa_y_usuario("crm1")
    resp = client.post("/soporte/tickets", json={
        "asunto": "Error en inventario",
        "mensaje": "No puedo agregar productos",
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["asunto"] == "Error en inventario"
    assert data["estado"] == "abierto"


def test_usuario_puede_listar_sus_tickets():
    headers = _registrar_empresa_y_usuario("crm2")
    client.post("/soporte/tickets", json={
        "asunto": "Consulta de prueba",
        "mensaje": "Mensaje inicial",
    }, headers=headers)
    resp = client.get("/soporte/tickets", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_superadmin_ve_todos_los_tickets():
    headers_a = _registrar_empresa_y_usuario("crm3")
    headers_b = _registrar_empresa_y_usuario("crm4")
    client.post("/soporte/tickets", json={"asunto": "Ticket A", "mensaje": "msg"}, headers=headers_a)
    client.post("/soporte/tickets", json={"asunto": "Ticket B", "mensaje": "msg"}, headers=headers_b)
    resp = client.get("/superadmin/tickets", headers={"x-superadmin-key": SUPERADMIN_KEY})
    assert resp.status_code == 200
    asuntos = [t["asunto"] for t in resp.json()]
    assert "Ticket A" in asuntos
    assert "Ticket B" in asuntos


def test_flujo_completo_ticket_respuesta():
    headers = _registrar_empresa_y_usuario("crm5")
    # 1. Usuario abre ticket
    create_resp = client.post("/soporte/tickets", json={
        "asunto": "Duda de facturación",
        "mensaje": "¿Cómo exporto el reporte?",
    }, headers=headers)
    assert create_resp.status_code == 201
    ticket_id = create_resp.json()["id"]

    # 2. Superadmin responde
    admin_resp = client.post(
        f"/superadmin/tickets/{ticket_id}/responder",
        json={"mensaje": "Ve a Reportes > Exportar Excel."},
        headers={"x-superadmin-key": SUPERADMIN_KEY},
    )
    assert admin_resp.status_code == 200

    # 3. Usuario ve la respuesta en el hilo
    detail_resp = client.get(f"/soporte/tickets/{ticket_id}", headers=headers)
    assert detail_resp.status_code == 200
    data = detail_resp.json()
    assert data["estado"] == "respondido"
    assert len(data["mensajes"]) == 2
    assert data["mensajes"][1]["remitente_rol"] == "superadmin"
```

- [ ] **Step 2: Correr tests para verificar que fallan (soporte.py está vacío)**

```powershell
.venv\Scripts\pytest.exe tests/test_soporte_crm.py -v -k "usuario or flujo or superadmin_ve"
```

Esperado: varios FAIL (404 o AssertionError)

- [ ] **Step 3: Implementar el router completo de soporte**

Reemplazar el contenido de `app/routers/soporte.py`:

```python
# app/routers/soporte.py
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.soporte import TicketCrear, TicketListOut, TicketOut, TicketResponder

router = APIRouter(prefix="/soporte", tags=["Soporte"])


@router.post("/tickets", status_code=status.HTTP_201_CREATED, response_model=TicketOut)
def crear_ticket(
    data: TicketCrear,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    ticket = models.SoporteTicket(
        empresa_id=current_user.empresa_id,
        usuario_id=current_user.id,
        asunto=data.asunto,
    )
    db.add(ticket)
    db.flush()

    primer_mensaje = models.SoporteMensaje(
        ticket_id=ticket.id,
        remitente_rol="usuario",
        remitente_email=current_user.email,
        mensaje=data.mensaje,
    )
    db.add(primer_mensaje)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/tickets", response_model=list[TicketListOut])
def listar_tickets(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    return (
        db.query(models.SoporteTicket)
        .filter(
            models.SoporteTicket.empresa_id == current_user.empresa_id,
            models.SoporteTicket.is_active.is_(True),
        )
        .order_by(models.SoporteTicket.updated_at.desc())
        .all()
    )


@router.get("/tickets/{ticket_id}", response_model=TicketOut)
def obtener_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    ticket = (
        db.query(models.SoporteTicket)
        .filter(
            models.SoporteTicket.id == ticket_id,
            models.SoporteTicket.empresa_id == current_user.empresa_id,
            models.SoporteTicket.is_active.is_(True),
        )
        .first()
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return ticket


@router.post("/tickets/{ticket_id}/responder")
def responder_ticket(
    ticket_id: UUID,
    data: TicketResponder,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    ticket = (
        db.query(models.SoporteTicket)
        .filter(
            models.SoporteTicket.id == ticket_id,
            models.SoporteTicket.empresa_id == current_user.empresa_id,
            models.SoporteTicket.is_active.is_(True),
        )
        .first()
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    if ticket.estado == models.EstadoTicket.CERRADO:
        raise HTTPException(status_code=400, detail="El ticket está cerrado")

    mensaje = models.SoporteMensaje(
        ticket_id=ticket_id,
        remitente_rol="usuario",
        remitente_email=current_user.email,
        mensaje=data.mensaje,
    )
    ticket.estado = models.EstadoTicket.ABIERTO
    db.add(mensaje)
    db.commit()
    return {"mensaje": "Respuesta enviada"}
```

- [ ] **Step 4: Correr todos los tests del módulo**

```powershell
.venv\Scripts\pytest.exe tests/test_soporte_crm.py -v
```

Esperado: todos PASSED

- [ ] **Step 5: Commit**

```bash
git add app/routers/soporte.py tests/test_soporte_crm.py
git commit -m "feat(router): complete soporte router with ticket CRUD and reply flow"
```

---

## Task 6: Registrar routers en main.py

**Files:**
- Modify: `app/main.py`

- [ ] **Step 1: Actualizar el import y los include_router**

En `app/main.py` línea 10, reemplazar:

```python
from app.routers import auth, dashboard, empresas, productos, reportes, ventas
```

Por:

```python
from app.routers import auth, dashboard, empresas, productos, reportes, ventas, superadmin, soporte
```

Después de `app.include_router(reportes.router)`, añadir:

```python
app.include_router(superadmin.router)
app.include_router(soporte.router)
```

- [ ] **Step 2: Verificar que la app arranca**

```powershell
.venv\Scripts\python.exe -c "from app.main import app; print('App OK', len(app.routes), 'routes')"
```

Esperado: `App OK N routes` sin errores

- [ ] **Step 3: Correr suite completa de tests**

```powershell
.venv\Scripts\pytest.exe tests/ -v --tb=short
```

Esperado: todos PASSED (incluyendo los tests previos de auth)

- [ ] **Step 4: Commit**

```bash
git add app/main.py
git commit -m "feat(main): register superadmin and soporte routers"
```

---

## Task 7: Frontend — Sidebar + Rutas App

**Files:**
- Modify: `frontend/src/components/layout/Sidebar.jsx`
- Modify: `frontend/src/App.jsx`

- [ ] **Step 1: Añadir "Soporte Técnico" al Sidebar**

En `frontend/src/components/layout/Sidebar.jsx`, en los imports de lucide-react (línea 2), añadir `MessageCircle`:

```javascript
import {
  LayoutDashboard,
  Package,
  ShoppingCart,
  BarChart3,
  Settings,
  X,
  MessageCircle,
} from 'lucide-react'
```

En el array `navItems` (línea 12), añadir antes de Configuración:

```javascript
const navItems = [
  { to: '/dashboard',     label: 'Dashboard',        icon: LayoutDashboard },
  { to: '/inventario',    label: 'Inventario',        icon: Package },
  { to: '/ventas',        label: 'Ventas',            icon: ShoppingCart },
  { to: '/reportes',      label: 'Reportes',          icon: BarChart3 },
  { to: '/soporte',       label: 'Soporte Técnico',   icon: MessageCircle },
  { to: '/configuracion', label: 'Configuración',     icon: Settings },
]
```

- [ ] **Step 2: Añadir rutas en App.jsx**

En `frontend/src/App.jsx`, añadir los imports:

```javascript
import Soporte from './pages/Soporte'
import SuperAdmin from './pages/SuperAdmin'
```

Dentro del bloque `<Route element={<Layout />}>`, añadir:

```javascript
<Route path="/soporte" element={<Soporte />} />
```

Fuera del bloque `<Route element={<ProtectedRoute />}>` (pero antes del catch-all `*`), añadir la ruta del superadmin (no protegida por JWT — tiene su propia autenticación por key):

```javascript
<Route path="/superadmin" element={<SuperAdmin />} />
```

El resultado completo de App.jsx debe quedar:

```javascript
import { Routes, Route, Navigate } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/layout/Layout'
import Login from './pages/Login'
import Registro from './pages/Registro'
import Dashboard from './pages/Dashboard'
import Inventario from './pages/Inventario'
import Ventas from './pages/Ventas'
import Reportes from './pages/Reportes'
import Soporte from './pages/Soporte'
import SuperAdmin from './pages/SuperAdmin'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/registro" element={<Registro />} />
      <Route path="/superadmin" element={<SuperAdmin />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/inventario" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/inventario" element={<Inventario />} />
          <Route path="/ventas" element={<Ventas />} />
          <Route path="/reportes" element={<Reportes />} />
          <Route path="/soporte" element={<Soporte />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}
```

- [ ] **Step 3: Crear archivos placeholder para que el build no falle**

```powershell
New-Item -ItemType File "frontend\src\pages\Soporte.jsx"
New-Item -ItemType File "frontend\src\pages\SuperAdmin.jsx"
```

Pegar en cada uno un componente mínimo temporal:

`frontend/src/pages/Soporte.jsx`:
```jsx
export default function Soporte() { return <div>Soporte - cargando...</div> }
```

`frontend/src/pages/SuperAdmin.jsx`:
```jsx
export default function SuperAdmin() { return <div>SuperAdmin - cargando...</div> }
```

- [ ] **Step 4: Verificar que Vite compila sin errores**

```powershell
cd frontend; npm run build 2>&1 | Select-String -Pattern "error|Error|ERROR" -NotMatch | Select-Object -Last 5
```

Esperado: sin líneas de error, output con `✓ built in`

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/layout/Sidebar.jsx frontend/src/App.jsx frontend/src/pages/Soporte.jsx frontend/src/pages/SuperAdmin.jsx
git commit -m "feat(frontend): add soporte route, sidebar link, and SuperAdmin route"
```

---

## Task 8: Página Soporte.jsx — Inbox del tendero

**Files:**
- Modify: `frontend/src/pages/Soporte.jsx`

- [ ] **Step 1: Implementar la página completa**

Reemplazar el contenido de `frontend/src/pages/Soporte.jsx`:

```jsx
import { useState, useEffect, useRef } from 'react'
import { MessageCircle, Plus, Send, X } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const ESTADO_COLOR = {
  abierto: 'bg-orange-100 text-orange-700',
  respondido: 'bg-green-100 text-green-700',
  cerrado: 'bg-gray-100 text-gray-500',
}

async function apiFetch(path, options = {}, token) {
  const res = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...(options.headers || {}),
    },
  })
  if (!res.ok) throw new Error(`Error ${res.status}`)
  return res.json()
}

export default function Soporte() {
  const { token } = useAuth()
  const [tickets, setTickets] = useState([])
  const [ticketActivo, setTicketActivo] = useState(null)
  const [mensajeNuevo, setMensajeNuevo] = useState('')
  const [mostrarModal, setMostrarModal] = useState(false)
  const [nuevoAsunto, setNuevoAsunto] = useState('')
  const [nuevoMensaje, setNuevoMensaje] = useState('')
  const [cargando, setCargando] = useState(false)
  const chatRef = useRef(null)

  const cargarTickets = () =>
    apiFetch('/soporte/tickets', {}, token)
      .then(setTickets)
      .catch(console.error)

  const abrirTicket = (ticket) =>
    apiFetch(`/soporte/tickets/${ticket.id}`, {}, token)
      .then(setTicketActivo)
      .catch(console.error)

  useEffect(() => { cargarTickets() }, [])

  useEffect(() => {
    if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight
  }, [ticketActivo?.mensajes])

  const crearTicket = async () => {
    if (!nuevoAsunto.trim() || !nuevoMensaje.trim()) return
    setCargando(true)
    try {
      await apiFetch('/soporte/tickets', {
        method: 'POST',
        body: JSON.stringify({ asunto: nuevoAsunto, mensaje: nuevoMensaje }),
      }, token)
      setMostrarModal(false)
      setNuevoAsunto('')
      setNuevoMensaje('')
      await cargarTickets()
    } finally {
      setCargando(false)
    }
  }

  const enviarRespuesta = async () => {
    if (!mensajeNuevo.trim() || !ticketActivo) return
    setCargando(true)
    try {
      await apiFetch(`/soporte/tickets/${ticketActivo.id}/responder`, {
        method: 'POST',
        body: JSON.stringify({ mensaje: mensajeNuevo }),
      }, token)
      setMensajeNuevo('')
      await abrirTicket(ticketActivo)
      await cargarTickets()
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="h-[calc(100vh-56px)] flex flex-col">
      <div className="flex items-center justify-between px-6 py-4 border-b bg-white">
        <h1 className="text-xl font-semibold text-slate-800 flex items-center gap-2">
          <MessageCircle size={20} /> Soporte Técnico
        </h1>
        <button
          onClick={() => setMostrarModal(true)}
          className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700 transition-colors"
        >
          <Plus size={16} /> Nuevo ticket
        </button>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Lista de tickets */}
        <aside className="w-72 border-r bg-slate-50 overflow-y-auto shrink-0">
          {tickets.length === 0 && (
            <p className="text-slate-400 text-sm text-center mt-12 px-4">
              No tienes tickets aún. Crea uno si necesitas ayuda.
            </p>
          )}
          {tickets.map((t) => (
            <button
              key={t.id}
              onClick={() => abrirTicket(t)}
              className={`w-full text-left px-4 py-3 border-b hover:bg-white transition-colors ${
                ticketActivo?.id === t.id ? 'bg-white border-l-4 border-l-indigo-600' : ''
              }`}
            >
              <p className="font-medium text-sm text-slate-800 truncate">{t.asunto}</p>
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${ESTADO_COLOR[t.estado]}`}>
                {t.estado}
              </span>
            </button>
          ))}
        </aside>

        {/* Hilo de conversación */}
        <main className="flex-1 flex flex-col">
          {!ticketActivo ? (
            <div className="flex-1 flex items-center justify-center text-slate-400 text-sm">
              Selecciona un ticket para ver la conversación
            </div>
          ) : (
            <>
              <div className="px-6 py-3 border-b bg-white">
                <p className="font-semibold text-slate-800">{ticketActivo.asunto}</p>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${ESTADO_COLOR[ticketActivo.estado]}`}>
                  {ticketActivo.estado}
                </span>
              </div>

              <div ref={chatRef} className="flex-1 overflow-y-auto px-6 py-4 space-y-4 bg-slate-50">
                {ticketActivo.mensajes.map((m) => (
                  <div
                    key={m.id}
                    className={`flex ${m.remitente_rol === 'usuario' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-md px-4 py-2 rounded-xl text-sm ${
                        m.remitente_rol === 'usuario'
                          ? 'bg-indigo-600 text-white'
                          : 'bg-white text-slate-800 border'
                      }`}
                    >
                      <p className="font-medium text-xs opacity-70 mb-1">{m.remitente_email}</p>
                      <p>{m.mensaje}</p>
                    </div>
                  </div>
                ))}
              </div>

              {ticketActivo.estado !== 'cerrado' && (
                <div className="flex gap-2 px-6 py-3 border-t bg-white">
                  <input
                    value={mensajeNuevo}
                    onChange={(e) => setMensajeNuevo(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && enviarRespuesta()}
                    placeholder="Escribe tu respuesta..."
                    className="flex-1 border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                  <button
                    onClick={enviarRespuesta}
                    disabled={cargando || !mensajeNuevo.trim()}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                  >
                    <Send size={16} />
                  </button>
                </div>
              )}
            </>
          )}
        </main>
      </div>

      {/* Modal nuevo ticket */}
      {mostrarModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-semibold text-slate-800">Nuevo ticket de soporte</h2>
              <button onClick={() => setMostrarModal(false)} className="text-slate-400 hover:text-slate-600">
                <X size={18} />
              </button>
            </div>
            <input
              value={nuevoAsunto}
              onChange={(e) => setNuevoAsunto(e.target.value)}
              placeholder="Asunto (ej: Error en inventario)"
              className="w-full border rounded-lg px-3 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <textarea
              value={nuevoMensaje}
              onChange={(e) => setNuevoMensaje(e.target.value)}
              placeholder="Describe tu problema con el mayor detalle posible..."
              rows={4}
              className="w-full border rounded-lg px-3 py-2 text-sm mb-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
            />
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setMostrarModal(false)}
                className="px-4 py-2 text-sm text-slate-600 hover:text-slate-800"
              >
                Cancelar
              </button>
              <button
                onClick={crearTicket}
                disabled={cargando || !nuevoAsunto.trim() || !nuevoMensaje.trim()}
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50"
              >
                {cargando ? 'Enviando...' : 'Crear ticket'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Verificar build sin errores**

```powershell
cd frontend; npm run build 2>&1 | Select-String "error" -CaseSensitive
```

Esperado: sin líneas de error

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/Soporte.jsx
git commit -m "feat(frontend): implement Soporte inbox page with ticket list and chat UI"
```

---

## Task 9: Página SuperAdmin.jsx — Consola del administrador

**Files:**
- Modify: `frontend/src/pages/SuperAdmin.jsx`

- [ ] **Step 1: Implementar la página completa**

Reemplazar el contenido de `frontend/src/pages/SuperAdmin.jsx`:

```jsx
import { useState, useEffect } from 'react'
import { ShieldCheck, Store, MessageSquare, Lock, Eye, EyeOff } from 'lucide-react'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function adminFetch(path, options = {}, key) {
  const res = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'x-superadmin-key': key,
      ...(options.headers || {}),
    },
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `Error ${res.status}`)
  }
  return res.json()
}

function LoginSuperAdmin({ onLogin }) {
  const [key, setKey] = useState('')
  const [mostrar, setMostrar] = useState(false)
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)

  const intentarLogin = async () => {
    setCargando(true)
    setError('')
    try {
      await adminFetch('/superadmin/empresas', {}, key)
      localStorage.setItem('x-superadmin-key', key)
      onLogin(key)
    } catch {
      setError('Clave inválida. Verifica e intenta de nuevo.')
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center">
      <div className="bg-white rounded-2xl p-8 w-full max-w-sm shadow-2xl">
        <div className="flex justify-center mb-4">
          <ShieldCheck size={40} className="text-indigo-600" />
        </div>
        <h1 className="text-xl font-bold text-center text-slate-800 mb-1">Panel de Super Admin</h1>
        <p className="text-sm text-center text-slate-400 mb-6">Gestión Neiva · Sistema de Control</p>

        <div className="relative mb-4">
          <input
            type={mostrar ? 'text' : 'password'}
            value={key}
            onChange={(e) => setKey(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && intentarLogin()}
            placeholder="Llave del sistema..."
            className="w-full border rounded-lg px-3 py-2 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            onClick={() => setMostrar(!mostrar)}
            className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600"
          >
            {mostrar ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        </div>

        {error && <p className="text-red-500 text-xs mb-3">{error}</p>}

        <button
          onClick={intentarLogin}
          disabled={cargando || !key}
          className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors text-sm font-medium"
        >
          {cargando ? 'Verificando...' : 'Ingresar'}
        </button>
      </div>
    </div>
  )
}

function TabComercio({ adminKey }) {
  const [empresas, setEmpresas] = useState([])
  const [busqueda, setBusqueda] = useState('')

  const cargar = () =>
    adminFetch('/superadmin/empresas', {}, adminKey)
      .then(setEmpresas)
      .catch(console.error)

  useEffect(() => { cargar() }, [])

  const cambiarEstado = async (id, is_active) => {
    await adminFetch(`/superadmin/empresas/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ is_active }),
    }, adminKey)
    cargar()
  }

  const cambiarTrial = async (id, fecha) => {
    await adminFetch(`/superadmin/empresas/${id}/trial`, {
      method: 'PUT',
      body: JSON.stringify({ trial_expires_at: new Date(fecha).toISOString() }),
    }, adminKey)
    cargar()
  }

  const filtradas = empresas.filter(e =>
    e.nombre_comercial.toLowerCase().includes(busqueda.toLowerCase()) ||
    e.nit_o_cedula.includes(busqueda)
  )

  return (
    <div>
      <input
        value={busqueda}
        onChange={(e) => setBusqueda(e.target.value)}
        placeholder="Buscar por nombre o NIT..."
        className="w-full border rounded-lg px-3 py-2 text-sm mb-4 focus:outline-none focus:ring-2 focus:ring-indigo-500"
      />
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-100 text-slate-600 text-left">
              <th className="px-4 py-2">Comercio</th>
              <th className="px-4 py-2">NIT</th>
              <th className="px-4 py-2">Plan</th>
              <th className="px-4 py-2">Usuarios</th>
              <th className="px-4 py-2">Trial hasta</th>
              <th className="px-4 py-2">Estado</th>
              <th className="px-4 py-2">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filtradas.map((e) => (
              <tr key={e.id} className="border-b hover:bg-slate-50">
                <td className="px-4 py-3 font-medium text-slate-800">{e.nombre_comercial}</td>
                <td className="px-4 py-3 text-slate-500">{e.nit_o_cedula}</td>
                <td className="px-4 py-3">
                  <span className="bg-indigo-100 text-indigo-700 text-xs px-2 py-0.5 rounded-full font-medium">
                    {e.plan}
                  </span>
                </td>
                <td className="px-4 py-3 text-center">{e.total_usuarios}</td>
                <td className="px-4 py-3">
                  <input
                    type="date"
                    defaultValue={e.trial_expires_at ? e.trial_expires_at.slice(0, 10) : ''}
                    onChange={(ev) => cambiarTrial(e.id, ev.target.value)}
                    className="border rounded px-2 py-1 text-xs"
                  />
                </td>
                <td className="px-4 py-3">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${e.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                    {e.is_active ? 'Activo' : 'Suspendido'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => cambiarEstado(e.id, !e.is_active)}
                    className={`text-xs px-3 py-1 rounded-lg font-medium transition-colors ${
                      e.is_active
                        ? 'bg-red-50 text-red-600 hover:bg-red-100'
                        : 'bg-green-50 text-green-600 hover:bg-green-100'
                    }`}
                  >
                    {e.is_active ? 'Suspender' : 'Activar'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtradas.length === 0 && (
          <p className="text-center text-slate-400 text-sm py-8">Sin resultados</p>
        )}
      </div>
    </div>
  )
}

function TabSoporte({ adminKey }) {
  const [tickets, setTickets] = useState([])
  const [ticketActivo, setTicketActivo] = useState(null)
  const [respuesta, setRespuesta] = useState('')
  const [cargando, setCargando] = useState(false)

  const cargar = () =>
    adminFetch('/superadmin/tickets', {}, adminKey)
      .then(setTickets)
      .catch(console.error)

  const abrirTicket = (t) =>
    fetch(`${API}/soporte/tickets/${t.id}`, {
      headers: { 'x-superadmin-key': adminKey, 'Content-Type': 'application/json' },
    })
      .then(r => r.json())
      .then(setTicketActivo)
      .catch(console.error)

  useEffect(() => { cargar() }, [])

  const enviarRespuesta = async () => {
    if (!respuesta.trim() || !ticketActivo) return
    setCargando(true)
    try {
      await adminFetch(`/superadmin/tickets/${ticketActivo.id}/responder`, {
        method: 'POST',
        body: JSON.stringify({ mensaje: respuesta }),
      }, adminKey)
      setRespuesta('')
      await abrirTicket(ticketActivo)
      await cargar()
    } finally {
      setCargando(false)
    }
  }

  const ESTADO_COLOR = {
    abierto: 'bg-orange-100 text-orange-700',
    respondido: 'bg-green-100 text-green-700',
    cerrado: 'bg-gray-100 text-gray-500',
  }

  return (
    <div className="flex gap-4 h-[600px]">
      <aside className="w-72 border rounded-xl overflow-y-auto shrink-0 bg-slate-50">
        {tickets.length === 0 && (
          <p className="text-slate-400 text-sm text-center mt-12 px-4">Sin tickets de soporte</p>
        )}
        {tickets.map((t) => (
          <button
            key={t.id}
            onClick={() => abrirTicket(t)}
            className={`w-full text-left px-4 py-3 border-b hover:bg-white transition-colors ${
              ticketActivo?.id === t.id ? 'bg-white border-l-4 border-l-indigo-600' : ''
            }`}
          >
            <p className="font-medium text-sm text-slate-800 truncate">{t.asunto}</p>
            <span className={`text-xs px-2 py-0.5 rounded-full ${ESTADO_COLOR[t.estado]}`}>
              {t.estado}
            </span>
          </button>
        ))}
      </aside>

      <div className="flex-1 border rounded-xl flex flex-col overflow-hidden bg-white">
        {!ticketActivo ? (
          <div className="flex-1 flex items-center justify-center text-slate-400 text-sm">
            Selecciona un ticket
          </div>
        ) : (
          <>
            <div className="px-5 py-3 border-b">
              <p className="font-semibold text-slate-800">{ticketActivo.asunto}</p>
            </div>
            <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3 bg-slate-50">
              {(ticketActivo.mensajes || []).map((m) => (
                <div key={m.id} className={`flex ${m.remitente_rol === 'superadmin' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-sm px-4 py-2 rounded-xl text-sm ${
                    m.remitente_rol === 'superadmin'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white border text-slate-800'
                  }`}>
                    <p className="text-xs opacity-70 mb-1">{m.remitente_email}</p>
                    <p>{m.mensaje}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="flex gap-2 px-5 py-3 border-t">
              <input
                value={respuesta}
                onChange={(e) => setRespuesta(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && enviarRespuesta()}
                placeholder="Responder al comercio..."
                className="flex-1 border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <button
                onClick={enviarRespuesta}
                disabled={cargando || !respuesta.trim()}
                className="bg-indigo-600 text-white px-4 rounded-lg hover:bg-indigo-700 disabled:opacity-50 text-sm"
              >
                Enviar
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default function SuperAdmin() {
  const storedKey = localStorage.getItem('x-superadmin-key')
  const [adminKey, setAdminKey] = useState(storedKey || '')
  const [autenticado, setAutenticado] = useState(false)
  const [tab, setTab] = useState('comercios')

  useEffect(() => {
    if (storedKey) {
      fetch(`${API}/superadmin/empresas`, {
        headers: { 'x-superadmin-key': storedKey },
      }).then(r => {
        if (r.ok) setAutenticado(true)
        else localStorage.removeItem('x-superadmin-key')
      }).catch(() => {})
    }
  }, [])

  if (!autenticado) {
    return <LoginSuperAdmin onLogin={(k) => { setAdminKey(k); setAutenticado(true) }} />
  }

  return (
    <div className="min-h-screen bg-slate-100">
      <header className="bg-slate-900 text-white px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <ShieldCheck size={22} className="text-indigo-400" />
          <span className="font-semibold">Panel de Super Admin — Gestión Neiva</span>
        </div>
        <button
          onClick={() => { localStorage.removeItem('x-superadmin-key'); setAutenticado(false) }}
          className="text-xs text-slate-400 hover:text-white flex items-center gap-1"
        >
          <Lock size={12} /> Cerrar sesión
        </button>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setTab('comercios')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              tab === 'comercios' ? 'bg-indigo-600 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'
            }`}
          >
            <Store size={16} /> Control de Comercios
          </button>
          <button
            onClick={() => setTab('soporte')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              tab === 'soporte' ? 'bg-indigo-600 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'
            }`}
          >
            <MessageSquare size={16} /> Bandeja de Soporte
          </button>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm">
          {tab === 'comercios' && <TabComercio adminKey={adminKey} />}
          {tab === 'soporte' && <TabSoporte adminKey={adminKey} />}
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Verificar build sin errores**

```powershell
cd frontend; npm run build 2>&1 | Select-String "error" -CaseSensitive
```

Esperado: sin errores

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/SuperAdmin.jsx
git commit -m "feat(frontend): implement SuperAdmin console with company control and CRM inbox"
```

---

## Task 10: Verificación final end-to-end

- [ ] **Step 1: Correr suite completa de tests backend**

```powershell
.venv\Scripts\pytest.exe tests/ -v --tb=short
```

Esperado: TODOS los tests en verde (incluyendo `test_auth.py` y `test_soporte_crm.py`)

- [ ] **Step 2: Smoke test manual del backend**

Con el servidor corriendo (`uvicorn app.main:app --reload`):

```powershell
# Listar empresas como superadmin
curl -s -H "x-superadmin-key: TU_CLAVE" http://localhost:8000/superadmin/empresas | python -m json.tool
```

Esperado: JSON con lista de empresas

- [ ] **Step 3: Commit final y actualizar PLAN_ACTIVO.md**

Actualizar `PLAN_ACTIVO.md` para marcar Sprint 8 con la tarea completada:

```
[✅] Panel de Super Admin y Soporte CRM — COMPLETO
```

```bash
git add PLAN_ACTIVO.md
git commit -m "docs: mark Super Admin Panel + CRM as complete in PLAN_ACTIVO"
```

---

## Self-Review checklist

- [x] **Cobertura de spec:** Todos los endpoints de PLAN_SOPORTE_CRM.md están cubiertos (GET empresas, PUT trial, PUT status, GET tickets, POST responder — superadmin; POST/GET/GET{id}/POST responder — usuario)
- [x] **Sin placeholders:** Cada step tiene código completo
- [x] **Consistencia de tipos:** `EstadoTicket.ABIERTO/RESPONDIDO/CERRADO` usado consistentemente en modelos y routers
- [x] **Multi-tenant:** El router `/soporte` filtra siempre por `empresa_id` del usuario autenticado
- [x] **Seguridad:** El router `/superadmin` lee la key de `os.getenv` en cada request (no cachea al inicio del módulo para que los tests con `monkeypatch` funcionen)
- [x] **Soft delete:** `SoporteTicket` usa `AuditMixin` con `is_active`; todas las queries filtran `is_active.is_(True)`
