# pos-ventas — Decisions

## [DEC-01] Snapshot Immutability over Dynamic Joins

| Field | Value |
|---|---|
| Date | 2026-09-28 |
| Status | Active |

**Context:** If a store changes a product's price or deletes an employee, past financial accounting must not alter.

**Decision:** Unit price and cashier name are permanently copied into `detalles_venta.precio_unitario` and `ventas.vendedor_nombre_snapshot`.

**Global ADR:** none — internal to `pos_ventas`

## [DEC-02] Deadlock Prevention via Sorted Locking

| Field | Value |
|---|---|
| Date | 2026-09-28 |
| Status | Active |

**Context:** When two cashiers ring up multiple overlapping items simultaneously, database deadlocks can occur.

**Decision:** Product IDs are sorted alphabetically before executing `SELECT ... FOR UPDATE`.

**Global ADR:** [`ADR-003`](../../05-architecture/decisions/records/ADR-003-concurrencia-inventario-pos.md)

---

**Related:** [`./README.md`](./README.md) · [`../../05-architecture/decisions/README.md`](../../05-architecture/decisions/README.md)
