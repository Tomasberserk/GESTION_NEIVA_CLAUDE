# reportes-analytics — Runbook

## Symptoms this module can cause

| Symptom | Likely cause inside this module |
|---|---|
| Excel export times out (> 10s) | Querying broad date ranges without indexes on `ventas(fecha_venta)` |
| Corrupted spreadsheet download | OpenPyXL buffer not reset to position 0 before streaming bytes |
| Dashboard cards show zero revenue | Timezone mismatch on `fecha_venta` filter |

## Diagnosis

| Step | How |
|---|---|
| Isolate logs | Filter structured logs for `module: "reportes_analytics"` |
| Inspect query plan | Run `EXPLAIN ANALYZE SELECT * FROM ventas WHERE empresa_id = '...' AND fecha_venta >= '...'` |
| Test Excel output | Run `pytest tests/test_fase2_backend_rbac.py -k test_resumen` |

## Recovery

| Situation | Action |
|---|---|
| Slow export query | Limit date range to maximum 90 days per export request |
| High server memory | Ensure `BytesIO` buffer is discarded after streaming |

---

**Related:** [`./README.md`](./README.md) · [`../../13-operations/README.md`](../../13-operations/README.md)
