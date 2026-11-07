# 06 — Migrations

## Migration strategy

Gestión Neiva uses **Alembic** to manage a single ordered history for the database.
Every schema change is tracked in `alembic/versions/` and applied sequentially via
`alembic upgrade head`.

## Ordered version history

| Rev | Script | Scope | Purpose |
|---|---|---|---|
| 001 | `001_initial_schema.py` | `auth_tenancy`, `inventario`, `pos_ventas` | Initial schema: empresas, usuarios, productos, ventas, detalles |
| 002 | `002_barcode_unique_por_empresa.py` | `inventario` | Scopes barcode unique constraint per tenant (`uq_producto_empresa_barras`) |
| 003 | `003_trial_y_plan_empresa.py` | `auth_tenancy` | Adds `trial_expires_at` and subscription `plan` to `empresas` |
| 004 | `004_cantidad_numeric_vencimiento_unidad.py`| `inventario` | Decimal precision for bulk stock (`granel`) and expiration date |
| 005 | `005_add_categoria_producto.py` | `inventario` | Adds `categoria` enum to `productos` |
| 006 | `006_crear_tablas_soporte.py` | `soporte_crm` | Creates `soporte_tickets` and `soporte_mensajes` tables |
| 007 | `007_factory_launcher_sso.py` | `auth_tenancy` | SSO launcher credentials column |
| 008 | `008_erp_monolito.py` | `erp` *(deprecated)* | Temporary ERP tables (compras, cxp) |
| 009 | `009_whatsapp_vinculacion.py` | `auth_tenancy` | Adds `telefono_whatsapp` to `usuarios` |
| 010 | `010_crear_tabla_agent_commands.py` | `agente_ia` | Creates `agent_commands` table for FSM idempotency |
| 011 | `011_remover_modulos_erp.py` | `system` | **Pruned ERP tables permanently** (`compras`, `cxp`, `abonos`, `proveedores`) |
| 012 | `012_rbac_nombre_usuario_y_trazabilidad_ventas.py` | `auth_tenancy`, `pos_ventas` | Adds `nombre` in usuarios and `vendedor_nombre_snapshot` in ventas |
| 013 | `013_desacoplar_fks_entre_modulos.py` *(planned)* | `pos_ventas`, `soporte_crm` | Drops cross-module DB foreign keys per **ADR-004** |

## Rollback rules

Every migration file must supply a matching `downgrade()` function. In CI, every pull
request applying a migration is tested bidirectionally (`upgrade head` -> `downgrade -1` -> `upgrade head`).

---

**Related:** [`./database-conventions.md`](./database-conventions.md) · [`./models.md`](./models.md)
