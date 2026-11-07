# inventario — Data Model

## Tables owned

| Table | Entity | Key attributes |
|---|---|---|
| `productos` | Producto | id (UUID), empresa_id, codigo_barras, nombre, precio_costo, precio_venta, cantidad_actual, unidad_medida, fecha_vencimiento, categoria, is_active |

## Invariants

| Invariant | Enforced where |
|---|---|
| `BR-01`: Stock count is never negative | `InventarioFacade.validar_y_descontar_stock_atomic()` |
| `BR-05`: Products with historical sales are soft-deleted | `internal/application/eliminar_producto.py` |
| `BR-10`: Barcode is unique per tenant (`uq_producto_empresa_barras`) | Database unique constraint |
| `BR-11`: Products with `fecha_vencimiento <= now() + 15 days` trigger alert | Query scope in `obtener_productos_por_vencer()` |

## Cross-module references

| Column | Points to | Validated by |
|---|---|---|
| `empresa_id` | `auth_tenancy.empresas` | Request token dependency / `AuthTenancyFacade` |

No foreign key constraint is declared on `empresa_id` across schemas per **ADR-004**.

---

**Related:** [`./README.md`](./README.md) · [`../../06-data/models.md`](../../06-data/models.md)
