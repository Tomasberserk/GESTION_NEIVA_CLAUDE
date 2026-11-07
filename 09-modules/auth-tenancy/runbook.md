# auth-tenancy — Runbook

## Symptoms this module can cause

| Symptom | Likely cause inside this module |
|---|---|
| User receives 401 on valid credentials | Password hash mismatch or expired JWT token |
| Store receives 403 Forbidden on POS write | `trial_expires_at` has passed without an active paid plan |
| Cashier cannot be added | Plan limit reached (Basic = 1 cashier, Pro = 5) |

## Diagnosis

| Step | How |
|---|---|
| Isolate logs | Filter structured logs for `module: "auth_tenancy"` |
| Check tenant trial | Query `SELECT plan, trial_expires_at, is_active FROM empresas WHERE id = '...'` |
| Inspect active cashiers | Query `SELECT count(*) FROM usuarios WHERE empresa_id = '...' AND rol = 'tendero' AND is_active = true` |

## Recovery

| Situation | Action |
|---|---|
| Expired trial for paying store | SuperAdmin updates trial via `PUT /api/v1/superadmin/empresas/{id}/trial` |
| Blocked admin user | SuperAdmin sets `is_active = true` via console |

---

**Related:** [`./README.md`](./README.md) · [`../../13-operations/README.md`](../../13-operations/README.md)
