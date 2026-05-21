# ERP Distribuidora — Sistema Comercial Mayorista

> Sistema ERP SaaS tier-medium generado por la **Fábrica de Agentes IA** (Claude + Gemini).  
> Caso de estudio y demostración del pipeline `build-medium.md` — Sprint 6 de Gestión Neiva.

## Stack técnico

| Capa | Tecnología |
|------|-----------|
| Backend | FastAPI + SQLAlchemy + SQLite (Test) / PostgreSQL 16 (Prod) |
| Auth | JWT (python-jose + bcrypt) |
| Frontend | React 19 + Vite + TailwindCSS v4 |
| Tests | pytest + FastAPI TestClient (8 tests integrales de negocio) |
| DevOps | Docker Compose |

## Funcionalidades Core (Tier Medium)

- 🔐 **Multi-tenant** — Aislamiento completo de datos por `empresa_id`
- 👤 **RBAC (Roles)** — Admin (acceso total a finanzas y reportes) y Asistente (reabastecimiento e inventario, sin acceso a deudas consolidadas ni dashboard financiero)  
- 📦 **Costeo Dinámico** — El costo unitario de los productos (`precio_costo`) se actualiza automáticamente con el costo de la compra más reciente
- 🛒 **Compras de Mercancía** — Formulario interactivo maestro-detalle con buscador asíncrono para registrar compras a proveedores
- 💸 **Cuentas por Pagar (Deudas)** — Generación automática de deudas a crédito cuando `compra.metodo_pago == 'CREDITO'`
- 📉 **Amortización en Tiempo Real** — Aplicación de abonos a deudas con recalculación y promoción de estado a `PAGADA` al saldar el saldo pendiente
- 🔄 **Reversiones seguras** — Anulación de compras y abonos con bloqueo de concurrencia (`with_for_update`) y restauración del stock/saldo
- 📊 **Dashboard Financiero** — KPIs consolidados de deudas totales, montos pagados, pendientes y alertas de vencimiento rojas para deudas expiradas

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
- **Frontend:** http://localhost:5174
- **API:** http://localhost:8001
- **Docs API:** http://localhost:8001/docs

## Arranque desarrollo local

### Backend

```bash
# Prerrequisitos: Python 3.11+

# 1. Crear entorno virtual (si no se usa el del root)
python -m venv .venv
source .venv/bin/activate       # Linux/Mac
.venv\Scripts\activate          # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Copiar entorno y arrancar
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```
El servidor de Vite levantará en http://localhost:5174 (o 5173 si está libre).

## Suite de Pruebas

```bash
# Desde la carpeta erp-distribuidora, ejecuta:
python -m pytest tests/ -v
```

## Estructura del proyecto

```
erp-distribuidora/
├── app/
│   ├── main.py              # FastAPI bootstrap, CORS y registro de routers
│   ├── database.py          # Session y Engine local
│   ├── dependencies.py      # JWT Auth y validación de roles (RBAC)
│   ├── models.py            # Modelos SQLAlchemy (Empresa, Proveedor, CuentaPorPagar, etc.)
│   ├── routers/             # Endpoints (auth, productos, proveedores, compras, cuentas_por_pagar, dashboard)
│   ├── services/            # Lógica de negocio (auth_service, producto_service, proveedor_service, compra_service, cxp_service)
│   └── schemas/             # Pydantic v2 para validación y serialización
├── frontend/                # React 19 JSX
│   ├── src/
│   │   ├── pages/           # Dashboard, RegistrarCompra, CuentasPorPagar, Proveedores
│   │   ├── components/      # ProtectedRoute, Header, Sidebar, Layout
│   │   ├── hooks/           # useCompras, useCuentasPorPagar, useProveedores, useProductos
│   │   └── services/        # authService
├── tests/                   # Pruebas de integración
│   ├── conftest.py          # Configuración SQLite en memoria con parcheo UUID
│   └── test_erp_flows.py    # 8 casos de prueba integrales
├── docker-compose.yml
├── .env.example
├── Dockerfile
├── requirements.txt
├── qa-report.md
└── METRICAS.md
```

---

*Generado con la Fábrica de Agentes IA — Gestión Neiva © 2026*
