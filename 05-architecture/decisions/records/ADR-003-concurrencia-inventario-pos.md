# ADR-003 — Concurrencia en Inventario POS mediante `SELECT ... FOR UPDATE`

## Identification

| Field | Value |
|---|---|
| Id | ADR-003 |
| Date | 2026-09-28 |
| Status | Accepted |
| Authors | Tech Lead and Engineering Team |
| Supersedes | none |

## Context

During peak store hours with multiple cashiers, concurrent checkout requests can target the
last available unit of a product. Without concurrency controls, race conditions result in
negative stock balances and overselling, violating **BR-01** and **BR-04**.

| Constraint | Source |
|---|---|
| Zero overselling or negative inventory | `BR-01`, `Constitution Article VI` |
| POS checkout completed under 300 ms | `NFR-01` |
| Zero deadlocks under concurrent multi-item sales | `NFR-03` |

## Decision

**We decided:** use **pessimistic row-level locking (`SELECT ... FOR UPDATE`) ordered
deterministically by product UUID** within a short database transaction during checkout.

Sorting product IDs alphabetically prior to acquisition prevents deadlocks. The lock is
held only during stock verification and deduction, committing immediately with the sale.
If stock is insufficient, the transaction rolls back with HTTP 422.

## Alternatives evaluated

| Alternative | Pros | Cons | Verdict |
|---|---|---|---|
| Pessimistic `FOR UPDATE` sorted by UUID | Immediate consistency; zero overselling; eliminates deadlocks | Holds row lock for a few milliseconds | Chosen |
| Optimistic locking (`version` column) | No locks held | Fails checkout under race conditions, frustrating cashiers in store | Rejected |
| Asynchronous queue (Redis/Celery) | Decouples requests | High latency in cash register; violates immediate synchronous checkout | Rejected |

## Consequences

| Kind | Consequence |
|---|---|
| Positive | Guaranteed inventory consistency under high cashier concurrency |
| Positive | Immediate rejection (422) if a product was purchased milliseconds earlier |
| Cost | Requires short database transactions; external API calls cannot occur inside the lock |
| Risk | Long-running queries on `productos` could block sales; mitigated by short transaction scopes |

## Revisit condition

Revisit this decision if concurrent checkout throughput per store exceeds 50 transactions per second and row-lock contention (`SELECT FOR UPDATE`) causes p95 latency > 300 ms.

---

**Related:** [`../../../02-domain/entities-and-rules.md`](../../../02-domain/entities-and-rules.md) · [`../../../04-requirements/non-functional.md`](../../../04-requirements/non-functional.md)
