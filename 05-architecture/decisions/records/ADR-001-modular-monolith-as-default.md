# ADR-001 — Modular Monolith as the Default Architecture

## Identification

| Field | Value |
|---|---|
| Id | ADR-001 |
| Date | 2026-09-12 |
| Status | Accepted |
| Authors | Tech Lead and Engineering Team |
| Supersedes | none |

## Context

The engineering team needed to establish whether code is organized by technical layer
or by business bounded context before scaling. Changing this layout later across a
multi-developer team is expensive and risks high-merge friction.

| Constraint | Source |
|---|---|
| One deployable, one PostgreSQL database, one release pipeline | [`../../../01-context/overview.md`](../../../01-context/overview.md) |
| Six distinct bounded contexts drawn on domain map | [`../../../02-domain/domain-map.md`](../../../02-domain/domain-map.md) |
| High-concurrency ACID transactions required for POS checkout | `NFR-01`, `NFR-03` |
| Fast developer onboarding under 1 hour | `NFR-08` |

## Decision

**We decided:** organize Gestión Neiva as a **modular monolith** — one deployable
application divided into modules with private internals and public facades, enforced by
`import-linter`.

The tiebreaker was transactional integrity and operational simplicity: POS checkout
requires strict ACID row locking across sales and inventory that microservices would
complicate with network sagas.

## Alternatives evaluated

| Alternative | Pros | Cons | Verdict |
|---|---|---|---|
| Modular Monolith | ACID consistency in one DB; single deployment; clear folder ownership | Requires lint tooling (`import-linter`) | Chosen |
| Flat Layered Architecture | Simplest initial structure | Cross-domain dependencies quickly tangle into big balls of mud | Rejected |
| Microservices | Independent deployments | Distributed transaction complexity; operational cost exceeds budget | Rejected |

## Consequences

| Kind | Consequence |
|---|---|
| Positive | Blast radius of an inventory or billing change is isolated to its own module |
| Positive | Boundary enforcement is checked automatically in CI via `lint-imports` |
| Cost | Modules cannot cross-import internals; facades must be maintained explicitly |
| Risk | Facades with excessive methods indicate an incorrectly drawn boundary |

---

**Related:** [`../../modular-monolith.md`](../../modular-monolith.md) · [`../../boundary-enforcement.md`](../../boundary-enforcement.md)
