# QA Report — POS Papelería
**Sistema:** POS Papelería (factory demo — tier basic)  
**Sprint:** 5  
**Fecha review:** 2026-05-20  
**Revisor:** Gemini (Paso 7 del pipeline `build-basic.md`)  
**Resultado:** ✅ **APROBADO** — 0 issues críticos, 3 observaciones menores

---

## Resumen ejecutivo

| Área | Estado | Detalles |
|------|--------|----------|
| Tests automatizados | ✅ 34/34 passing | `pytest` 13 seg — cero fallos |
| Multi-tenancy | ✅ Correcto | Todas las queries filtran `empresa_id` |
| Autenticación JWT | ✅ Correcto | `get_current_user` + UUID parse robusto |
| Soft delete | ✅ Correcto | `is_active=False` — nunca DELETE físico |
| Validación de input | ✅ Correcto | Pydantic v2 + `field_validator` |
| Control de roles | ✅ Correcto | Admin vs Tendero separados |
| Stock concurrencia | ✅ Correcto | `with_for_update()` en venta |
| Serialización JSON | ✅ Correcto | `jsonable_encoder` en validation handler |

---

## Issues críticos (bloqueantes)

> Ninguno. El sistema puede ir a producción.

---

## Observaciones menores (no bloqueantes)

### OBS-01 — `is_active` en tablas del AuditMixin (CORREGIDO)
**Archivo:** `app/models.py` L43  
**Descripción:** `server_default="true"` es texto plano; SQLite lo almacena como
la cadena `'true'`, no el booleano `1`. Esto causaba que `is_active.is_(True)` devolviera
`None` en tests, rompiendo login, auth y todas las queries con ese filtro.  
**Corrección aplicada:** `default=True, server_default="1"` — cross-database compatible.  
**Estado:** ✅ Resuelto

### OBS-02 — UUID como `str` en JWT no convertido a `uuid.UUID` (CORREGIDO)
**Archivo:** `app/dependencies.py` L25–34  
**Descripción:** El payload del JWT devuelve `sub` como `str`. SQLAlchemy's `UUID(as_uuid=True)`
requiere un objeto `uuid.UUID` para generar el SQL correcto en SQLite (`.hex`). Pasar la cadena
directamente causaba `AttributeError: 'str' object has no attribute 'hex'`.  
**Corrección aplicada:** `uuid.UUID(user_id_str)` + captura de `ValueError` en el try/except.  
**Estado:** ✅ Resuelto

### OBS-03 — `empresa_id` requerido en `ProductoCrear` (CORREGIDO)
**Archivo:** `app/schemas/producto.py` L26  
**Descripción:** `empresa_id: UUID` era un campo requerido en el schema de creación, pero el
router lo sobreescribe siempre con `current_user.empresa_id` (seguridad multi-tenant). Esto
causaba 422 en clientes que no enviaran el campo.  
**Corrección aplicada:** `empresa_id: Optional[UUID] = None` — el router sigue overrideando desde JWT.  
**Estado:** ✅ Resuelto

---

## Checklist de seguridad

| Control | Verificación | Resultado |
|---------|-------------|-----------|
| Todas las queries filtran `empresa_id` | Grep en `app/` — confirmado en services + routers + dashboard | ✅ |
| JWT con `SECRET_KEY` de env | `auth_service.py` L13 — `os.getenv("SECRET_KEY")` | ✅ |
| Passwords con bcrypt (salt incluido) | `hash_password()` usa `bcrypt.gensalt()` | ✅ |
| No DELETE físico | Solo `is_active = False` en usuarios y productos | ✅ |
| Tendero no puede crear/eliminar productos | Test `test_tendero_no_puede_crear_producto` + `test_tendero_no_puede_eliminar_producto` → 403 | ✅ |
| Admin solo puede operar en su empresa | `current_user.empresa_id != empresa_id` → 403 | ✅ |
| Stock validado antes de venta | `producto.cantidad_actual < item.cantidad` → 400 | ✅ |
| Carrito vacío rechazado | `@field_validator("items")` + `jsonable_encoder` | ✅ |
| Rollback en error de venta | try/except con `db.rollback()` + `db.flush()` antes de commit | ✅ |
| Concurrencia en stock | `.with_for_update()` en query de producto durante venta | ✅ |

---

## Checklist de calidad de código

| Criterio | Estado |
|----------|--------|
| Capa de servicios separada de routers | ✅ `app/services/` independiente |
| Schemas Pydantic v2 en todas las respuestas | ✅ `from_attributes=True` + `model_validator` |
| `stock_minimo` configurable por producto | ✅ No hardcodeado — campo en `Producto` |
| Dashboard agrega ventas del día por timezone-aware | ✅ `datetime.combine + .replace(tzinfo=timezone.utc)` |
| Ventas filtradas por rango `desde/hasta` | ✅ `obtener_ventas_empresa()` con `Optional[datetime]` |
| `joinedload` en queries de ventas | ✅ Evita N+1 para `detalles` y `usuario` |
| Índices en columnas de filtro frecuente | ✅ `idx_productos_stock_bajo`, `idx_ventas_empresa_fecha` |

---

## Cobertura de tests

| Módulo | Tests | Cobertura funcional |
|--------|-------|---------------------|
| Auth | 9 tests | Registro, login, /me, duplicados, token inválido |
| Dashboard | 5 tests | Métricas reales, multi-tenant, stock bajo dinámico |
| Productos | 9 tests | CRUD, roles, barcode único por empresa, multi-empresa |
| Usuarios | 5 tests | Listar, crear cajero, soft-delete, RBAC |
| Ventas | 6 tests | Happy path, stock insuficiente, carrito vacío, filtros |
| **Total** | **34/34** | **100% passing** |

---

## Recomendaciones para producción (no bloqueantes)

1. **Rate limiting** en `/auth/login` para prevenir brute force — FastAPI + `slowapi`
2. **Refresh tokens** para sesiones largas (actualmente tokens de 30 min sin renovación)
3. **HTTPS obligatorio** — configurar `Secure` en cookies si se migra a sesiones
4. **Logging estructurado** — añadir `structlog` o `loguru` para trazabilidad en producción
5. **Migración a PostgreSQL** antes del primer cliente real — schemas UUID nativo y transacciones ACID completas

---

## Conclusión

El sistema **POS Papelería** supera el criterio de calidad tier basic de la fábrica:
- ✅ Multi-tenant correcto en todos los endpoints
- ✅ Auth JWT robusto con parsing UUID
- ✅ Soft delete consistente
- ✅ 34/34 tests passing en < 15 segundos
- ✅ Stock con protección de concurrencia
- ✅ Roles (admin/tendero) aplicados en todos los endpoints sensibles

**El sistema está listo para demo con cliente.**
