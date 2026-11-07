# 02 — Entities and Rules

## Entities

| Entity | Key attributes | Invariants |
|---|---|---|
| Empresa | id, nombre_comercial, nit_o_cedula, plan, trial_expires_at, is_active | NIT/cédula is unique across platform; trial date cannot be in the past when creating |
| Usuario | id, email, hashed_password, empresa_id, rol, nombre, telefono_whatsapp | Email is globally unique; cashier role cannot access admin reports or settings |
| Producto | id, empresa_id, codigo_barras, nombre, precio_costo, precio_venta, cantidad_actual, unidad_medida | Barcode unique per tenant; prices cannot be negative; stock >= 0 per **BR-01** |
| Venta | id, empresa_id, fecha_venta, total, usuario_id, vendedor_nombre_snapshot | Total equals the sum of line subtotals; cashier name snapshot is immutable |
| DetalleVenta | id, venta_id, producto_id, cantidad, precio_unitario, subtotal | Subtotal = cantidad * precio_unitario; price snapshot never changes |
| SoporteTicket | id, empresa_id, usuario_id, asunto, estado | Must link to an active tenant; state transitions: abierto -> respondido -> cerrado |
| SoporteMensaje | id, ticket_id, remitente_rol, remitente_email, mensaje, created_at | Body cannot be empty; sender role is either superadmin or usuario |
| AgentCommand | id, empresa_id, conversation_id, command_id, action, status, result | Command ID is unique per tenant per **BR-12**; execution is strictly idempotent |

## Business rules

1. **BR-01** — A sale cannot process if `producto.cantidad_actual < cantidad_solicitada`. Lanza HTTP 422.
2. **BR-02** — At checkout, unit price and product name are frozen in `DetalleVenta`; later catalog changes do not alter historical sales.
3. **BR-03** — Every query and mutation filters strictly by `empresa_id` (Zero Leakage). Cross-tenant queries return 404 or 403.
4. **BR-04** — Checkout and stock reduction occur in a single ACID transaction protected by pessimistic row locking (`SELECT ... FOR UPDATE`).
5. **BR-05** — Entities with transaction history (`Producto`, `Usuario`, `Empresa`) are never hard-deleted; only deactivated (`is_active = False`).
6. **BR-06** — The sale total is derived from the sum of its items; no redundant mutable column overrides the lines.
7. **BR-07** — Basic plan permits at most 3 active cashiers (`MAX_CAJEROS_BASIC = 3`); Pro and higher plans permit unlimited active cashiers.
8. **BR-08** — When `now() > trial_expires_at` without an active paid plan, write operations return 403 Forbidden.
9. **BR-09** — Voice/AI endpoints (`/agente/*`) reject requests from tenants without Pro or Premium plans.
10. **BR-10** — `codigo_barras` is unique per tenant (`uq_producto_empresa_barras`), allowing different stores to stock identical barcodes.
11. **BR-11** — Products with `fecha_vencimiento <= (today + 15 days)` are classified as critical expiration alerts.
12. **BR-12** — AI voice commands enforce idempotency via `command_id`; duplicate submissions return cached results without re-executing.

## Where a rule is enforced

Every `BR-NN` rule lives in the module that owns the entity it governs — see
[`module-boundaries.md`](./module-boundaries.md).

---

**Related:** [`./domain-map.md`](./domain-map.md) · [`./module-boundaries.md`](./module-boundaries.md)
