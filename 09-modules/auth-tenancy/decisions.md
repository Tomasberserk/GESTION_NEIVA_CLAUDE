# auth-tenancy — Decisions

## [DEC-01] Row-Level Isolation over Database-per-Tenant

| Field | Value |
|---|---|
| Date | 2026-09-28 |
| Status | Active |

**Context:** Managing hundreds of small grocery stores requires cost-efficient infrastructure.

**Decision:** We store all tenant data in a shared PostgreSQL database scoped by `empresa_id`.

**Global ADR:** [`ADR-002`](../../05-architecture/decisions/records/ADR-002-aislamiento-multitenant.md)

## [DEC-02] 15-Day Trial Period for New Stores

| Field | Value |
|---|---|
| Date | 2026-10-15 |
| Status | Active |

**Context:** Small retailers in Neiva need to test the software before purchasing a subscription.

**Decision:** New registrations default to `plan=basic` with `trial_expires_at = now() + 15 days`.

**Global ADR:** none — internal to `auth_tenancy`

---

**Related:** [`./README.md`](./README.md) · [`../../05-architecture/decisions/README.md`](../../05-architecture/decisions/README.md)
