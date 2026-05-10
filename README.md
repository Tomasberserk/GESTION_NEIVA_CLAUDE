# Gestión Neiva — Sistema POS SaaS

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green?logo=fastapi)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)

Sistema de punto de venta (POS) SaaS multi-tenant para gestión de tiendas en Neiva, Colombia.

---

## Tech Stack

| Capa | Tecnología |
|------|-----------|
| Backend | FastAPI + SQLAlchemy 2.0 (sync + async) |
| Base de datos | PostgreSQL 16 |
| Caché / Sesiones | Redis 7 |
| Frontend | React 19 + Vite + TailwindCSS v4 |
| Migraciones | Alembic |

---

## Estructura del proyecto

```
GESTION_NEIVA_CLAUDE/
├── app/
│   ├── core/           # Config y base de datos async
│   ├── models/         # Modelos nuevos (Tenant, ...)
│   ├── routers/        # Endpoints FastAPI
│   ├── schemas/        # Schemas Pydantic
│   ├── services/       # Lógica de negocio
│   ├── database.py     # Conexión sync (legado)
│   ├── models.py       # Modelos sync (legado)
│   └── main.py         # Entry point FastAPI
├── frontend/
│   ├── src/
│   │   ├── components/ # Componentes React
│   │   ├── pages/      # Páginas de la app
│   │   ├── context/    # Contextos globales
│   │   └── hooks/      # Custom hooks
│   └── package.json
├── docs/
│   └── srs/            # Documentos de requerimientos
├── alembic/            # Migraciones de BD
├── docker-compose.yml  # Servicios locales
└── requirements.txt
```

---

## Requisitos

- Python 3.11+
- Node.js 20+
- Docker y Docker Compose (para servicios locales)

---

## Instalación rápida

### 1. Clonar y configurar entorno

```bash
git clone <repo-url>
cd GESTION_NEIVA_CLAUDE

# Backend — entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

### 2. Variables de entorno

```bash
cp .env.example .env   # Editar con tus credenciales
```

### 3. Levantar servicios con Docker

```bash
docker compose up -d
```

Esto levanta PostgreSQL en `localhost:5432` y Redis en `localhost:6379`.

### 4. Correr migraciones

```bash
alembic upgrade head
```

### 5. Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Variables de entorno (.env)

```env
DATABASE_URL=postgresql://gestion_user:gestion_pass@localhost:5432/gestion_neiva
ASYNC_DATABASE_URL=postgresql+asyncpg://gestion_user:gestion_pass@localhost:5432/gestion_neiva
SECRET_KEY=tu-clave-secreta-aqui
ENVIRONMENT=development
REDIS_URL=redis://localhost:6379
```

---

## Comandos útiles

```bash
# Correr backend
uvicorn app.main:app --reload

# Correr frontend
cd frontend && npm run dev

# Correr tests
pytest

# Nueva migración
alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
alembic upgrade head
```

**Backend:** http://localhost:8000  
**Docs API:** http://localhost:8000/docs  
**Frontend:** http://localhost:5173

---

## Contribución

1. Crea un branch desde `main`
2. Haz tus cambios
3. Corre los tests antes de hacer PR
4. El PR debe tener descripción clara del cambio
