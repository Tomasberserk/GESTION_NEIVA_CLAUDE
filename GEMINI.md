# GEMINI.md — Contexto del proyecto para Gemini / Antigravity

> Este archivo es el equivalente de CLAUDE.md pero escrito desde la perspectiva de Gemini.  
> Léelo al inicio de cada sesión en Antigravity para tener el contexto completo del proyecto.

---

## 1. Qué es este proyecto

**Gestión Neiva** es un sistema POS (punto de venta) SaaS para tiendas de barrio en Neiva, Colombia. Pero es más que eso: es el **primer producto de una fábrica de agentes IA** que usa Claude + Gemini para construir sistemas de software de negocio de forma semi-automática.

El negocio real no son los sistemas para las tiendas — es la capacidad de orquestar IA para generar esos sistemas con mínimo costo y máxima velocidad.

---

## 2. Tu rol en el equipo

Eres un **co-autor y co-arquitecto**, no un asistente. Tus fortalezas específicas en este proyecto:

- **Análisis de codebase grande** — con 1M tokens de contexto puedes leer el repo completo y encontrar inconsistencias que Claude perdería por límite de ventana
- **Review de calidad** — revisar PRs o sprints completos antes de mergear
- **Propuesta de mejoras al plan** — `PLAN_ACTIVO.md` es un documento vivo; puedes proponer cambios, agregar tareas, reorganizar prioridades
- **Análisis de requirements** — procesar documentos de cliente y estructurar JSON de requisitos para el Architect
- **QA del código generado** — en el pipeline de la fábrica, eres el paso de QA gratuito antes del deploy

### Lo que NO debes hacer sin confirmar

- Modificar `app/models.py` directamente (requiere migration Alembic sincronizada)
- Cambiar la estructura de routers o la arquitectura de capas sin alinear con Claude
- Commitear código sin que pase por el pipeline definido en `factory/workflows/`

---

## 3. Stack técnico (resumen)

### Backend
- FastAPI + SQLAlchemy sync + PostgreSQL 16
- Alembic para migraciones
- JWT auth (python-jose + bcrypt)
- Capa async en `app/core/` (para features futuras)

### Frontend
- React 19 JSX (sin TypeScript — decisión de velocidad para MVP)
- Vite + TailwindCSS v4 + Shadcn/UI
- React Router v6 con `<Outlet />` para layout wrapping
- CartContext para estado global del carrito

### Entorno
- Docker Compose (PostgreSQL 16 + Redis 7)
- Python venv en `.venv/` — siempre usar `.venv/bin/`
- Codespace como entorno principal
- Gemini CLI: `GEMINI_CLI_TRUST_WORKSPACE=true` para análisis sin prompts de permiso

---

## 4. Estado actual del proyecto

Ver `PLAN_ACTIVO.md` para el estado del sprint activo.

### Lo que ya funciona (Sprint 2 + 3)
- Auth completo: registro empresa+admin, login, JWT, /me, logout
- Modelos SQLAlchemy con multi-tenant (todas las queries filtran por empresa_id)
- Unique constraint de barcode por empresa (no global)
- Dashboard con métricas reales (ventas hoy, ingresos hoy, stock bajo)
- CartSidebar en el layout (ventas posibles)
- CORS configurado para puertos 5173 y 5174 de Vite

### Lo que falta para el MVP
- Probar flujo end-to-end: login → inventario → venta → reporte
- Tests automatizados (cero tests actualmente)
- Script de arranque del entorno (hoy se levanta todo manualmente)

---

## 5. La fábrica de agentes IA

### Visión
Tres tiers de sistemas, construidos semi-automáticamente:

| Tier | Ejemplo | Precio cliente | Costo IA |
|------|---------|---------------|---------|
| Basic | POS simple (Gestión Neiva) | $300–800 USD | ~$0.21 |
| Medium | ERP ligero | $1,500–3,500 USD | ~$0.80 |
| Professional | SaaS multi-tenant | $5,000–15,000 USD | ~$2.50 |

### Pipeline tier basic (tú eres el paso 1 y el paso 7)

```
1. [Gemini]    Analizar requirements → JSON estructurado       (gratis)
2. [Architect] Schema DB + contratos API                       (~$0.05)
3. [Haiku ×3]  Backend: models + schemas + migrations          (~$0.02)
4. [Haiku ×3]  Backend: routers + services                     (~$0.03)
5. [Sonnet]    Frontend: páginas + hooks                       (~$0.08)
6. [Haiku]     Tests: auth + ventas + inventario               (~$0.02)
7. [Gemini]    QA: review completo del código generado         (gratis)
8. [Haiku]     DevOps: docker-compose + README deploy          (~$0.01)
```

Ver `factory/workflows/build-basic.md` para el pipeline completo.

---

## 6. Cómo colaborar con Claude

El plan en `PLAN_ACTIVO.md` es **mutable por ambos**. Si ves algo que falta, está mal priorizado, o podría hacerse mejor:

1. Propone el cambio con justificación clara
2. Marca los cambios propuestos con `> [GEMINI PROPONE]` en el archivo
3. Claude evaluará e integrará (o argumentará en contra) en la próxima sesión

**Los planes no son órdenes de Claude — son el mapa compartido del equipo.**

---

## 7. Reglas del repo

1. Sin TypeScript en el frontend (JSX puro)
2. No mover archivos sin coordinar — el namespace `app/models.py` ya causó problemas
3. Siempre `.venv/bin/` para comandos Python
4. El `.env` nunca va a git
5. Multi-tenant siempre: todas las queries filtran por `empresa_id`
6. Soft delete: `is_active = False`, nunca DELETE físico

---

## 8. Cómo arrancar el entorno

```bash
# Base de datos
docker compose up -d

# Migraciones
.venv/bin/alembic upgrade head

# Backend
.venv/bin/uvicorn app.main:app --reload

# Frontend (otra terminal)
cd frontend && npm run dev
```

**Docs de API interactivas:** http://localhost:8000/docs

---

## 9. Archivos clave que deberías conocer

| Archivo | Qué hace |
|---------|----------|
| `app/models.py` | Modelos ORM — Empresa, Usuario, Producto, Venta, DetalleVenta |
| `app/main.py` | FastAPI app, CORS, routers registrados |
| `app/routers/` | Endpoints por módulo |
| `frontend/src/context/` | AuthContext (JWT) y CartContext (carrito) |
| `frontend/src/App.jsx` | Routing principal |
| `PLAN_ACTIVO.md` | Plan de sprint — **léelo y propón cambios** |
| `AGENTS.md` | Protocolo de coordinación entre AIs |
| `factory/` | La fábrica — templates, workflows, pricing |
