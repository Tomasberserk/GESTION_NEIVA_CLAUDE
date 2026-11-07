# 02 — Module Boundaries

## What a module is

A **module** is a bounded context living inside the single deployable. It owns its
data tables, exposes a narrow **public API** (`<Module>Facade`), and keeps everything
else **internal**, enforced by `import-linter`.

| Term | Meaning | Enforced by |
|---|---|---|
| Module | A bounded context with its own folder and dedicated tables | Folder layout (`app/<module>/`) |
| Public API | The only entry point (`api/facade.py`) other modules may import | Boundary linter (`import-linter`) |
| Internal | Domain, application, and persistence code unreachable from outside | Boundary linter |

## Module map

| Module | Owns | Public API | Depends on |
|---|---|---|---|
| `auth_tenancy` | `empresas`, `usuarios` | `AuthTenancyFacade` | — |
| `inventario` | `productos` | `InventarioFacade` | — |
| `pos_ventas` | `ventas`, `detalles_venta` | `VentasFacade` | `inventario`, `auth_tenancy` |
| `soporte_crm` | `soporte_tickets`, `soporte_mensajes` | `SoporteCrmFacade` | `auth_tenancy` |
| `agente_ia` | `agent_commands` | `AgenteIaFacade` | `inventario`, `pos_ventas`, `auth_tenancy` |
| `reportes_analytics` | *(none — read projections)* | `ReportesFacade` | `pos_ventas`, `inventario` |

## Decoupled table ownership via UUIDs

To satisfy **Table Ownership**, no database `FOREIGN KEY` crosses a module boundary:

1. `detalles_venta.producto_id` is a plain `UUID` column. `pos_ventas` verifies the product
   and fetches frozen price snapshots via `InventarioFacade.validar_y_descontar_stock_atomic()`.
2. `ventas.usuario_id` is a plain `UUID` column with an immutable `vendedor_nombre_snapshot`
   string; verified via `AuthTenancyFacade`.
3. `soporte_tickets.usuario_id` is a plain `UUID` column; merchant data is hydrated via
   `AuthTenancyFacade.obtener_usuario()`.

## Signals the boundary is wrong

| Signal | What it means |
|---|---|
| Two modules write to the same table | Ownership is broken; combine or split the entities |
| A database migration adds a `REFERENCES` across modules | Violates table isolation; replace with UUID and facade validation |
| Circular dependencies between facades | The boundary was drawn in the wrong place |

---

**Evidence:** [BIB-001](https://github.com/jesusarielgb-works/engineering-casebook/blob/v1.0.0/records/bib/BIB-001-parnas-1972.md) — Parnas (1972): decompose around decisions likely to change.

**Related:** [`./domain-map.md`](./domain-map.md) · [`../06-data/database-conventions.md`](../06-data/database-conventions.md)
