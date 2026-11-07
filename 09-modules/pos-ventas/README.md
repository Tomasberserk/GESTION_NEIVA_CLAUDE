# pos-ventas — Module Overview

## Purpose

The `pos_ventas` module executes atomic POS transactions, applies pessimistic concurrency
locks during checkout, freezes historical price snapshots, logs cashier identities,
and calculates register totals.

## Public API

| Method | Input | Output | Called by |
|---|---|---|---|
| `VentasFacade.procesar_venta` | `db: Session, empresa_id: UUID, cajero_id: UUID, request: VentaCrearDTO` | `VentaResumenDTO` | Presentation router |
| `VentasFacade.obtener_resumen_diario` | `db: Session, empresa_id: UUID, fecha: date` | `ResumenVentasDiaDTO` | `reportes_analytics`, `agente_ia` |

## Dependencies

| Depends on | Through | Why |
|---|---|---|
| `inventario` | `InventarioFacade.validar_y_descontar_stock_atomic()` | Checks availability and locks items during checkout |
| `auth_tenancy` | `AuthTenancyFacade.obtener_usuario()` | Validates cashier and fetches seller name snapshot |

## Operational verification

- Verified automatically in the GitHub Actions CI pipeline (`.github/workflows/ci.yml`).
- Reviewed by the engineering team under the Monolith Governance Framework v2.1.0.

---

**Related:** [`./data-model.md`](./data-model.md) · [`./runbook.md`](./runbook.md) · [`../module-catalog.md`](../module-catalog.md)
