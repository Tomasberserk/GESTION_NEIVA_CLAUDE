# 13 — Operations

## Purpose

This section defines the observability, monitoring, logging, and operational runbook
procedures for running Gestión Neiva reliably in production.

## Documents

| Document | Answers | Priority |
|---|---|---|
| [observability.md](./observability.md) | How are JSON structured logs, correlationIds, and health checks handled? | ⭐ |
| [runbook.md](./runbook.md) | What are the standard operating procedures for backups, restore, and key rotation? | ⭐ |

## Out of scope

Complex multi-cluster service meshes or distributed APM agents. The application runs as
a single containerized monolith with built-in health checks and log aggregation.

## Ready when

- [x] Structured JSON log format is documented with mandatory `correlationId` (**NFR-09**)
- [x] Deep health check evaluating PostgreSQL and Redis connectivity is specified
- [x] Operational procedures for backups, disaster recovery, and migrations are documented

---

**Related:** [`../04-requirements/non-functional.md`](../04-requirements/non-functional.md) · [`../10-devops/environments.md`](../10-devops/environments.md)
