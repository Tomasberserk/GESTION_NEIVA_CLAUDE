# 11 — Quality

## Purpose

This section defines the testing strategy, test pyramid layers, code coverage gates,
and Test-Driven Development (TDD) discipline for Gestión Neiva.

## Documents

| Document | Answers | Priority |
|---|---|---|
| [testing-strategy.md](./testing-strategy.md) | How are tests structured across unit, integration, and e2e layers? | ⭐ |
| [tdd-guide.md](./tdd-guide.md) | How does the team apply Red-Green-Refactor to domain facades? | ⭐ |

## Out of scope

Manual QA exploratory testing protocols or hardware barcode scanner testing rigs.
This section governs automated testing in CI/CD.

## Ready when

- [x] Test pyramid is divided into `unit`, `module_integration`, and `end_to_end` layers
- [x] Coverage thresholds of 80% global and 90% in `pos_ventas` (**NFR-07**) are enforced
- [x] TDD discipline is documented for all facade methods

---

**Related:** [`../04-requirements/traceability-matrix.md`](../04-requirements/traceability-matrix.md) · [`../10-devops/ci-cd.md`](../10-devops/ci-cd.md)
