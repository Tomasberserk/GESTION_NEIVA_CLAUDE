# 01 — Context

## Purpose

This section states why Gestión Neiva exists, for whom, and where its edges are,
before any domain model or architecture decision is written down.

## Documents

| Document | Answers | Priority |
|---|---|---|
| [overview.md](./overview.md) | What is this system, in one page? | ⭐ |
| [scope.md](./scope.md) | What is in and out of the product? | ⭐ |
| [glossary.md](./glossary.md) | What does each domain term mean? | — |

## Out of scope

This section frames why the system exists and where its edges are — it does not
specify architecture, data schemas, or measurable requirements, and it assumes
one deployable application throughout. Nothing here assumes microservices,
service mesh, API gateway, service discovery, saga, circuit breaker, or
distributed transaction semantics. Distributed-system concerns belong to the
microservices governance framework.

## Ready when

- [x] `overview.md`, `scope.md`, and `glossary.md` describe the real multi-tenant POS SaaS
- [x] `scope.md`'s "Out" list explicitly excludes deprecated ERP/CxP modules and external DIAN invoicing
- [x] Every term `02-domain` documents borrow from this section appears in `glossary.md`

---

**Related:** [`../00-governance/README.md`](../00-governance/README.md) · [`../02-domain/README.md`](../02-domain/README.md)
