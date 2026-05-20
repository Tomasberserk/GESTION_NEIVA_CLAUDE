# PLAN ACTIVO — Gestión Neiva + Fábrica de Agentes IA

**Fecha:** 2026-05-20  
**Sprint activo:** Sprint 6 — Template medium  
**Próxima revisión:** Fin de Sprint 6

> Este documento es **mutable por Claude y Gemini**. Ver `AGENTS.md` para el protocolo de cambios.  
> Usa `> [GEMINI PROPONE]` o `> [CLAUDE PROPONE]` para proponer cambios sin implementarlos aún.

---

## Estado general

```
[✅] Sprint 2 — Auth funcional, layout conectado, bugs críticos resueltos
[✅] Sprint 3 — MVP cerrado (flujo end-to-end en producción verificado)
[✅] Sprint 3.5 — Features gancho: vencimiento, granel, categorías, escáner
[✅] Sprint 3.6 — Historial de ventas con tabs y filtro por fecha
[✅] Sprint 3.8 — Cierre brechas SRS: categorías, escáner, responsividad
[✅] Sprint 4 — Fundamentos de la fábrica (docs + templates + workflows)
[✅] Sprint 5 — Pipeline funcional tier basic (COMPLETO)
[🔄] Sprint 6 — Template medium (SIGUIENTE)
[⏳] Sprint 7 — Template professional + Hermes activado
```

---

## Sprint 5 — Pipeline funcional tier basic

**Objetivo:** ejecutar el pipeline `build-basic.md` de punta a punta con un sistema demo real, medir costos reales y tener algo que mostrar a un primer cliente.

**La meta concreta:** construir **"POS Papelería"** — un segundo sistema básico usando la fábrica, que sirva como demo y validación del pipeline.

| # | Tarea | Archivo | Estado |
|---|-------|---------|--------|
| 1 | Definir requirements de POS Papelería (texto libre) | `factory/jobs/pos-papeleria/requirements.txt` | ✅ |
| 2 | [Gemini] Analizar requirements → JSON estructurado | `factory/jobs/pos-papeleria/requirements.json` | ✅ |
| 3 | [Architect] Schema DB + contratos API adaptados | `factory/jobs/pos-papeleria/schema.md` + `api-contracts.md` | ✅ |
| 4 | [Haiku] Backend: models + schemas + migration | `factory/jobs/pos-papeleria/` | ✅ |
| 5 | [Haiku] Backend: routers + services | `factory/jobs/pos-papeleria/` | ✅ |
| 6 | [Sonnet] Frontend adaptado | `factory/jobs/pos-papeleria/` | ✅ |
| 7 | [Gemini] QA review completo | `factory/jobs/pos-papeleria/qa-report.md` | ✅ |
| 8 | [Haiku] DevOps: docker-compose + README deploy | `factory/jobs/pos-papeleria/` | ✅ |
| 9 | Medir costo real en tokens y tiempo | `factory/jobs/pos-papeleria/METRICAS.md` | ✅ |
| 10 | Landing page simple para mostrar el portafolio | `docs/landing/` o Notion público | ⏳ pendiente Sprint 6 |

### Criterios de éxito Sprint 5

1. POS Papelería corre en local: `login → inventario → venta → reporte`
2. Costo real de tokens documentado en `METRICAS.md`
3. Tiempo real de construcción documentado (debe ser < 4 horas)
4. QA report sin issues críticos
5. Hay algo que mostrarle a un potencial cliente (demo o landing)

### Resultado Sprint 5

✅ **34/34 tests passing** — 0 issues críticos en QA  
✅ `qa-report.md`, `docker-compose.yml`, `README.md`, `METRICAS.md` entregados  
✅ Costo real: ~$0.22 USD | Tiempo: ~4.5 horas  

### Próximo paso (Sprint 6)

> Definir template medium: módulos de proveedores, compras, cuentas por pagar.


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
| 3 | RF-04 | Responsividad móvil — layout y componentes adaptados a pantalla pequeña | ✅ Hecho |

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

_(Sin propuestas pendientes — todas implementadas)_

---

## Historial de propuestas implementadas

> [GEMINI PROPONE → ✅ CLAUDE IMPLEMENTA] Validar límite de stock en CartContext.agregar()
> **Solución:** `CartContext.jsx` — en `agregar()`, si `existe.cantidad >= producto.cantidad_actual` retorna `prev` sin modificar. El botón "+" queda silenciosamente deshabilitado al llegar al stock disponible.

> [GEMINI PROPONE → ✅ CLAUDE IMPLEMENTA] Refrescar listado de productos post-checkout
> **Solución:** Evento `window` desacoplado — `CartSidebar.jsx` dispara `new Event('venta-completada')` post-checkout. `Inventario.jsx` escucha el evento con `useEffect` y llama `cargar()`. Evita acoplar contextos y no requiere ProductosContext global.


