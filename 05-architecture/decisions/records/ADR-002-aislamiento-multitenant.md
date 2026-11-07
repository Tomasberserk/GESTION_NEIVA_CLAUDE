# ADR-002 — Aislamiento Multi-Tenant por Discriminador de Fila

## Identification

| Field | Value |
|---|---|
| Id | ADR-002 |
| Date | 2026-09-28 |
| Status | Accepted |
| Authors | Tech Lead and Engineering Team |
| Supersedes | none |

## Context

Gestión Neiva serves multiple independent stores in Neiva. Data leakage between stores
(such as prices, sales, or customer records) is catastrophic. A multi-tenant strategy was
needed that balances infrastructure cost and strict data isolation per **BR-03**.

| Constraint | Source |
|---|---|
| Zero data leakage between tenants | `Constitution Article I`, `NFR-02` |
| Low infrastructure budget on managed PostgreSQL | `01-context/overview.md` |
| Fast query response under 300 ms | `NFR-01` |

## Decision

**We decided:** implement **Row-Level Multitenancy with an indexed `empresa_id` column**
on all business tables, coupled with mandatory FastAPI dependency injection.

Every incoming request resolves the tenant from the validated JWT token and scopes all
queries through `empresa_id`. Compound indexes `(empresa_id, ...)` guarantee query speed.

## Alternatives evaluated

| Alternative | Pros | Cons | Verdict |
|---|---|---|---|
| Row-Level `empresa_id` Discriminator | Maximum resource efficiency; single Alembic migration sequence; fast queries | Requires discipline in query filtering | Chosen |
| Database-per-tenant | Physical isolation | High hosting cost; migrating 100+ separate DBs is intractable | Rejected |
| Schema-per-tenant | Logical schema separation | Connection pool overhead in PostgreSQL; migration complexity | Rejected |

## Consequences

| Kind | Consequence |
|---|---|
| Positive | Cost-effective deployment on single PostgreSQL instance; simple Alembic migrations |
| Positive | Cross-store analytical aggregation by SuperAdmin is straightforward |
| Cost | All database queries must include the tenant filter |
| Risk | An omitted `where(empresa_id=...)` could leak data; mitigated by automated security tests |

## Revisit condition

Revisit this decision if enterprise retail chains require physically dedicated PostgreSQL schemas or isolated database instances for regulatory compliance.

---

**Related:** [`../../../02-domain/entities-and-rules.md`](../../../02-domain/entities-and-rules.md) · [`../../../06-data/models.md`](../../../06-data/models.md)
