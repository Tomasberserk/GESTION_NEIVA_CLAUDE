# 06 — Database Conventions

## One database, divided by module

The application uses a single PostgreSQL 16 database. Each module owns its specific
tables exclusively. Per **ADR-004**, **no foreign key constraint crosses a module boundary**.

| Relationship Type | Mechanism | Enforced by |
|---|---|---|
| **Intra-module** (same module) | Standard SQL `FOREIGN KEY` (e.g. `detalles_venta.venta_id -> ventas.id`) | PostgreSQL engine constraint |
| **Cross-module** (across modules) | Plain indexed `UUID` column (e.g. `detalles_venta.producto_id`) | Calling `<Module>Facade` at write time |

A write spanning two modules commits within the same database transaction. What moves
is who validates the reference: the facade check replaces the database `REFERENCES` constraint.

## Naming rules

| Element | Rule | Example |
|---|---|---|
| Table | snake_case, plural | `empresas`, `productos`, `ventas`, `detalles_venta` |
| Column | snake_case | `codigo_barras`, `precio_venta`, `cantidad_actual` |
| Primary key | `id`, UUID | `id UUID PRIMARY KEY DEFAULT gen_random_uuid()` |
| Foreign key (internal) | `<singular_table>_id` | `venta_id`, `ticket_id`, `empresa_id` |
| Cross-module reference | `<target_concept>_id` (plain UUID) | `producto_id`, `usuario_id` |
| Boolean | prefixed `is_` or `has_` | `is_active`, `is_admin` |
| Index | `idx_<table>_<column(s)>` | `idx_productos_empresa`, `idx_ventas_empresa_fecha` |
| Unique constraint | `uq_<table>_<column(s)>` | `uq_producto_empresa_barras` |

## Audit columns and soft deletes

Every business table inherits from `AuditMixin`:
- `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- `is_active BOOLEAN NOT NULL DEFAULT TRUE`

Entities with historical transactions are never physically deleted (`DELETE FROM ...`);
they are deactivated via soft delete (`is_active = False`) per **BR-05**.

---

**Related:** [`./models.md`](./models.md) · [`../05-architecture/decisions/records/ADR-004-desacople-llaves-foraneas-uuid.md`](../05-architecture/decisions/records/ADR-004-desacople-llaves-foraneas-uuid.md)
