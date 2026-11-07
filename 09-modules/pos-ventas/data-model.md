# pos-ventas — Data Model

## Tables owned

| Table | Entity | Key attributes |
|---|---|---|
| `ventas` | Venta | id (UUID), empresa_id, fecha_venta, total, usuario_id (UUID), vendedor_nombre_snapshot, is_active |
| `detalles_venta` | DetalleVenta | id (UUID), venta_id (FK), producto_id (UUID), cantidad, precio_unitario, subtotal, is_active |

## Invariants

| Invariant | Enforced where |
|---|---|
| `BR-02`: Price snapshot is immutable upon insertion | `detalles_venta.precio_unitario` never updated |
| `BR-04`: Checkout and stock reduction commit in one transaction | `VentasFacade.procesar_venta()` |
| `BR-06`: Total equals sum of line subtotals | Calculated at sale emission |

## Cross-module references

| Column | Points to | Validated by |
|---|---|---|
| `detalles_venta.producto_id` | `inventario.productos` | `InventarioFacade.validar_y_descontar_stock_atomic()` |
| `ventas.usuario_id` | `auth_tenancy.usuarios` | `AuthTenancyFacade.obtener_usuario()` |

Per **ADR-004**, references are stored as plain UUID columns without database FK constraints.

---

**Related:** [`./README.md`](./README.md) · [`../../06-data/models.md`](../../06-data/models.md)
