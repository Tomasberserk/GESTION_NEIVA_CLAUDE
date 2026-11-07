# 06 — Data

## Purpose

This section defines the database conventions, canonical data models, and migration
strategy for the single PostgreSQL database powering Gestión Neiva.

## Documents

| Document | Answers | Priority |
|---|---|---|
| [database-conventions.md](./database-conventions.md) | What naming, type, and ownership rules apply? | ⭐ |
| [models.md](./models.md) | What tables exist, who owns them, and how are they related? | ⭐ |
| [migrations.md](./migrations.md) | How does the database schema evolve across releases? | ⭐ |

## Out of scope

Distributed transactions, sharding, multi-database replication topologies, and database
gateways. The system uses a single relational PostgreSQL 16 database.

## Ready when

- [x] Every table has an explicit, single owning module assigned in `models.md`
- [x] Zero foreign keys cross module boundaries per **ADR-004**
- [x] All 8 active tables are documented; zero ghost ERP tables exist
- [x] Migrations 001 through 012 are documented in `migrations.md`

---

**Related:** [`../05-architecture/modular-monolith.md`](../05-architecture/modular-monolith.md) · [`../07-api/README.md`](../07-api/README.md)
