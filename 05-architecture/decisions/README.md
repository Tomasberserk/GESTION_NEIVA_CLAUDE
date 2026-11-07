# 05 — Decisions (ADRs)

## Architecture Decision Records

This directory records significant architectural decisions using the canonical
`monolith-governance-framework` ADR format. An accepted decision cannot be quietly
overridden in code; it must be superseded by a new ADR.

## Index of records

| Id | Title | Status | Date |
|---|---|---|---|
| [ADR-001](./records/ADR-001-modular-monolith-as-default.md) | Modular Monolith as the Default Architecture | Accepted | 2026-09-12 |
| [ADR-002](./records/ADR-002-aislamiento-multitenant.md) | Aislamiento Multi-Tenant por Discriminador de Fila | Accepted | 2026-09-28 |
| [ADR-003](./records/ADR-003-concurrencia-inventario-pos.md) | Concurrencia en Inventario POS mediante `SELECT ... FOR UPDATE` | Accepted | 2026-09-28 |
| [ADR-004](./records/ADR-004-desacople-llaves-foraneas-uuid.md) | Desacople de Llaves Foráneas entre Módulos mediante UUIDs | Accepted | 2026-11-06 |

## Decision lifecycle

- **Proposed:** Documented, undergoing team review.
- **Accepted:** Approved at the architecture review gate; code must conform.
- **Superseded:** Replaced by a newer decision that references this ID.

## Operational verification

- Verified automatically in the GitHub Actions CI pipeline (`.github/workflows/ci.yml`).
- Reviewed by the engineering team under the Monolith Governance Framework v2.1.0.

---

**Related:** [`../README.md`](../README.md) · [`../modular-monolith.md`](../modular-monolith.md)
