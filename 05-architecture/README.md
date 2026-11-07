# 05 — Architecture

## Purpose

This section defines the architecture of Gestión Neiva: the modular monolith pattern,
layering inside each bounded context, physical folder layout, boundary enforcement via
`import-linter`, and Architecture Decision Records (ADRs).

## Documents

| Document | Answers | Priority |
|---|---|---|
| [modular-monolith.md](./modular-monolith.md) | How are modules organized in the single deployable? | ⭐ |
| [layered-architecture.md](./layered-architecture.md) | How are technical concerns layered inside a module? | — |
| [module-structure.md](./module-structure.md) | What does the folder tree look like on disk? | ⭐ |
| [boundary-enforcement.md](./boundary-enforcement.md) | How are module boundaries enforced in CI? | ⭐ |
| [decisions/README.md](./decisions/README.md) | What architectural decisions govern the codebase? | ⭐ |

## Out of scope

Independent microservice deployments, Kubernetes orchestration, distributed tracing,
and event brokers (RabbitMQ/Kafka). This system ships as one unified Python/FastAPI process.

## Ready when

- [x] Every module from `02-domain/module-boundaries.md` is accounted for
- [x] Boundary enforcement rules are configured for Python in `.importlinter`
- [x] ADRs 001 through 004 are accepted and recorded in `decisions/records/`

---

**Related:** [`../02-domain/module-boundaries.md`](../02-domain/module-boundaries.md) · [`../06-data/README.md`](../06-data/README.md)
