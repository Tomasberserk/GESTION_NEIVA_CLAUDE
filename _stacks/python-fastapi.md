# _stacks — Python, FastAPI, and React

## Version baseline

| Component | Version | Verify with |
|---|---|---|
| Python & FastAPI | 3.11+ and >= 0.115.0 | `python --version`, `python -c "import fastapi; print(fastapi.__version__)"` |
| SQLAlchemy & Alembic | 2.0.30+ and 1.13.1+ | `python -c "import sqlalchemy; print(sqlalchemy.__version__)"` |
| import-linter | >= 2.0 (`lint-imports`) | `lint-imports --version` |
| pytest & pytest-cov | >= 7.4.0 and >= 4.1.0 | `pytest --version` |
| React & Vite | 19.0+ and 8.0+ | `cd frontend && npm list react vite` |
| PostgreSQL & Redis | 16 and 7-alpine | `docker compose exec redis redis-cli ping` |

## Module layout for FastAPI

```
app/
├── auth_tenancy/                   # Bounded context module
│   ├── api/facade.py + contracts.py  # Public facade; all external modules import
│   └── internal/                   # Private domain, application use cases, models, routes
├── inventario/                     # Bounded context: productos
├── pos_ventas/                     # Bounded context: ventas, detalles_venta
├── soporte_crm/                    # Bounded context: soporte_tickets, mensajes
├── agente_ia/                      # Bounded context: agent_commands
├── reportes_analytics/             # Bounded context: read projections
└── platform/                       # Shared wiring: config, database, errors, middleware
```

## Boundary enforcement (`.importlinter`)

```ini
[importlinter]
root_package = app
[importlinter:contract:module-privacy]
name = Only inventario imports inventario's internals
type = forbidden
allow_indirect_imports = True
source_modules = app.pos_ventas, app.auth_tenancy, app.soporte_crm, app.agente_ia, app.reportes_analytics
forbidden_modules = app.inventario.internal
```

## Lifecycle commands

| Stage | Command | Purpose |
|---|---|---|
| `build` | `pip install -r requirements.txt && python -m compileall -q app` | Resolves packages, verifies syntax |
| `boundary-check`| `lint-imports` | Enforces modular monolith boundaries |
| `test` | `pytest -m "unit or module_integration" --cov=app --cov-fail-under=80` | Enforces **NFR-07** coverage gate |
| `package` | `docker build -t gestion-neiva-api:$(git rev-parse --short HEAD) .` | Builds container image |
| `deploy` | `pytest -m end_to_end` against promoted artifact | Runs e2e validation |
| `local` | `make dev` or `powershell ./dev.ps1` | Starts Redis, FastAPI, and Vite |

---

**Related:** [`../05-architecture/boundary-enforcement.md`](../05-architecture/boundary-enforcement.md) · [`../10-devops/ci-cd.md`](../10-devops/ci-cd.md)
