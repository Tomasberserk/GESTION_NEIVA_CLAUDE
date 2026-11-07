# 05 — Module Structure

## The folder tree

```
GESTION_NEIVA_CLAUDE/
├── app/
│   ├── auth_tenancy/                   # Bounded context: empresas, usuarios
│   │   ├── api/                        # Public API: facade.py and immutable contracts.py
│   │   └── internal/                   # Private: domain/, application/, persistence/, routes/
│   ├── inventario/                     # Bounded context: productos
│   │   ├── api/
│   │   └── internal/
│   ├── pos_ventas/                     # Bounded context: ventas, detalles_venta
│   │   ├── api/
│   │   └── internal/
│   ├── soporte_crm/                    # Bounded context: soporte_tickets, soporte_mensajes
│   │   ├── api/
│   │   └── internal/
│   ├── agente_ia/                      # Bounded context: agent_commands
│   │   ├── api/
│   │   └── internal/
│   ├── reportes_analytics/             # Bounded context: read projections
│   │   ├── api/
│   │   └── internal/
│   └── platform/                       # Cross-cutting technical infrastructure
│       ├── config/                     # Settings and environment variables
│       ├── database/                   # SessionLocal and engine wiring
│       ├── errors/                     # Global exception handlers and error schema
│       ├── middleware/                 # CorrelationId, SecurityHeaders, CORS
│       └── security/                   # JWT and password hashing utilities
├── alembic/versions/                   # Single linear sequence of database migrations
├── frontend/                           # React 19 Single Page Application
├── tests/
│   ├── unit/                           # Pure domain logic tests (no database)
│   ├── module_integration/             # Facade tests against PostgreSQL
│   └── end_to_end/                     # Full HTTP client journey tests
└── .importlinter                       # Boundary enforcement rules
```

## Folder contents

| Folder | Holds | Never holds |
|---|---|---|
| `<module>/api/` | `facade.py` and input/output DTO contracts | Business rules, raw SQLAlchemy queries |
| `<module>/internal/` | Domain entities, use cases, models, and HTTP routes | Imports from another module's `internal/` |
| `platform/` | Framework wiring, logging, security, database session | Business domain logic |
| `tests/` | Unit, integration, and e2e test suites | Production application code |

---

**Related:** [`./modular-monolith.md`](./modular-monolith.md) · [`./boundary-enforcement.md`](./boundary-enforcement.md)
