# inventario — Decisions

## [DEC-01] Barcode Uniqueness Scoped per Tenant

| Field | Value |
|---|---|
| Date | 2026-09-18 |
| Status | Active |

**Context:** Multiple stores stock standard manufactured products (e.g. Coca-Cola 350ml) sharing the exact same EAN-13 barcode.

**Decision:** The unique constraint on barcodes is compound: `(empresa_id, codigo_barras)` via migration `002`.

**Global ADR:** none — internal to `inventario`

## [DEC-02] Decimal Precision for Fractional and Bulk Units

| Field | Value |
|---|---|
| Date | 2026-09-22 |
| Status | Active |

**Context:** Small retailers sell items by weight (gramo, libra, kilo) or bulk divisions.

**Decision:** Column `cantidad_actual` is `NUMERIC(10, 3)` to support fractional sales (e.g. 0.500 kg).

**Global ADR:** none — internal to `inventario`

---

**Related:** [`./README.md`](./README.md) · [`../../05-architecture/decisions/README.md`](../../05-architecture/decisions/README.md)
