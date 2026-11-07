# inventario — Module Overview

## Purpose

The `inventario` module is the authoritative owner of the store's product catalog.
It controls product names, categories, wholesale/retail units of measure, barcode
lookups, acquisition costs, sale prices, stock balances, and 15-day expiration alerts.

## Public API

| Method | Input | Output | Called by |
|---|---|---|---|
| `InventarioFacade.obtener_producto_por_id` | `empresa_id: UUID, producto_id: UUID` | `ProductoDTO \| None` | `pos_ventas`, `agente_ia` |
| `InventarioFacade.validar_y_descontar_stock_atomic` | `db: Session, empresa_id: UUID, items: list[ItemVentaDTO]` | `list[SnapshotProductoDTO]` | `pos_ventas` |
| `InventarioFacade.reabastecer_stock` | `empresa_id: UUID, producto_id: UUID, cantidad: Decimal, costo: Decimal \| None` | `ProductoDTO` | `agente_ia` |

## Dependencies

| Depends on | Through | Why |
|---|---|---|
| *(none)* | — | `inventario` owns its product data directly; tenant context is passed in arguments |

---

**Related:** [`./data-model.md`](./data-model.md) · [`./runbook.md`](./runbook.md) · [`../module-catalog.md`](../module-catalog.md)
