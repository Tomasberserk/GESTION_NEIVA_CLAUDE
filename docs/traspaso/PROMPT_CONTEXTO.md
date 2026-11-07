# PROMPT DE CONTEXTO — Pegar al inicio de cualquier sesión nueva (Claude/Gemini)

> Última actualización: 2026-10-18 · Mantener este prompt actualizado al cierre de cada sprint (ver checklist en `docs/checklists/pre-flight-checklist.md`).

---

## Copiar y pegar desde aquí ⬇️

Estás trabajando en **Gestión Neiva** (`C:\Users\merid\Documents\GESTION_NEIVA_CLAUDE`), un POS/ERP multi-tenant para tenderos de Neiva, Colombia. Es también una **fábrica de sistemas IA** (tiers basic/medium/professional) construida con Claude + Gemini como co-autores; leer `AGENTS.md` (protocolo de colaboración), `CLAUDE.md`, `GEMINI.md` y `PLAN_ACTIVO.md` (fuente de verdad del sprint).

**Stack:** FastAPI + SQLAlchemy + Alembic + PostgreSQL (SQLite solo para tests rápidos) + Redis en backend (`app/`); React 19 + JSX puro (SIN TypeScript) + Vite + Tailwind en frontend (`frontend/src/`); docker + render.yaml para deploy. Scripts en PowerShell (Windows).

**Estado real (verificado 2026-10-18):** 86/86 tests backend pasando y build de Vite limpio (~15s). Completados hasta Sprint 8.4: auth multi-tenant, POS con stock concurrente (`SELECT FOR UPDATE`), dashboard/reportes, categorías/vencimientos/granel/escáner, RBAC Dueño vs Cajero con límite de cajeros por plan, ERP integrado (compras/proveedores/cuentas por pagar) según plan de empresa, CRM de soporte + SuperAdmin, **Agente IA in-app** con FSM + idempotencia persistente (`agent_commands`) + provider agnóstico (Groq/Gemini, modelo fijado `gemini-3.6-flash`) + benchmark 280/280 + dictamen GO producción 9.5/10, ciclo de voz blindado (VAD 950ms, BackendSTT vs WebSpeech, watchdog), y entitlements con trial Pro de 15 días Fail-Closed + UI Pro en Header.

**Vamos a trabajar sobre las brechas del Sprint 9 (definidas en `PLAN_ACTIVO.md` → sección "Sprint 9 — Brechas pendientes para Producción Comercial")**, hoje priorizadas:

1. **🔴 B1+B2 — Monetización (prioridad main):** la activación Pro es hoy manual vía ticket de soporte (`/api/soporte/solicitar-upgrade`). Falta pasarela de pago colombiana (candidato: Wompi), webhook idempotente de confirmación, `suscripcion_service` que active/desactive `empresa.plan` automáticamente, y ciclo de vida trial→pago→pro→vencimiento con tests E2E. **El primer cobro real desbloquea Hermes-3 (Together AI), restricción activa del proyecto.**
2. **🔴 B3 — Deploy productivo:** compose completo (Postgres 16 + Redis 7 + Nginx + migraciones alembic en arranque + backups). `docker-compose.yml`, `render.yaml`, `Dockerfile` y `Procfile` ya existen pero básicos.
3. **🟡 B4 — Telemetría del agente:** medir `time_to_sale`, `confirmation_rate`, `clarification_rate`, `LLM_fallback_rate` para el piloto de 5–10 tiendas.
4. **🟡 B5 — Landing con placeholders** (`[HISTORIA REAL PENDIENTE]` ×2, redes vacías) en `LandingPage.jsx`.
5. **🟡 B6 — Code-splitting:** bundle único >500 kB; hacer `React.lazy` en rutas pesadas (`App.jsx`, `LandingPage`, `SuperAdmin`) y `manualChunks`.

**Reglas inamovibles (las 5 Leyes + restricciones):**
- PostgreSQL es la única autoridad de datos; el LLM es solo intérprete. Toda mutación pasa por servicios de negocio con confirmación del usuario.
- Aislamiento multi-tenant estricto: `empresa_id`/`usuario_id` desde el JWT verificado, siempre.
- POS básico (ventas/caja/inventario) **nunca se bloquea** por vencimiento de trial/suscripción (Regla SUB-09); `require_pro_entitlement` solo protege funciones Pro (agente, voz).
- Hermes-3 y toda API paga: BLOQUEADOS hasta primer ingreso real. Sin Ollama local. Sin TypeScript en frontend.
- TDD pragmático: test rojo primero cuando aplique; toda tarea de `PLAN_ACTIVO.md` se cierra ejecutando su comando de verificación y actualizando el plan + commit descriptivo.

**Verificación rápida al iniciar (PowerShell, raíz del repo):**
```powershell
.venv\Scripts\python.exe -m pytest tests/ -q --tb=no    # esperado: todos passed
cd frontend; npm run build; cd ..                       # esperado: ✓ built
docker compose ps                                       # servicios arriba
.venv\Scripts\python.exe -m alembic current             # migración al día
```

Lee `PLAN_ACTIVO.md` antes de proponer cambios y registra propuestas con `> [CLAUDE PROPONE]` o `> [GEMINI PROPONE]`.

## ⬆️ Hasta aquí — copiar y pegar

---

## Declaración de Uso de Inteligencia Artificial Generativa y Derechos de Autor (Norma APA 7.ª Edición)

En cumplimiento de las políticas de integridad académica y propiedad intelectual del Servicio Nacional de Aprendizaje (SENA — Programa ADSO) y los estándares de citación de la American Psychological Association (APA, 7.ª ed., 2020), el equipo de desarrollo integrado por Tomás Barrera Ortiz (`@Tomasberserk`), Santiago Javela Ospino (`@SantiagoJavelaOspino`) y Juan Pablo Doria Caviedes (`@Doritotes444`) declara de manera explícita y transparente el uso ético y supervisado de herramientas de Inteligencia Artificial Generativa (IAG):

1. **Alcance del apoyo con IA:** Los modelos de lenguaje fueron utilizados como asistentes de programación en pareja (*pair programming*), generación de código repetitivo (*boilerplate* de esquemas Pydantic y migraciones Alembic), estructuración inicial de plantillas documentales bajo el marco SDD (*Specification-Driven Development*), auditoría estática de seguridad OWASP y pruebas automatizadas. Toda la arquitectura de negocio, reglas de dominio del comercio minorista en Neiva (`BR-01` a `BR-12`), validación funcional y decisiones técnicas fueron diseñadas, verificadas y aprobadas íntegramente por los aprendices autores.
2. **Modelos utilizados y atribución técnica:**
   - *Anthropic Claude Sonnet 4.6 y Claude Haiku 4.5* (Anthropic, 2026): Asistencia en refactorización modular, generación de esquemas, contratos de fachada y coautoría declarada en metadatos de commits (`Co-Authored-By`).
   - *Google Gemini 2.5 Flash / 3.6 Flash* (Google DeepMind, 2026): Procesamiento de lenguaje natural en el módulo `agente_ia`, análisis de contexto de repositorio y revisión de calidad documental.
   - *Groq Cloud Whisper Large v3* (Groq Inc., 2026): Transcripción automática de voz a texto (STT) en tiempo real para el Modo Mostrador del punto de venta.
   - *OpenAI ChatGPT (GPT-4o)* (OpenAI, 2026) y *Google Veo*: Consultoría de optimización de rendimiento frontend (`code-splitting`) y apoyo en guionización visual de la página de aterrizaje.
3. **Derechos de autor y licencias de terceros:** El código fuente original de **Gestión Neiva (TiendApp POS SaaS)** es propiedad intelectual de sus autores humanos (Barrera Ortiz, Javela Ospino y Doria Caviedes, 2026). Las librerías de terceros (FastAPI, SQLAlchemy, React 19, TailwindCSS, Radix UI, Lucide Icons, ZXing) se utilizan bajo sus respectivas licencias de código abierto (MIT / Apache 2.0 / BSD), y los recursos fotográficos de demostración provienen de bancos libres de regalías (Pexels / Picsum Photos) conforme a sus términos de atribución.

**Referencias de modelos IA (Formato APA 7):**
- Anthropic. (2026). *Claude (Versiones Sonnet 4.6 y Haiku 4.5)* [Modelo de lenguaje grande]. https://www.anthropic.com
- Google. (2026). *Gemini (Versión 2.5 Flash)* [Modelo multimodal de inteligencia artificial]. https://deepmind.google/technologies/gemini/
- OpenAI. (2026). *ChatGPT (Versión GPT-4o)* [Modelo de lenguaje grande]. https://chat.openai.com
