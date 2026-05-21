# MÉTRICAS — ERP Distribuidora (Sprint 6)

> Costo real de tokens y tiempo de construcción del primer sistema demo del Tier Medium  
> generado por el pipeline de la Fábrica de Agentes IA (Claude + Gemini).

---

## Resumen ejecutivo

| Métrica | Valor |
|---------|-------|
| **Tiempo total de construcción** | ~3.5 horas |
| **Tests passing al cierre** | 8/8 ✅ (Suite integral de flujos de negocio) |
| **Issues críticos en QA** | 0 |
| **Modelos usados** | Claude 3.5 Sonnet / Claude 3 Opus / Gemini Free (QA) |
| **Costo estimado en tokens** | ~$0.25 USD (estimado) |

---

## Tiempos por paso del pipeline

| Paso | Descripción | Agente | Tiempo estimado |
|------|-------------|--------|-----------------|
| 1 | Definición de requirements texto libre | Usuario | 15 min |
| 2 | Requisitos estructurados a JSON | Gemini Free | 10 min |
| 3 | Schema DB + contratos API específicos | Claude Sonnet / Opus | 25 min |
| 4 | Backend boilerplate (modelos, esquemas y migraciones) | Claude Sonnet | 30 min |
| 5 | Routers + servicios transaccionales complejos | Claude Sonnet | 45 min |
| 6 | Frontend React 19 JSX (Proveedores, Compras, Deudas, Abonos) | Claude Code (Sonnet) | 40 min |
| 7 | Pruebas de integración integrales de flujo | Claude Sonnet | 25 min |
| 8 | QA completo + qa-report.md | Gemini Free | 15 min |
| 9 | DevOps (Dockerfile, docker-compose.yml, README) | Gemini Free | 10 min |
| 10 | Métricas (este archivo) | Gemini Free | 5 min |
| **Total** | | | **~3.7 horas** |

---

## Costo de tokens (estimado)

| Paso | Modelo | Tokens estimados | Costo estimado |
|------|--------|-----------------|----------------|
| Requirements JSON (Paso 2) | Gemini Free | ~6,000 | $0.00 |
| Schema + API contracts (Paso 3) | Claude Sonnet | ~10,000 | ~$0.030 |
| Backend boilerplate (Paso 4-5) | Claude Sonnet | ~20,000 | ~$0.060 |
| Frontend React JSX (Paso 6) | Claude Code | ~30,000 | ~$0.090 |
| Pruebas de integración (Paso 7) | Claude Sonnet | ~15,000 | ~$0.045 |
| QA completo (Paso 8) | Gemini Free | ~12,000 | $0.00 |
| DevOps & Métricas (Paso 9-10) | Gemini Free | ~8,000 | $0.00 |
| **Total** | | **~101,000** | **~$0.225 USD** |

---

## Bugs y lecciones de arquitectura resueltas

### 1. Parcheo Dinámico de UUID a GUID en SQLite
* **Problema:** SQLite no soporta nativamente el tipo UUID de PostgreSQL, lo cual rompía las llaves primarias y foráneas al correr la suite de pruebas SQLite en memoria.
* **Solución:** Creamos una clase `GUID` personalizada que hereda de `TypeDecorator` y parchea dinámicamente los metadatos de SQLAlchemy al inicio de las pruebas en `conftest.py`.

### 2. Lock de fila (`with_for_update`) al anular compras
* **Problema:** Si se anula una compra de reabastecimiento al mismo tiempo que ocurre una venta, el stock podría quedar con saldo negativo si no hay bloqueo transaccional.
* **Solución:** Implementamos `.with_for_update()` en la consulta del stock de producto dentro de la transacción de anulación, garantizando consistencia atómica y lanzando un `400 Bad Request` si la cantidad en inventario es insuficiente para devolver la mercancía.

### 3. Restricciones de seguridad por Roles a nivel de API
* **Problema:** Los usuarios con rol `asistente` no debían acceder a deudas consolidadas ni ver KPIs de caja del dashboard.
* **Solución:** Implementamos un middleware lógico en las dependencias y routers que valida el JWT del usuario, lanzando un `403 Forbidden` si un `asistente` intenta acceder a los endpoints financieros `/api/cuentas-por-pagar/*` y `/api/dashboard/kpis`.

---

## Comparativa con el objetivo del pipeline (Tier Medium)

| Criterio | Objetivo | Real |
|----------|----------|------|
| Costo de tokens | < $0.80 USD | ~$0.23 USD (Óptimo, gracias a Gemini Free en QA) |
| Tiempo de construcción | < 8 horas | ~3.7 horas (Rendimiento ultra-eficiente) |
| Tests automatizados | Cobertura integral transaccional | 8/8 passing ✅ |
| QA completo | 0 issues críticos | 0 issues críticos ✅ |

---

## ROI proyectado

| Escenario | Costo construcción | Precio al cliente | Margen bruto |
|-----------|-------------------|-------------------|--------------|
| Sistema Medium (ERP Ligero) | ~$0.25 USD | $1,500–$3,500 USD | **99.9%** |
| Con customización de 4h de dev | ~$30 USD | $2,000–$4,000 USD | **98.5%** |

---

*Métricas registradas: 2026-05-21 | Sprint 6 — Fábrica de Agentes IA*
