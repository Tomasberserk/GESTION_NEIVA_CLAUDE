# reportes-analytics — Module Overview

## Purpose

The `reportes_analytics` module computes read projections, financial KPIs for the dashboard,
and exports sales history to Excel spreadsheets (`openpyxl`). It owns no transactional tables
and operates purely as an analytical read model.

## Public API

| Method | Input | Output | Called by |
|---|---|---|---|
| `ReportesFacade.obtener_metricas_dashboard` | `db: Session, empresa_id: UUID` | `DashboardDTO` | Presentation router |
| `ReportesFacade.generar_excel_ventas` | `db: Session, empresa_id: UUID, fecha_inicio: date, fecha_fin: date` | `bytes` | Presentation router |

Everything not exposed in `ReportesFacade` is private to `internal/application/`.

## Dependencies

| Depends on | Through | Why |
|---|---|---|
| `pos_ventas` | `VentasFacade.obtener_resumen_diario()` | Reads closed sales and revenue totals |
| `inventario` | `InventarioFacade` | Reads low stock counts and expiring products |

## In-process events

| Event | Direction | Involved module |
|---|---|---|
| `VentaConfirmadaEvent` | Consumes | `pos_ventas` (invalidates cached dashboard aggregates) |

---

**Related:** [`./data-model.md`](./data-model.md) · [`./runbook.md`](./runbook.md) · [`../module-catalog.md`](../module-catalog.md)
