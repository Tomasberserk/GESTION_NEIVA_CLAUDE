# 00 — Security Policy

## Secrets management

| Rule | Detail |
|## Ownership

- **Security Owner:** Tomás Barrera Ortiz (`@Tomasberserk`) — Tech Lead & Security Officer.
- **Deputy Reviewers:** Santiago Javela Ospino (`@SantiagoJavelaOspino`) and Juan Pablo Doria Caviedes (`@Doritotes444`).
- **Incident Escalation:** Any credential leak or multi-tenant isolation anomaly must be reported to the Security Owner within 1 hour for immediate key rotation and token revocation.

---|## Ownership

- **Security Owner:** Tomás Barrera Ortiz (`@Tomasberserk`) — Tech Lead & Security Officer.
- **Deputy Reviewers:** Santiago Javela Ospino (`@SantiagoJavelaOspino`) and Juan Pablo Doria Caviedes (`@Doritotes444`).
- **Incident Escalation:** Any credential leak or multi-tenant isolation anomaly must be reported to the Security Owner within 1 hour for immediate key rotation and token revocation.

---|
| Zero secrets in source control | Enforced by pre-commit checks and CI secrets detection |
| Local development | Developers copy `.env.example` to `.env`; real production keys are prohibited |
| Staging and production | Secrets injected directly via Render and Vercel platform environment stores |
| Key rotation | `SECRET_KEY`, `SUPERADMIN_KEY`, and AI API tokens rotated every 90 days |

## Authentication and multi-tenancy

- **Password Hashing:** Passwords hashed with `bcrypt` (work factor 12) via `passlib`.
- **JWT Protection:** HS256 tokens expiring in 480 minutes; validated on all protected endpoints.
- **Tenant Isolation (Fuga Cero):** Per **Constitution Article I**, every database query
  must filter by `empresa_id`. Cross-tenant attempts return HTTP 403 or 404 per **BR-03**.
- **SuperAdmin Protection:** Endpoints under `/api/v1/superadmin/*` require the header
  `x-superadmin-key` matching the private environment variable.

## Input sanitization and CORS

- **Payload Validation:** 100% of request bodies are parsed through strict Pydantic v2 schemas.
- **SQL Injection Prevention:** All queries use SQLAlchemy ORM parameterized statements; raw concatenated SQL strings are strictly forbidden.
- **CORS Allowlist:** Restricted to authorized production domains (`*.vercel.app`) and local development ports (5173/5174).

## Ownership

- **Security Owner:** Tomás Barrera Ortiz (`@Tomasberserk`) — Tech Lead & Security Officer.
- **Deputy Reviewers:** Santiago Javela Ospino (`@SantiagoJavelaOspino`) and Juan Pablo Doria Caviedes (`@Doritotes444`).
- **Incident Escalation:** Any credential leak or multi-tenant isolation anomaly must be reported to the Security Owner within 1 hour for immediate key rotation and token revocation.

---

**Related:** [`./documentation-rules.md`](./documentation-rules.md) · [`../05-architecture/decisions/records/ADR-002-aislamiento-multitenant.md`](../05-architecture/decisions/records/ADR-002-aislamiento-multitenant.md)
