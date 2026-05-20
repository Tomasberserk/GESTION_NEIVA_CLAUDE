# MÉTRICAS — POS Papelería (Sprint 5)

> Costo real de tokens y tiempo de construcción del primer sistema demo  
> generado por el pipeline `build-basic.md` de la Fábrica de Agentes IA.

---

## Resumen ejecutivo

| Métrica | Valor |
|---------|-------|
| **Tiempo total de construcción** | ~4 horas (sesión fragmentada) |
| **Tests passing al cierre** | 34/34 ✅ |
| **Issues críticos en QA** | 0 |
| **Modelo principal usado** | Claude Sonnet / Gemini Pro |
| **Costo estimado en tokens** | ~$0.18–0.25 USD (estimado) |

---

## Tiempos por paso del pipeline

| Paso | Descripción | Agente | Tiempo estimado |
|------|-------------|--------|-----------------|
| 1 | Requirements → texto libre | Usuario | 15 min |
| 2 | Requirements → JSON estructurado | Gemini | 10 min |
| 3 | Schema DB + contratos API | Claude Sonnet | 20 min |
| 4 | Backend boilerplate (models, schemas, migrations) | Claude Sonnet | 25 min |
| 5 | Routers + services | Claude Sonnet | 30 min |
| 6 | Frontend (páginas, hooks, contexto) | Claude Sonnet | 40 min |
| 6b | Debugging tests (blocker: SQLite + UUID + bool) | Claude Sonnet + Gemini | ~90 min |
| 7 | QA review + qa-report.md | Gemini | 20 min |
| 8 | DevOps: docker-compose + README + .env.example | Claude Sonnet | 15 min |
| 9 | Métricas (este archivo) | Claude Sonnet | 5 min |
| **Total** | | | **~4.5 horas** |

---

## Costo de tokens (estimado)

> Nota: Los costos exactos de tokens requieren instrumentación directa de la API.
> Las cifras siguientes son estimaciones basadas en el tamaño del código generado
> y los modelos utilizados.

| Paso | Modelo | Tokens estimados | Costo estimado |
|------|--------|-----------------|----------------|
| Requirements JSON (Paso 2) | Gemini Free | ~5,000 | $0.00 |
| Schema + API contracts (Paso 3) | Claude Sonnet | ~8,000 | ~$0.024 |
| Backend boilerplate (Paso 4-5) | Claude Sonnet | ~15,000 | ~$0.045 |
| Frontend (Paso 6) | Claude Sonnet | ~20,000 | ~$0.060 |
| Debugging (Paso 6b) | Claude Sonnet | ~25,000 | ~$0.075 |
| QA review (Paso 7) | Gemini Free | ~10,000 | $0.00 |
| DevOps (Paso 8-9) | Claude Sonnet | ~5,000 | ~$0.015 |
| **Total** | | **~88,000** | **~$0.22 USD** |

---

## Bugs encontrados y resueltos durante el pipeline

| # | Bug | Causa raíz | Corrección |
|---|-----|-----------|-----------|
| 1 | `no such table: usuarios` | SQLite in-memory con connection pool aislado | `StaticPool` en `conftest.py` |
| 2 | `ModuleNotFoundError: No module named 'conftest'` | `PYTHONPATH` no incluía directorio `tests/` | `$env:PYTHONPATH=".;tests"` |
| 3 | `401 Unauthorized` en login (is_active filter) | `server_default="true"` incompatible con SQLite — se almacena como string, no booleano | `default=True, server_default="1"` |
| 4 | `AttributeError: 'str' object has no attribute 'hex'` | JWT `sub` devuelve string; SQLAlchemy UUID necesita objeto `uuid.UUID` | `uuid.UUID(user_id_str)` en `dependencies.py` |
| 5 | `422 Unprocessable Entity` en crear producto | `empresa_id` requerido en schema pero router siempre lo overridea desde JWT | `Optional[UUID] = None` en `ProductoCrear` |
| 6 | `TypeError: Object of type ValueError is not JSON serializable` | Pydantic validator lanza `ValueError` que JSON nativo no puede serializar | `jsonable_encoder(exc.errors())` en exception handler |

---

## Lecciones aprendidas para el pipeline

### Para el template basic (mejoras futuras)

1. **`is_active` boolean cross-DB**: Siempre usar `default=True, server_default="1"` en el `AuditMixin` para compatibilidad SQLite/PostgreSQL.

2. **UUID en JWT**: El template debe incluir `uuid.UUID(payload.get("sub"))` desde el inicio en `dependencies.py`.

3. **`empresa_id` en schemas de creación**: Marcar como `Optional` desde el template — el router siempre lo sobreescribe desde JWT.

4. **`jsonable_encoder` en validation handler**: Siempre usar en el `RequestValidationError` handler para evitar serialization errors de validators personalizados.

5. **`PYTHONPATH` en pytest**: Documentar en `pytest.ini` o `conftest.py` que se debe incluir tanto `.` como `tests`.

---

## Comparativa con el objetivo del pipeline

| Criterio | Objetivo | Real |
|----------|----------|------|
| Costo de tokens | < $0.21 USD | ~$0.22 USD (ligeramente sobre — debugging extra) |
| Tiempo de construcción | < 4 horas | ~4.5 horas (debugging inesperado de SQLite) |
| Tests automatizados | Presentes | 34/34 passing ✅ |
| QA sin issues críticos | Requerido | 0 issues críticos ✅ |
| Demo funcional | Requerido | Backend verificado, frontend generado ✅ |

**Nota:** El costo y tiempo extra se debieron a bugs en la interacción SQLite + SQLAlchemy UUID + boolean — bugs de plataforma que el template corregido ya no tendrá.

---

## ROI proyectado

| Escenario | Costo construcción | Precio al cliente | Margen bruto |
|-----------|-------------------|-------------------|--------------|
| Sistema básico (tier basic) | ~$0.25 USD | $300–$800 USD | **99.9%** |
| Con customización 2h de dev | ~$15 USD | $500–$1,000 USD | **98.5%** |

---

*Métricas registradas: 2026-05-20 | Sprint 5 — Fábrica de Agentes IA*
