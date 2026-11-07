# reportes-analytics — Data Model

## Tables owned

| Table | Entity | Key attributes |
|---|---|---|
| *(none)* | — | This module maintains no dedicated database tables; it calculates read projections |

Because this module owns no tables, all its operations are strictly read-only queries
projected onto the tables owned by `pos_ventas` and `inventario`.

## Invariants

| Invariant | Enforced where |
|---|---|
| Historical sales figures cannot be recalculated with current catalog prices | `reportes_analytics` queries frozen snapshot values in `detalles_venta` |
| Zero write operations to database tables | Pure analytical read models |
| Date range must not exceed 90 days per query | `internal/application/validar_rango_fechas()` |

## Cross-module references

| Column | Points to | Validated by |
|---|---|---|
| `empresa_id` | `auth_tenancy.empresas` | Request token dependency / `AuthTenancyFacade` |

This module reads tables owned by other bounded contexts solely through projection queries
or facade summaries; it never holds foreign keys.

---

**Related:** [`./README.md`](./README.md) · [`../../06-data/models.md`](../../06-data/models.md)
