# inventario — Runbook

## Symptoms this module can cause

| Symptom | Likely cause inside this module |
|---|---|
| Checkout fails with 422 Unprocessable | `cantidad_actual` is less than requested quantity (**BR-01**) |
| Product creation fails with 400 Bad Request | Barcode already registered in this tenant (`uq_producto_empresa_barras`) |
| Product search returns 0 results | `is_active` set to false, or filter category mismatch |

## Diagnosis

| Step | How |
|---|---|
| Isolate logs | Filter logs for `module: "inventario"` |
| Check stock balance | Query `SELECT id, nombre, cantidad_actual, is_active FROM productos WHERE empresa_id = '...' AND codigo_barras = '...'` |
| Verify alerts | Query `SELECT id, nombre, fecha_vencimiento FROM productos WHERE empresa_id = '...' AND fecha_vencimiento <= CURRENT_DATE + 15` |

## Recovery

| Situation | Action |
|---|---|
| Inaccurate physical stock | Re-stock or adjust via `InventarioFacade.reabastecer_stock()` or PUT endpoint |
| Accidental soft-deletion | Set `is_active = true` via product update endpoint |

---

**Related:** [`./README.md`](./README.md) · [`../../13-operations/README.md`](../../13-operations/README.md)
