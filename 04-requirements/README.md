# 04 — Requirements

## Purpose

This section defines what Gestión Neiva must do, measurably and falsifiably.
Every user story (`HU-NN`) and non-functional requirement (`NFR-NN`) here is
bound to an owning module and closed by an automated test.

## Documents

| Document | Answers | Priority |
|---|---|---|
| [user-stories.md](./user-stories.md) | What does each user story require? | ⭐ |
| [non-functional.md](./non-functional.md) | What operational constraints govern the system? | ⭐ |
| [traceability-matrix.md](./traceability-matrix.md) | How does each requirement trace to code and tests? | ⭐ |

## Out of scope

This section defines requirements, not implementation mechanics or UI component
specifications. Nothing here assumes distributed transactions or external microservices.
Features excluded in [`../01-context/scope.md`](../01-context/scope.md) (such as
deprecated ERP/CxP or electronic invoicing) earn no requirement rows here.

## Ready when

- [x] Every story (`HU-01` to `HU-12`) is assigned to an authoritative owning module
- [x] Every non-functional requirement (`NFR-01` to `NFR-10`) is quantitatively falsifiable
- [x] The traceability matrix maps every row to a design document and a concrete test case

---

**Related:** [`../01-context/scope.md`](../01-context/scope.md) · [`../05-architecture/README.md`](../05-architecture/README.md)
