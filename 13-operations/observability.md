# 13 — Observability

## Structured JSON logs

Every log line emitted by Gestión Neiva is structured JSON containing at least the following
standard fields per **NFR-09**:

| Field | Meaning | Example |
|---|---|---|
| `timestamp` | ISO 8601 UTC timestamp | `"2026-11-06T12:00:00Z"` |
| `level` | Log severity level | `"INFO"`, `"WARNING"`, `"ERROR"` |
| `correlationId` | Unique UUID generated per incoming request | `"c7a9e1e2-9b2f-4c12-8e6f-123456789abc"` |
| `module` | Owning module logger namespace | `"pos_ventas"`, `"inventario"`, `"platform"` |
| `message` | Human-readable event description | `"Venta registrada exitosamente"` |

Carrying `correlationId` through facades allows tracing a request from the POS router
through stock verification in `inventario` to final commit in `pos_ventas`.

## Minimum operational metrics

| Metric | Type | Purpose |
|---|---|---|
| `http_requests_total` | Counter by status and route | Measures overall traffic and error rates |
| `http_request_duration_seconds` | Histogram by route | Enforces **NFR-01** (p95 checkout < 300 ms) |
| `sales_completed_total` | Counter by tenant | Core business volume signal |

## Deep health check (`GET /health`)

The health endpoint evaluates critical operational dependencies:
- **Database:** Executes `SELECT 1` on the PostgreSQL connection pool.
- **Cache:** Sends `PING` to Redis.

Returns `200 OK` with `{"status": "ok", "db": "connected", "redis": "connected"}`;
returns `503 Service Unavailable` if any dependency fails.

---

**Related:** [`./runbook.md`](./runbook.md) · [`../04-requirements/non-functional.md`](../04-requirements/non-functional.md)
