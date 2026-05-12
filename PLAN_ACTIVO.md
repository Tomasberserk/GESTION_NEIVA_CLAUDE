# PLAN ACTIVO — Gestión Neiva + Fábrica de Agentes IA

**Fecha:** 2026-05-11  
**Sprint activo:** Sprint 3 (cierre MVP) + Sprint 4 fundamentos fábrica  
**Próxima revisión:** Fin de Sprint 3

> Este documento es **mutable por Claude y Gemini**. Ver `AGENTS.md` para el protocolo de cambios.  
> Usa `> [GEMINI PROPONE]` o `> [CLAUDE PROPONE]` para proponer cambios sin implementarlos aún.

---

## Estado general

```
[✅] Sprint 2 — Auth funcional, layout conectado, bugs críticos resueltos
[🔄] Sprint 3 — Cierre MVP (en progreso)
[🔄] Sprint 4 — Fundamentos de la fábrica (en progreso en paralelo)
[⏳] Sprint 5 — Pipeline funcional tier basic
[⏳] Sprint 6 — Template medium
[⏳] Sprint 7 — Template professional + Hermes activado
```

---

## Sprint 3 — Cierre MVP Gestión Neiva

**Objetivo:** ciclo completo `login → inventario → venta → reporte` funciona sin errores.

| # | Tarea | Archivo | Estado |
|---|-------|---------|--------|
| 1 | CartSidebar en el layout | `Layout.jsx` | ✅ Hecho |
| 2 | Fix unique barcode global → por empresa | `models.py` + migration 002 | ✅ Hecho |
| 3 | Dashboard con métricas reales | `Dashboard.jsx` + `routers/dashboard.py` | ✅ Hecho |
| 4 | Correr migration 002 en BD | `alembic upgrade head` | ⏳ Pendiente |
| 5 | Probar flujo end-to-end | Manual: login → producto → venta | ⏳ Pendiente |
| 6 | Tests auth básicos | `tests/test_auth.py` | ⏳ Pendiente |
| 7 | Script arranque entorno | `dev.sh` o `Makefile` | ⏳ Pendiente |

### Criterios de éxito Sprint 3

1. Login en `localhost:5173` funciona sin errores
2. Crear producto → aparece en la grilla
3. Click "Agregar" → CartSidebar aparece con el item
4. Finalizar venta → stock descontado, aparece en historial
5. Exportar Excel desde Reportes → descarga archivo válido
6. Dashboard muestra números reales (no "—")
7. Otro usuario en otra empresa puede registrarse y operar su propia tienda

---

---

## Sprint 3.5 — Features "Gancho" para MVP (Alta Prioridad)

**Objetivo:** Implementar analítica, fechas de vencimiento y soporte para productos a granel para aumentar el valor percibido del MVP Básico.

| # | Tarea | Responsable | Estado |
|---|-------|-------------|--------|
| 1 | Migración DB: `cantidad` a `Numeric`, añadir `fecha_vencimiento` y `unidad_medida` (Enum: unidad, gramo, libra, kilo) | Claude | ✅ Hecho |
| 2 | Endpoints Dashboard (Top productos, Alertas vencimiento a 15 días fijos) | Claude | ✅ Hecho |
| 3 | Actualizar ModalProducto (nuevos campos, input fecha y selector de medida) | Claude | ✅ Hecho |
| 4 | Modificar CartSidebar para permitir fracciones en granel según medida | Claude | ✅ Hecho |
| 5 | Gráficas en Dashboard (Recharts) y panel rojo de vencimientos | Claude | ✅ Hecho |

### Criterios de éxito Sprint 3.5
1. Dashboard muestra gráfica de los 5 productos más vendidos.
2. Dashboard muestra alerta roja para productos que vencen en 15 días o menos.
3. Se puede crear un producto seleccionando unidad de medida (ej. Libra) y fecha de vencimiento opcional.
4. En el POS (CartSidebar), si un producto es por peso, se puede ingresar "1.5" y calcula el subtotal.

---

## Sprint 4 — Fundamentos de la fábrica

**Objetivo:** infraestructura de documentación y agentes para que la fábrica pueda operar.

| # | Tarea | Archivo | Estado |
|---|-------|---------|--------|
| 1 | CLAUDE.md completo | `CLAUDE.md` | ✅ Hecho |
| 2 | GEMINI.md (contexto para Antigravity) | `GEMINI.md` | ✅ Hecho |
| 3 | AGENTS.md (protocolo colaboración) | `AGENTS.md` | ✅ Hecho |
| 4 | PLAN_ACTIVO.md (este archivo) | `PLAN_ACTIVO.md` | ✅ Hecho |
| 5 | `.claude/settings.json` MCP servers | `.claude/settings.json` | ✅ Hecho |
| 6 | Agente haiku-worker | `.claude/agents/haiku-worker.md` | ✅ Hecho |
| 7 | Agente architect | `.claude/agents/architect.md` | ✅ Hecho |
| 8 | factory/README.md | `factory/README.md` | ✅ Hecho |
| 9 | Template basic (4 docs) | `factory/templates/basic/` | ✅ Hecho |
| 10 | Pipeline build-basic | `factory/workflows/build-basic.md` | ✅ Hecho |
| 11 | Portafolio de precios | `factory/pricing/PORTFOLIO.md` | ✅ Hecho |
| 12 | Actualizar VISION_Y_ROADMAP.md | `docs/VISION_Y_ROADMAP.md` | ✅ Hecho |

### Criterios de éxito Sprint 4

1. Nueva sesión Claude Code carga contexto completo sin handoff manual
2. Gemini puede leer GEMINI.md y PLAN_ACTIVO.md y contribuir al plan
3. `factory/templates/basic/` tiene los 4 documentos de referencia
4. El pipeline `build-basic.md` es ejecutable paso a paso

---

## Sprint 3.6 — Mini-refactor Historial de Ventas (UX cuadre de caja)

**Objetivo:** Vista de Ventas con 3 tabs (Hoy / Semana / Histórico) y filtro por fecha en el backend.

| # | Tarea | Archivo | Estado |
|---|-------|---------|--------|
| 1 | Endpoint ventas con `fecha_inicio` / `fecha_fin` query params | `routers/ventas.py`, `services/venta_service.py` | ✅ Hecho |
| 2 | UI tabs + TotalBanner + ExcelExport (tab Histórico) | `pages/Ventas.jsx` | ✅ Hecho |

---

## Sprint 3.8 — Cierre de Brechas SRS

**Objetivo:** Cubrir los requisitos funcionales RF-02 y RF-03 del SRS antes del despliegue.

| # | Paso | Descripción | Estado |
|---|------|-------------|--------|
| 1 | RF-02 | Categorías de productos — enum + migration 005 + selector en modal | ✅ Hecho |
| 2 | RF-03 | Escáner de código de barras via cámara (`@zxing/browser`) | ✅ Hecho |
| 3 | RF-04 | Responsividad móvil — layout y componentes adaptados a pantalla pequeña | ⏳ Pendiente |

### Criterios de éxito Sprint 3.8
1. Se puede asignar categoría al crear/editar un producto.
2. Al pulsar 📷 en el modal, la cámara detecta un código EAN/UPC y lo auto-rellena.
3. El POS es usable en móvil (mínimo 375 px de ancho).

---

## Sprint 5 — Pipeline funcional tier basic (próximo)

- `factory/workflows/build-basic.md` como workflow ejecutable real
- Generar un segundo sistema básico usando el pipeline (demo para clientes)
- Medir costo real en tokens por sistema construido
- Primer cliente Gestión Neiva pagando → **desbloquea Hermes-3**

---

## Sprint 6 — Template medium

- Definir y construir template medium (ERP ligero)
- Módulos adicionales: proveedores, compras, cuentas por pagar
- Probar construcción con la fábrica

---

## Sprint 7 — Template professional + Hermes activado

- Template professional: multi-tenant real, pagos, SSO, API pública
- **Activar Hermes-3 vía Together AI** (primer ingreso recurrente confirmado)
- Documentación pública del portafolio
- Landing page con los tres tiers

---

## Restricciones activas

- **Hermes-3 / Together AI:** BLOQUEADO hasta primer ingreso de Gestión Neiva
- **Ollama local:** descartado permanentemente (degrada rendimiento del equipo)
- **Stack de fábrica:** solo Claude + Gemini (free) hasta que el sistema facture
- **Sin TypeScript:** frontend en JSX puro mientras sea MVP

---

## Propuestas pendientes de evaluación

> [GEMINI PROPONE] Validar límite de stock en CartContext.agregar()
> **Motivo:** Actualmente se pueden agregar unidades infinitas usando el botón "+" del carrito, lo que permite sobreventa y posibles errores 400 en el backend.
> **Propuesta:** En `frontend/src/context/CartContext.jsx`, dentro de la función `agregar()`, validar que la cantidad en el carrito no supere a `producto.cantidad_actual` antes de incrementar. Ej: `if (existe && existe.cantidad >= producto.cantidad_actual) return prev;`

> [GEMINI PROPONE] Refrescar listado de productos post-checkout
> **Motivo:** Al finalizar una venta exitosa en `CartSidebar.jsx`, el inventario visual queda desactualizado mostrando el stock viejo en las tarjetas de producto.
> **Propuesta:** Forzar una recarga del estado de productos cuando la promesa de `registrar(detalles)` sea exitosa para mantener sincronía entre stock real y visual en la interfaz.
