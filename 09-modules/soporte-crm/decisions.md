# soporte-crm — Decisions

## [DEC-01] Two-Level Authentication for SuperAdmin

| Field | Value |
|---|---|
| Date | 2026-05-25 |
| Status | Active |

**Context:** The platform operator needs global administrative access across all store tickets without possessing tenant credentials.

**Decision:** Endpoints under `/superadmin/*` validate the HTTP header `x-superadmin-key` against an environment secret.

**Global ADR:** none — internal to `soporte_crm`

## [DEC-02] Threaded Conversations over Separate Email Gateways

| Field | Value |
|---|---|
| Date | 2026-06-01 |
| Status | Active |

**Context:** Micro-merchants rarely check external business email accounts while working behind the counter.

**Decision:** Support messaging is embedded directly within the in-app web interface as an inbox thread (`soporte_tickets` + `soporte_mensajes`).

**Global ADR:** none — internal to `soporte_crm`

---

**Related:** [`./README.md`](./README.md) · [`../../05-architecture/decisions/README.md`](../../05-architecture/decisions/README.md)
