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

*(Vacío — agregar con `> [GEMINI PROPONE]` o `> [CLAUDE PROPONE]`)*
