# reportes-analytics — Decisions

## [DEC-01] OpenPyXL for Server-Side Spreadsheet Generation

| Field | Value |
|---|---|
| Date | 2026-09-15 |
| Status | Active |

**Context:** Store owners in Neiva require formatted Excel sheets for tax bookkeeping and accounting.

**Decision:** Reports are generated in memory using `openpyxl` and streamed directly as `application/vnd.openxmlformats...`.

**Global ADR:** none — internal to `reportes_analytics`

## [DEC-02] Read Projections over Dedicated Reporting Tables

| Field | Value |
|---|---|
| Date | 2026-10-10 |
| Status | Active |

**Context:** For small retailers with fewer than 10,000 sales a month, maintaining materialized reporting tables creates synchronization overhead.

**Decision:** Dashboard metrics are queried directly via indexed aggregation queries on `ventas(empresa_id, fecha_venta)` rather than storing duplicate reporting tables.

**Global ADR:** none — internal to `reportes_analytics`

---

**Related:** [`./README.md`](./README.md) · [`../../05-architecture/decisions/README.md`](../../05-architecture/decisions/README.md)
