# pos-ventas — Runbook

## Symptoms this module can cause

| Symptom | Likely cause inside this module |
|---|---|
| Sale hangs during checkout | Database row lock wait exceeding timeout on `productos` |
| 422 Unprocessable on checkout | Stock was sold out by another cashier a millisecond prior (**BR-01**) |
| Total mismatch on receipt | Subtotal calculation discrepancy in cart payload |

## Diagnosis

| Step | How |
|---|---|
| Isolate logs | Filter structured logs for `module: "pos_ventas"` |
| Check transaction latency | Inspect `duration_ms` on `POST /ventas/{empresa_id}` endpoints |
| Verify lock contention | Query PostgreSQL `pg_stat_activity` for active row locks on `productos` |

## Recovery

| Situation | Action |
|---|---|
| Stale checkout attempt | Advise cashier to refresh cart to pull current available inventory |
| Erroneous sale entered | Merchant marks sale record as deactivated via supervisor endpoint |

---

**Related:** [`./README.md`](./README.md) · [`../../13-operations/README.md`](../../13-operations/README.md)
