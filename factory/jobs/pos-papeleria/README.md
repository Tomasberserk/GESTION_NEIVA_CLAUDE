# POS Papelería — Sistema de Punto de Venta

> Sistema POS SaaS tier-basic generado por la **Fábrica de Agentes IA** (Claude + Gemini).  
> Demo de pipeline `build-basic.md` — Sprint 5 de Gestión Neiva.

## Stack técnico

| Capa | Tecnología |
|------|-----------|
| Backend | FastAPI + SQLAlchemy + PostgreSQL 16 |
| Auth | JWT (python-jose + bcrypt) |
| Frontend | React 19 + Vite + TailwindCSS v4 |
| Tests | pytest + FastAPI TestClient (34 tests) |
| DevOps | Docker Compose |

## Funcionalidades

- 🔐 **Multi-tenant** — cada empresa opera en su propio namespace
- 👤 **Roles** — Admin (gestión completa) y Tendero (solo POS)  
- 📦 **Inventario** — CRUD productos, categorías papelería, stock mínimo configurable
- 🛒 **POS** — registro de ventas con descuento automático de stock
- 📊 **Dashboard** — ventas del día, ingresos, alertas de stock bajo
- 📋 **Reportes** — historial de ventas con filtro por fecha
- 🖼️ **Imágenes** — upload de fotos de productos

## Arranque rápido (Docker)

```bash
# 1. Copia variables de entorno
cp .env.example .env
# Edita .env con tus claves reales

# 2. Levanta todos los servicios
docker compose up -d

# 3. Verifica que todo corra
docker compose ps
```

El sistema queda disponible en:
- **Frontend:** http://localhost:5173
- **API:** http://localhost:8000
- **Docs API:** http://localhost:8000/docs (solo en DEBUG=true)

## Arranque desarrollo local

### Backend

```bash
# Prerrequisitos: Python 3.11+, PostgreSQL 16

# 1. Instalar dependencias
python -m venv .venv
.venv/Scripts/activate       # Windows
# source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt

# 2. Variables de entorno
cp .env.example .env
# Edita DATABASE_URL, SECRET_KEY

# 3. Migraciones
alembic upgrade head

# 4. Arrancar API
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Tests

```bash
# Desde la raíz del proyecto pos-papeleria
$env:PYTHONPATH=".;tests"
pytest                        # Windows PowerShell
PYTHONPATH=.:tests pytest    # Linux/Mac
```

Resultado esperado: `34 passed in ~13s`

## Estructura del proyecto

```
pos-papeleria/
├── app/
│   ├── main.py              # FastAPI app, CORS, routers
│   ├── database.py          # Engine, SessionLocal, Base
│   ├── models.py            # ORM: Empresa, Usuario, Producto, Venta
│   ├── dependencies.py      # get_current_user, get_current_user_admin
│   ├── routers/             # auth, productos, ventas, usuarios, dashboard, reportes
│   ├── services/            # auth_service, producto_service, venta_service
│   └── schemas/             # Pydantic v2: validación y serialización
├── alembic/                 # Migraciones DB
├── frontend/                # React + Vite
│   └── src/
│       ├── pages/           # Dashboard, Inventario, Ventas, Reportes
│       ├── components/      # CartSidebar, ModalProducto, etc.
│       └── context/         # AuthContext, CartContext
├── tests/                   # 34 integration tests
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── qa-report.md
└── METRICAS.md
```

## Endpoints principales

| Método | Endpoint | Descripción | Rol |
|--------|----------|-------------|-----|
| POST | `/auth/registro` | Registro empresa + admin | Público |
| POST | `/auth/login` | Login → JWT | Público |
| GET | `/auth/me` | Usuario actual | Auth |
| GET | `/dashboard/{empresa_id}` | Métricas del día | Auth |
| GET | `/productos/{empresa_id}` | Inventario | Auth |
| POST | `/productos/` | Crear producto | Admin |
| PUT | `/productos/{id}` | Actualizar producto | Admin |
| DELETE | `/productos/{id}` | Soft-delete producto | Admin |
| POST | `/ventas/{empresa_id}` | Registrar venta | Auth |
| GET | `/ventas/{empresa_id}` | Historial ventas | Auth |
| GET | `/usuarios/{empresa_id}` | Listar usuarios | Admin |
| POST | `/usuarios/` | Crear cajero | Admin |
| DELETE | `/usuarios/{id}` | Desactivar usuario | Admin |

## Variables de entorno requeridas

| Variable | Descripción |
|----------|-------------|
| `DATABASE_URL` | URL de conexión PostgreSQL |
| `SECRET_KEY` | Clave JWT (mínimo 32 chars aleatorios) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración del token (default: 30) |
| `CORS_ORIGINS` | Orígenes permitidos separados por coma |

Ver `.env.example` para la lista completa.

---

*Generado con la Fábrica de Agentes IA — Gestión Neiva © 2026*
