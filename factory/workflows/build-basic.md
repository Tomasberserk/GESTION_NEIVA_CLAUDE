# Pipeline — Construir sistema tier basic

> Workflow ejecutable para generar un sistema POS simple con la fábrica de agentes IA.  
> Tiempo estimado: 2–4 horas. Costo IA estimado: ~$0.21.

---

## Antes de empezar

**Checklist de prerequisites:**
- [ ] Requirements del cliente documentados en texto libre
- [ ] `factory/templates/basic/customization-checklist.md` completado
- [ ] Nombre del sistema definido (se usa como `{sistema}` en los paths)
- [ ] Stack confirmado: FastAPI + React + PostgreSQL

**Crear directorio del job:**
```bash
mkdir -p factory/jobs/{sistema}
cp factory/templates/basic/customization-checklist.md factory/jobs/{sistema}/
```

---

## Paso 1 — Gemini: analizar requirements (gratis, ~5 min)

**Input:** documento de requirements del cliente en lenguaje natural  
**Output:** `factory/jobs/{sistema}/requirements.json`

**Prompt para Gemini:**
```
Lee el siguiente documento de requirements y extrae en formato JSON:
- "entidades": lista de objetos del negocio con sus atributos
- "modulos": lista de módulos del sistema con descripción
- "reglas_negocio": lista de reglas y restricciones
- "flujos_principales": los 3-5 flujos de usuario más importantes
- "integraciones": sistemas externos necesarios
- "exclusiones": qué NO debe hacer el sistema

Documento: [pegar requirements del cliente]
```

---

## Paso 2 — Architect: diseño del sistema (~$0.05, ~30 min)

**Input:** `factory/jobs/{sistema}/requirements.json` + `factory/templates/basic/schema.md`  
**Output:**
- `factory/jobs/{sistema}/schema.md` — modelo de datos adaptado
- `factory/jobs/{sistema}/api-contracts.md` — endpoints del sistema

**Spawnar agente architect:**
```
Invoke: .claude/agents/architect.md
Task: "Diseña el sistema {sistema} basado en el template basic.
       Adapta el schema y los contratos API según requirements.json.
       Documenta todas las desviaciones del template estándar."
```

**Validar antes de continuar:**
- [ ] Todas las tablas tienen `empresa_id` (multi-tenant)
- [ ] Todas las tablas tienen `is_active` (soft delete)
- [ ] El `customization-checklist.md` está reflejado en el schema

---

## Paso 3 — Haiku: backend boilerplate (~$0.02, ~20 min)

**Input:** `factory/jobs/{sistema}/schema.md`  
**Output:** modelos, schemas, migration inicial

**Spawnar haiku-worker:**
```
Invoke: .claude/agents/haiku-worker.md
Task: "Genera app/models.py, app/schemas/ y alembic/versions/001_init.py
       para el sistema {sistema} según factory/jobs/{sistema}/schema.md.
       Seguir el patrón de Gestión Neiva (app/models.py de referencia)."
```

**Verificar:**
```bash
.venv/bin/python -c "from app import models; print('OK')"
.venv/bin/alembic upgrade head
```

---

## Paso 4 — Haiku: routers y services (~$0.03, ~25 min)

**Input:** `factory/jobs/{sistema}/api-contracts.md` + `app/models.py`  
**Output:** `app/routers/`, `app/services/`

**Spawnar haiku-worker:**
```
Invoke: .claude/agents/haiku-worker.md
Task: "Genera app/routers/ y app/services/ para {sistema}
       según factory/jobs/{sistema}/api-contracts.md.
       Incluir auth, productos, ventas, dashboard, reportes."
```

**Verificar:**
```bash
.venv/bin/uvicorn app.main:app --reload
curl http://localhost:8000/health
# Probar endpoints en http://localhost:8000/docs
```

---

## Paso 5 — Sonnet: frontend (~$0.08, ~45 min)

**Input:** `factory/jobs/{sistema}/api-contracts.md` + `factory/templates/basic/components-list.md`  
**Output:** `frontend/src/`

**Tarea para Claude Sonnet:**
```
Genera el frontend completo para {sistema} basado en el template basic de Gestión Neiva.
Adaptar según customization-checklist.md.
Mantener JSX puro (sin TypeScript), React 19, TailwindCSS v4.
```

**Verificar:**
```bash
cd frontend && npm run dev
# Probar: login → inventario → venta → reporte
```

---

## Paso 6 — Haiku: tests (~$0.02, ~15 min)

**Input:** `app/routers/`, `app/services/`  
**Output:** `tests/`

**Spawnar haiku-worker:**
```
Invoke: .claude/agents/haiku-worker.md
Task: "Genera tests de integración para {sistema}.
       Mínimo: test_auth.py (registro, login, /me),
       test_ventas.py (venta completa con descuento de stock).
       Usar pytest + TestClient + base de datos de test separada."
```

**Verificar:**
```bash
.venv/bin/pytest tests/ -v
```

---

## Paso 7 — Gemini: QA review (gratis, ~20 min)

**Input:** todo el código generado  
**Output:** `factory/jobs/{sistema}/qa-report.md`

**Prompt para Gemini:**
```
Revisa el sistema {sistema} completo y genera un reporte de calidad.
Verificar:
1. Multi-tenant: ¿todas las queries filtran por empresa_id?
2. Autenticación: ¿todos los endpoints protegidos usan Depends(get_current_user)?
3. Soft delete: ¿se usa is_active=False en lugar de DELETE?
4. Frontend: ¿el carrito funciona? ¿el token se envía en todas las requests?
5. Tests: ¿cubren los flujos críticos?
6. Seguridad básica: ¿hay SQL injection, XSS u otras vulnerabilidades evidentes?

Lista de issues ordenada por prioridad (crítico / alto / medio / bajo).
```

**Aplicar fixes críticos antes de entrega.**

---

## Paso 8 — Haiku: DevOps (~$0.01, ~10 min)

**Input:** stack definido (FastAPI + React + PostgreSQL)  
**Output:** archivos de deployment

**Spawnar haiku-worker:**
```
Invoke: .claude/agents/haiku-worker.md
Task: "Genera docker-compose.yml, .env.example, Makefile y README.md
       para el sistema {sistema} listo para deploy en Railway/Render."
```

---

## Entrega

**Checklist final antes de entregar al cliente:**
- [ ] `README.md` con instrucciones de instalación claras
- [ ] `.env.example` con todas las variables necesarias
- [ ] `docker-compose.yml` funcional
- [ ] Tests pasando (mínimo auth + ventas)
- [ ] QA report sin issues críticos
- [ ] Flujo end-to-end probado manualmente

**Actualizar estado del job:**
```bash
echo "Estado: ENTREGADO — $(date)" >> factory/jobs/{sistema}/ESTADO.md
git add factory/jobs/{sistema}/
git commit -m "feat: {sistema} — sistema básico completado y entregado"
```

---

## Resumen de costos

| Paso | Agente | Tiempo | Costo |
|------|--------|--------|-------|
| 1. Requirements | Gemini | 5 min | $0.00 |
| 2. Diseño | Sonnet (Architect) | 30 min | ~$0.05 |
| 3. Backend boilerplate | Haiku | 20 min | ~$0.02 |
| 4. Routers + services | Haiku | 25 min | ~$0.03 |
| 5. Frontend | Sonnet | 45 min | ~$0.08 |
| 6. Tests | Haiku | 15 min | ~$0.02 |
| 7. QA review | Gemini | 20 min | $0.00 |
| 8. DevOps | Haiku | 10 min | ~$0.01 |
| **Total** | | **~2.5 h** | **~$0.21** |
