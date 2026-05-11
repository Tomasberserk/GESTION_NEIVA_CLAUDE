# GESTION_NEIVA_CLAUDE

## Proyecto
Plataforma SaaS multi-tenant de gestión empresarial con agentes de IA.
Target inicial: tenderos de Neiva, Colombia.
Escalable a restaurantes, farmacias, retail.

## Stack Tecnológico
- Backend: Python 3.11+ / FastAPI / Pydantic v2
- Frontend: React 18 + Vite + TailwindCSS + Shadcn/UI
- Base de datos: PostgreSQL 15 + SQLAlchemy (async)
- Cache: Redis
- Vector DB: ChromaDB (para RAG)
- Orquestación IA: LangChain 0.2+ / CrewAI
- CI/CD: GitHub Actions
- Hosting: GitHub Codespace (dev) → Railway/Render (prod)

## Estructura del Proyecto
gestion-neiva-claude/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI routes
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── agents/        # IA agent definitions
│   │   └── core/          # Config, security, DB
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Route pages
│   │   ├── hooks/         # Custom hooks
│   │   ├── services/      # API calls
│   │   └── store/         # State management
│   └── package.json
├── docs/
│   ├── srs/               # SRS documents
│   ├── architecture/      # Architecture docs
│   └── agents/            # Agent specifications
├── CLAUDE.md              # THIS FILE
└── README.md

## Convenciones de Código

### Python (Backend)
- Async/await para todo I/O
- Type hints obligatorios
- Docstrings en español
- snake_case para funciones y variables
- PascalCase para clases
- Pydantic para validación de datos
- Alembic para migraciones de DB

### React (Frontend)
- Functional components con hooks
- TypeScript estricto
- TailwindCSS para estilos (no CSS custom)
- React Query para data fetching
- Zustand para state management
- Componentes en PascalCase

### General
- Commits en español: "feat: agregar dashboard de ventas"
- Branch naming: feature/nombre-corto, fix/bug-description
- Tests obligatorios para backend (pytest)
- Cada PR necesita pasar CI antes de merge

## Multi-Tenant
- Toda query debe filtrar por `tenant_id`
- Nunca exponer datos de un tenant a otro
- Auth: JWT con tenant_id en payload
- Row Level Security en PostgreSQL

## Verificación
- Backend: `cd backend && pytest -v`
- Frontend: `cd frontend && npm run test`
- Lint: `ruff check backend/` y `eslint frontend/src/`
- Type check: `mypy backend/app/`

## Reglas para Agentes
- NO crear archivos fuera de la estructura definida
- NO instalar dependencias sin documentar en requirements.txt/package.json
- NO hacer push directo a main (siempre branches)
- Documentar TODA decisión arquitectónica en docs/
- Si no estás seguro de algo, pregunta antes de implementar