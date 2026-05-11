# CLAUDE.md — Contexto maestro del proyecto

> Este archivo se carga automáticamente en cada sesión de Claude Code.  
> Mantenerlo actualizado es obligatorio al cerrar cada sprint.

---

## 1. Qué es este proyecto (en dos líneas)

**Objetivo real:** construir una **fábrica de agentes IA** que genere sistemas de software de negocio de forma semi-automática, usando Claude + Gemini como equipo.

**Primer producto de la fábrica:** Gestión Neiva — sistema POS SaaS para tiendas de barrio en Neiva, Colombia. Es simultáneamente el producto a vender y la implementación de referencia del tier "basic".

---

## 2. La fábrica de agentes IA

La fábrica orquesta modelos IA para construir sistemas completos a tres niveles de precio:

| Tier | Sistema | Precio cliente | Costo IA |
|------|---------|---------------|---------|
| Basic | POS simple (patrón Gestión Neiva) | $300–800 USD | ~$0.21 |
| Medium | ERP ligero + proveedores + contabilidad | $1,500–3,500 USD | ~$0.80 |
| Professional | SaaS multi-tenant + pagos + SSO | $5,000–15,000 USD | ~$2.50 |

Ver `factory/pricing/PORTFOLIO.md` para el catálogo completo.

### Stack de agentes — fase actual

| Agente | Modelo | Cuándo usarlo |
|--------|--------|---------------|
| Architect | Claude Sonnet/Opus | Diseño de sistema, schema DB, contratos API |
| Builder | Claude Sonnet | Generación de código principal, integración |
| Worker | Claude Haiku | Schemas Pydantic, tests, migrations, boilerplate |
| Analyst | Gemini CLI (gratis) | Leer codebase grande, análisis, review de calidad |
| Hermes-3 | **BLOQUEADO** | Se activa cuando el sistema facture — Together AI tiene cobro |

**Regla de oro: Gemini lee (gratis, 1M tokens), Claude actúa (de pago, preciso).**

---

## 3. Prioridad absoluta

```
[1] Cerrar MVP Gestión Neiva  →  [2] Primer cliente paga  →  [3] Construir la fábrica
```

Nada de fábrica sin producto que facture. Ver `PLAN_ACTIVO.md` para el estado actual.

---

## 4. Stack técnico de Gestión Neiva

### Backend
- **FastAPI** (Python 3.11) — routers en `app/routers/`
- **SQLAlchemy sync** — capa legacy que usan todos los routers actuales. NO mezclar con async.
- **Capa async** en `app/core/` — para features nuevas cuando escale
- **PostgreSQL 16** via Docker Compose — UUID nativo, enums, ACID
- **Alembic** para migraciones — siempre crear migration al cambiar modelos
- **python-jose + bcrypt** para JWT auth

### Frontend
- **React 19 JSX** (sin TypeScript — velocidad sobre tipado en MVP)
- **Vite** + **TailwindCSS v4** + **Shadcn/UI** (componentes accesibles)
- **React Router v6** — layout con `<Outlet />`, rutas protegidas con `<ProtectedRoute>`
- **CartContext** — estado global del carrito (no Redux, no Zustand — Context es suficiente)

### Infraestructura dev
- Docker Compose: PostgreSQL 16 + Redis 7
- `.venv/` en la raíz del proyecto — **siempre usar `.venv/bin/`**
- Codespaces como entorno principal
- Gemini CLI con `GEMINI_CLI_TRUST_WORKSPACE=true`

---

## 5. Cómo arrancar el entorno

```bash
# 1. Base de datos y Redis
docker compose up -d

# 2. Migraciones (si hay nuevas)
.venv/bin/alembic upgrade head

# 3. Backend (terminal 1)
.venv/bin/uvicorn app.main:app --reload
# → http://localhost:8000/docs

# 4. Frontend (terminal 2)
cd frontend && npm run dev
# → http://localhost:5173

# Usuario de prueba:
# email: admin@demo.com / password: admin123456
```

---

## 6. Reglas del repo — NO negociables

1. **Sin TypeScript** en el frontend — JSX puro mientras sea MVP
2. **No mover archivos sin preguntar** — el namespace `app/models.py` vs `app/models/` ya quemó horas
3. **Venv siempre** — `.venv/bin/python`, `.venv/bin/uvicorn`, `.venv/bin/alembic`; nunca `python3` del sistema
4. **El `.env` nunca va a git** — credenciales solo en Codespaces secrets
5. **Migration por cambio de schema** — cada `ALTER TABLE` necesita su migration Alembic
6. **Soft delete** — los registros nunca se borran físicamente; `is_active = False`
7. **Multi-tenant siempre** — todas las queries deben filtrar por `empresa_id`
8. **Gemini lee, Claude actúa** — no usar Claude para análisis de archivos grandes; usar Gemini CLI

---

## 7. Arquitectura del proyecto

```
GESTION_NEIVA_CLAUDE/
├── app/                        # Backend FastAPI
│   ├── main.py                 # App + CORS + routers registrados
│   ├── models.py               # SQLAlchemy ORM sync (Empresa, Usuario, Producto, Venta)
│   ├── database.py             # Engine sync + get_db
│   ├── dependencies.py         # get_current_user, get_current_user_admin
│   ├── routers/                # auth, productos, ventas, empresas, reportes, dashboard
│   ├── schemas/                # Pydantic schemas de entrada/salida
│   ├── services/               # Lógica de negocio (auth_service, venta_service)
│   └── core/                   # Capa async (database.py, tenant.py)
├── alembic/versions/           # Migraciones (001 inicial, 002 barcode por empresa)
├── frontend/src/
│   ├── context/                # AuthContext (JWT), CartContext (carrito global)
│   ├── hooks/                  # useProductos, useVentas
│   ├── pages/                  # Login, Registro, Dashboard, Inventario, Ventas, Reportes
│   ├── components/layout/      # Layout (Outlet), Sidebar, Header
│   ├── components/             # ProductoCard, ModalProducto, CartSidebar
│   └── services/authService    # fetch con token, logout automático en 401
├── factory/                    # LA FÁBRICA — crece post primer ingreso
│   ├── README.md
│   ├── templates/basic/        # Template basado en Gestión Neiva
│   ├── workflows/              # Pipelines de construcción por tier
│   └── pricing/PORTFOLIO.md
├── .claude/
│   ├── agents/                 # Definiciones de agentes invocables
│   └── settings.json           # MCP servers
├── docs/                       # Documentación del proyecto
├── CLAUDE.md                   # Este archivo
├── GEMINI.md                   # Contexto para Gemini en Antigravity
├── AGENTS.md                   # Protocolo de colaboración Claude + Gemini
└── PLAN_ACTIVO.md              # Plan de sprint activo (visible para ambos AIs)
```

---

## 8. Flujo de datos — venta completa

```
ProductoCard "Agregar"
  → CartContext.agregar()
    → CartSidebar (panel lateral, muestra items + total)
      → checkout()
        → POST /ventas/{empresa_id}
          → venta_service.registrar_venta()
            → SELECT FOR UPDATE por producto (lock de fila)
            → valida stock suficiente
            → descuenta cantidad_actual
            → INSERT ventas + detalles_venta
          → 201 {id, total, detalles}
        → CartContext.vaciar()
        → refetch inventario
```

---

## 9. Bugs conocidos activos

| # | Bug | Impacto | Estado |
|---|-----|---------|--------|
| 1 | CartSidebar no renderea | Ventas imposibles | ✅ Fix en Layout.jsx |
| 2 | barcode unique global | Multi-tenant roto | ✅ Fix models.py + migration 002 |
| 3 | Dashboard sin métricas | Cero visibilidad | ✅ Endpoint + UI reales |
| 4 | Cero tests | Regresiones invisibles | ⏳ Sprint siguiente |
| 5 | node_modules en git | Repo pesado | ⏳ Pendiente git rm --cached |

---

## 10. Colaboración Claude + Gemini

Claude Code y Gemini (Antigravity) son **co-autores** del proyecto, no subordinados entre sí.

- **Claude:** implementa, decide arquitectura, escribe código, ejecuta comandos
- **Gemini:** analiza codebase grande, hace review de calidad, propone mejoras al plan
- **`PLAN_ACTIVO.md`:** plan de sprint compartido — ambos pueden modificarlo
- **`AGENTS.md`:** protocolo de coordinación — reglas de quién hace qué y cuándo

Cuando Gemini proponga un cambio al plan, Claude lo evalúa y lo integra (o lo argumenta).  
Cuando Claude implemente algo que cambie el plan, lo actualiza en el archivo.

Ver `AGENTS.md` para el protocolo completo.
