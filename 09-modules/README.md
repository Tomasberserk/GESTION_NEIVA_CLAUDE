# 09 — Modules

## Purpose

This section defines the internal modular breakdown of Gestión Neiva. Each module
represents a discrete bounded context owning its data tables, exposing an in-process
facade (`api/facade.py`), and keeping its internal implementation private.

## Documents

| Document | Answers | Priority |
|---|---|---|
| [module-catalog.md](./module-catalog.md) | What modules exist, what tables do they own, and what is their status? | ⭐ |
| [auth-tenancy/README.md](./auth-tenancy/README.md) | Bounded context for store accounts, users, and plans | ⭐ |
| [inventario/README.md](./inventario/README.md) | Bounded context for products, barcodes, and expiration | ⭐ |
| [pos-ventas/README.md](./pos-ventas/README.md) | Bounded context for sales transactions and checkout | ⭐ |
| [soporte-crm/README.md](./soporte-crm/README.md) | Bounded context for helpdesk ticketing and SuperAdmin | — |
| [agente-ia/README.md](./agente-ia/README.md) | Bounded context for conversational AI and voice turns | — |
| [reportes-analytics/README.md](./reportes-analytics/README.md) | Bounded context for financial projections and Excel reports | — |

## Out of scope

Microservice networking, message brokers, and inter-process RPC protocols. All 6 modules
ship within the same deployable application and communicate via in-process facade methods.

## Ready when

- [x] Every module row in `module-catalog.md` has a corresponding folder with 4 files
- [x] Every table in `06-data/models.md` has exactly one owning module assigned
- [x] Zero foreign keys cross module boundaries per **ADR-004**

---

**Related:** [`../02-domain/module-boundaries.md`](../02-domain/module-boundaries.md) · [`../05-architecture/modular-monolith.md`](../05-architecture/modular-monolith.md)
