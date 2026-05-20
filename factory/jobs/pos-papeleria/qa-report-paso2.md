# QA Report — POS Papelería Neiva
# Paso 7 del pipeline — Revisión Gemini

**Fecha:** 2026-05-17  
**Revisor:** Gemini (Antigravity)  
**Archivos revisados:** `schema.md`, `api-contracts.md`  
**Veredicto general:** ✅ APROBADO con 2 observaciones menores

---

## Checklist de seguridad multi-tenant

| Criterio | Estado | Detalle |
|----------|--------|---------|
| Todas las tablas tienen `empresa_id` | ✅ | Empresa, Usuario, Producto, Venta. DetalleVenta lo hereda por FK a Venta |
| Todos los endpoints filtran por `empresa_id` | ✅ | Todos los endpoints usan `/{empresa_id}` en la URL |
| Cross-tenant protection | ✅ | El contrato especifica que el `empresa_id` del JWT debe coincidir — implementar verificación en servicio |

## Checklist de autenticación

| Criterio | Estado | Detalle |
|----------|--------|---------|
| Endpoints protegidos con JWT | ✅ | El contrato especifica `Authorization: Bearer` en todos salvo `/auth/login` y `/auth/registro` |
| Control de roles (admin vs tendero) | ✅ | Tabla de permisos completa en la sección "Permisos por rol" |
| Soft delete de usuarios | ✅ | `DELETE /usuarios/{empresa_id}/{usuario_id}` hace `is_active=False` |
| No puede desactivar su propia cuenta | ✅ | Error 403 documentado |

## Checklist de soft delete

| Criterio | Estado | Detalle |
|----------|--------|---------|
| Sin DELETE físico en ninguna tabla | ✅ | Schema usa `is_active=False` en todas las entidades |
| Productos soft-delete | ✅ | `DELETE /productos` → `is_active = false` |
| Usuarios soft-delete | ✅ | `DELETE /usuarios` → `is_active = false` |

## Checklist de diferencias vs Gestión Neiva

| Diferencia | Implementada | Detalle |
|-----------|-------------|---------|
| `stock_minimo` configurable por producto | ✅ | Campo en schema, default 5, presente en GET y POST |
| `usuario_id` en Venta | ✅ | Campo NOT NULL, FK a usuarios con RESTRICT, tomado del JWT automáticamente |
| Sin `fecha_vencimiento` | ✅ | No aparece en el schema |
| `unidad_medida` solo `unidad`/`paquete` | ✅ | Enum correcto, sin gramo/libra/kilo |
| Categorías de papelería | ✅ | 5 categorías correctas del requirements.json |
| Dashboard usa `cantidad_actual <= stock_minimo` | ✅ | Lógica correcta documentada en el contrato |

## Checklist Excel/Reportes

| Criterio | Estado | Detalle |
|----------|--------|---------|
| Columna Cajero en Excel | ✅ | El reporte incluye `Cajero` — valor agregado vs Gestión Neiva |
| Columna Categoría en Excel | ✅ | Incluida — útil para la papelería |
| Solo admin puede exportar | ✅ | 403 si no es admin |

---

## Observaciones (no bloquean avance)

### OBS-01 — Nivel: MEDIO
**`POST /auth/login` usa form-data, pero Gestión Neiva usa JSON**

El contrato define el login con `application/x-www-form-urlencoded` (OAuth2 estándar),
pero el frontend de Gestión Neiva envía JSON. Si se va a reutilizar el AuthContext del
template, el endpoint debería aceptar JSON también.

**Recomendación para Claude (Paso 3-4):** implementar el login aceptando JSON
(igual que en Gestión Neiva: `LoginForm` con `email` + `password` en body JSON)
en lugar de form-data OAuth2. Más consistente con el frontend React.

### OBS-02 — Nivel: BAJO
**`GET /ventas` usa `desde`/`hasta` pero Gestión Neiva usa `fecha_inicio`/`fecha_fin`**

Inconsistencia de nomenclatura entre sistemas. No es un problema para POS Papelería
(es un sistema independiente), pero si en el futuro se comparten componentes frontend,
conviene unificar.

**Recomendación:** mantener `desde`/`hasta` — es más legible en español. Documentar
la diferencia para no mezclar en el futuro.

---

## Issues críticos

**Ninguno.** El diseño es sólido y ejecutable.

---

## Próximos pasos (Pasos 3-6 para Claude)

Para el Paso 3 (Haiku — backend boilerplate), Claude debe:

1. Copiar `app/models.py` de Gestión Neiva y adaptar:
   - Agregar `stock_minimo = Column(Integer, default=5)` en Producto
   - Agregar `usuario_id` en Venta (FK a usuarios, RESTRICT)
   - Cambiar `UnidadMedida` a solo `unidad`/`paquete`
   - Cambiar `CategoriaProducto` a las 5 categorías de papelería
   - Quitar `fecha_vencimiento` de Producto

2. El migration `001_init.py` debe crear todas las tablas con sus índices

Para el Paso 5 (Sonnet — frontend), el `CartContext` de Gestión Neiva
es reutilizable directamente. Solo adaptar:
   - Categorías del modal de producto
   - Etiquetas de UI ("Papelería" en lugar de "TiendApp")
   - Sin campos de peso ni vencimiento en el modal

---

## Métricas del Paso 7

| Métrica | Valor |
|---------|-------|
| Tiempo de review | ~15 min |
| Costo IA | $0.00 (Gemini free) |
| Issues críticos | 0 |
| Observaciones menores | 2 |
| Veredicto | ✅ CONTINUAR AL PASO 3 |
