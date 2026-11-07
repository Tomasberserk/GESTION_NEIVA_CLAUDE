# ADR-004 — Desacople de Llaves Foráneas entre Módulos mediante UUIDs

## Identification

| Field | Value |
|---|---|
| Id | ADR-004 |
| Date | 2026-11-06 |
| Status | Accepted |
| Authors | Architecture Auditor and Engineering Team |
| Supersedes | none |

## Context

The `monolith-governance-framework` enforces strict **Table Ownership**: a table belongs
to one module alone, and **no database foreign key may cross a module boundary**.
In the legacy codebase, `detalles_venta.producto_id`, `ventas.usuario_id`, and
`soporte_tickets.usuario_id` used database `FOREIGN KEY` constraints, coupling domains.

| Constraint | Source |
|---|---|
| One table, one owning module (Table Ownership) | `monolith-governance-framework v2.1.0` |
| No foreign keys crossing module boundaries | [`../../../06-data/database-conventions.md`](../../../06-data/database-conventions.md) |
| Independent module evolution without schema-level cascade deadlocks | `05-architecture/modular-monolith.md` |

## Decision

**We decided:** drop all database `REFERENCES` constraints that cross module boundaries,
retaining the referenced IDs as **plain, indexed `UUID` columns** verified in application
code via public facades.

`pos_ventas` validates `producto_id` through `InventarioFacade`, while `ventas.usuario_id`
and `soporte_tickets.usuario_id` validate through `AuthTenancyFacade`.

## Alternatives evaluated

| Alternative | Pros | Cons | Verdict |
|---|---|---|---|
| Plain indexed UUID columns + Facade checks | Strict module boundary isolation; independent migrations; schema clean | Orphan checks move from DB engine to application code | Chosen |
| Retain PostgreSQL `FOREIGN KEY` constraints | Database engine guarantees referential existence | Modules cannot be refactored or tested in isolation; breaks Table Ownership | Rejected |
| Separate database instances per module | Physical separation | Over-engineering; destroys single-transaction POS checkout ACID | Rejected |

## Consequences

| Kind | Consequence |
|---|---|
| Positive | Schema changes in `productos` or `usuarios` do not require lock coordination with `pos_ventas` |
| Positive | Integration tests can mock cross-module dependencies without inserting dummy foreign rows |
| Cost | Deletions must be handled by application-level soft delete (`is_active = False`) |
| Risk | Unchecked manual SQL scripts could leave orphan UUIDs; mitigated by ORM facade methods |

---

**Related:** [`../../modular-monolith.md`](../../modular-monolith.md) · [`../../../06-data/database-conventions.md`](../../../06-data/database-conventions.md)
