# 02 — Domain

## Purpose

This section describes the business domain of Gestión Neiva: its bounded contexts,
its entities and business rules (`BR-NN`), and the module boundaries drawn inside
the single deployable to enforce table ownership and prevent coupling.

## Documents

| Document | Answers | Priority |
|---|---|---|
| [domain-map.md](./domain-map.md) | How do the domain's contexts relate to each other? | — |
| [entities-and-rules.md](./entities-and-rules.md) | What entities exist, and what rules govern them? | ⭐ |
| [module-boundaries.md](./module-boundaries.md) | Where does one module end and the next begin? | ⭐ |

## Out of scope

This section draws boundaries inside one deployable application — it does not
specify physical database migrations, OpenAPI specs, or code layout. A module here
is an internal boundary enforced by a static boundary linter (`import-linter`),
never an independently deployed microservice. No database foreign key crosses
between modules.

## Ready when

- [x] `domain-map.md`, `entities-and-rules.md`, and `module-boundaries.md` reflect the 6 canonical modules
- [x] Every bounded context in `domain-map.md` maps to exactly one module in `module-boundaries.md`
- [x] Every business rule in `entities-and-rules.md` has a unique, falsifiable `BR-NN` identifier
- [x] Cross-module foreign keys are replaced with plain UUID column references and facade checks

---

**Related:** [`../01-context/README.md`](../01-context/README.md) · [`../03-product/README.md`](../03-product/README.md)
