# soporte-crm — Runbook

## Symptoms this module can cause

| Symptom | Likely cause inside this module |
|---|---|
| SuperAdmin console returns 401 | Missing or mismatched `x-superadmin-key` header |
| Ticket creation fails with 404 | Merchant tenant ID not found in database |
| Thread messages out of order | Client system clock skew; sort by `created_at ASC` |

## Diagnosis

| Step | How |
|---|---|
| Isolate logs | Filter logs for `module: "soporte_crm"` |
| Check open tickets | Query `SELECT count(*) FROM soporte_tickets WHERE estado = 'abierto'` |
| Verify key configuration | Check environment variable `SUPERADMIN_KEY` on server |

## Recovery

| Situation | Action |
|---|---|
| Key compromise | Rotate `SUPERADMIN_KEY` secret on Render and re-issue to administrator |
| Orphaned ticket thread | Reassign ticket status to `cerrado` via SuperAdmin console |

---

**Related:** [`./README.md`](./README.md) · [`../../13-operations/README.md`](../../13-operations/README.md)
