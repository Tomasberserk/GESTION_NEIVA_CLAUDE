# 04 — User Stories

## Story identifier

`HU-NN` — sequential, two digits, starting at `01`. An id is never reused,
even if a story is dropped or deferred.

## Backlog

| HU-NN | Title | Module | Priority |
|---|---|---|---|
| HU-01 | Autenticación JWT y selección de Tenant | `auth_tenancy` | ⭐ |
| HU-02 | Gestión de Catálogo y códigos de barras por Empresa | `inventario` | ⭐ |
| HU-03 | Alerta preventiva de vencimiento (15 días) | `inventario` | ⭐ |
| HU-04 | Carrito POS y cálculo de subtotales | `pos_ventas` | ⭐ |
| HU-05 | Checkout atómico con bloqueo pesimista (`FOR UPDATE`) | `pos_ventas` | ⭐ |
| HU-06 | Emisión de ticket y snapshot inmutable de venta/vendedor | `pos_ventas` | ⭐ |
| HU-07 | Creación de ticket de soporte helpdesk | `soporte_crm` | — |
| HU-08 | Respuesta de soporte SuperAdmin y gestión de trials | `soporte_crm` | — |
| HU-09 | Reabastecimiento de stock por comando de voz/IA | `agente_ia` | ⭐ |
| HU-10 | Consulta analítica por lenguaje natural | `agente_ia` | — |
| HU-11 | Cierre de caja diario y resumen financiero | `reportes_analytics` | ⭐ |
| HU-12 | Exportación de reporte de ventas a Excel (`openpyxl`) | `reportes_analytics` | — |

## Acceptance criteria highlights

- **HU-01:** Reject unauthenticated requests; inject `empresa_id` into every database operation.
- **HU-02:** Allow identical barcodes across different tenants (`uq_producto_empresa_barras`).
- **HU-03:** Mark products expiring in <= 15 days as critical on the dashboard per **BR-11**.
- **HU-05:** Prevent overselling under concurrent requests using `SELECT ... FOR UPDATE` per **BR-01** and **BR-04**.
- **HU-06:** Freeze `precio_unitario` and `vendedor_nombre_snapshot` permanently per **BR-02**.
- **HU-09:** Process voice audio in Opus/WebM, transcribe via Whisper, and execute idempotent restocking per **BR-12**.

---

**Related:** [`./non-functional.md`](./non-functional.md) · [`./traceability-matrix.md`](./traceability-matrix.md)
