# Setup Multi-Agente — Gestión Neiva

Guía para coordinar Claude Code + Gemini CLI + Codex CLI en el mismo proyecto.

---

## Arquitectura real del equipo

```
┌─────────────────────────────────────────────────┐
│              TU (el coordinador)                │
└───────┬─────────────────┬───────────────────────┘
        │                 │                    │
        ▼                 ▼                    ▼
  Claude Code        Gemini CLI          Codex CLI
  (terminal 1)      (terminal 2)        (terminal 3)
  
  Opus/Sonnet       Gratis              API key OpenAI
  para features     para research       para sugerencias
  y arquitectura    y contexto largo    inline agénticas
  
  Haiku             ← ideal para →      docs, tests,
  para tareas                           boilerplate
  livianas en team
```

**Importante:** Gemini y Codex NO son teammates de Claude Code.
Son herramientas separadas que coordinás vos manualmente.

---

## 1. Claude Code — Configurar modelos por teammate

Dentro de Claude Code podés especificar qué modelo usa cada agente.

### En el prompt al lead:

```
Crea un agent team para refactorizar los routers.
- Teammate "Arquitecto": usa claude-opus-4-7. Diseña la estructura.
- Teammate "Builder": usa claude-sonnet-4-6. Implementa los cambios.
- Teammate "Tester": usa claude-haiku-4-5-20251001. Escribe los tests.
```

### Subagent definitions para reutilizar:

Crea `.claude/agents/haiku-worker.md`:

```markdown
---
name: haiku-worker
description: Agente liviano para tareas repetitivas (tests, docs, boilerplate)
model: claude-haiku-4-5-20251001
---

Eres un agente eficiente especializado en tareas bien definidas.
Ejecuta exactamente lo que se te pide, sin explorar ni expandir el scope.
Reporta cuando termines con un resumen de una línea.
```

Crea `.claude/agents/senior-dev.md`:

```markdown
---
name: senior-dev
description: Agente para features complejas y decisiones de arquitectura
model: claude-opus-4-7
---

Eres un desarrollador senior experto en FastAPI, SQLAlchemy async, y React.
Antes de implementar, valida que tu enfoque es el correcto.
Prioriza código limpio, seguro y mantenible.
```

Uso:
```
Spawn a haiku-worker teammate to write unit tests for app/routers/auth.py
Spawn a senior-dev teammate to redesign the tenant isolation strategy
```

---

## 2. Gemini CLI — Instalación y uso (GRATIS)

### Instalación

```bash
npm install -g @google/gemini-cli
```

Requiere cuenta Google. Límite gratis: 60 requests/min, 1M tokens de contexto.

### Autenticación

```bash
gemini auth login
```

### Uso en este proyecto

Gemini CLI es ideal para contexto largo — puede leer todo el codebase de una vez.

```bash
# Desde la raíz del proyecto
cd C:\Users\merid\Documents\GESTION_NEIVA_CLAUDE

# Revisión de código completa
gemini "Revisa el archivo app/models.py y app/models/tenant.py. 
¿Hay inconsistencias entre el modelo sync legado y el nuevo Tenant async? 
Dame un reporte con los conflictos potenciales."

# Research de librería
gemini "¿Cuál es la mejor estrategia de multi-tenancy con FastAPI + SQLAlchemy async? 
Dame 3 opciones con pros y contras para un SaaS POS pequeño."

# Revisión del SRS
gemini --file docs/srs/SRS_MVP_v1.md "Completa las secciones vacías de este SRS 
basándote en un sistema POS SaaS multi-tenant para tiendas pequeñas en Colombia."
```

### Prompt base para Gemini en este proyecto

```
Contexto: Trabajo en Gestión Neiva, un sistema POS SaaS multi-tenant.
Stack: FastAPI + SQLAlchemy 2.0 async + PostgreSQL + React 19 JSX + TailwindCSS v4.
El código está en C:\Users\merid\Documents\GESTION_NEIVA_CLAUDE.
Backend en app/, frontend en frontend/src/.
NO uses TypeScript, NO crees carpeta backend/ (usamos app/).

[Tu pregunta aquí]
```

---

## 3. OpenAI Codex CLI — Instalación

> Requiere cuenta OpenAI con créditos (no es gratis, pero hay $5 de crédito inicial).

### Instalación

```bash
npm install -g @openai/codex
```

### Autenticación

```bash
export OPENAI_API_KEY=tu-api-key-aqui
# Windows PowerShell:
$env:OPENAI_API_KEY = "tu-api-key-aqui"
```

### Uso en este proyecto

```bash
cd C:\Users\merid\Documents\GESTION_NEIVA_CLAUDE

# Generar endpoint
codex "Crea un endpoint FastAPI GET /api/tenants/{slug} que retorne 
el tenant con ese slug usando SQLAlchemy async. 
Sigue el patrón de app/routers/empresas.py"

# Modo interactivo (puede editar archivos directamente)
codex --approval-mode auto "Agrega validación de slug único en el modelo Tenant"
```

---

## 4. Workflow coordinado — cómo trabajar con los 3

### Setup de terminales

```
Terminal 1: Claude Code (lead)
Terminal 2: Gemini CLI (research/revisión)
Terminal 3: Codex CLI (implementación rápida)
Terminal 4: uvicorn --reload (backend corriendo)
Terminal 5: npm run dev (frontend corriendo)
```

### Flujo recomendado por tipo de tarea

| Tarea | Herramienta |
|-------|-------------|
| Diseño de arquitectura | Claude Opus (en Claude Code) |
| Implementar feature compleja | Claude Sonnet (en Claude Code) |
| Escribir tests / docs | Claude Haiku (en Claude Code, como teammate) |
| Research de librerías | Gemini CLI (gratis, contexto largo) |
| Revisión de código extenso | Gemini CLI (puede leer todo el repo) |
| Boilerplate rápido | Codex CLI |
| Completar SRS / documentar | Gemini CLI |
| Debugging complejo | Claude Sonnet/Opus |

### Ejemplo de sesión real

```bash
# 1. Gemini investiga
gemini "¿Cómo implementar row-level security para multi-tenancy en PostgreSQL 
con SQLAlchemy async? Dame el patrón más simple para un MVP."

# 2. Llevás el resultado a Claude Code
# (copiás la respuesta de Gemini y se la das al lead de Claude Code)
"Basado en este research de Gemini: [pegar respuesta]
Implementá el tenant isolation en app/core/database.py"

# 3. Claude Haiku escribe los tests
"Spawn a haiku-worker teammate to write tests for the tenant isolation 
implemented in app/core/database.py"

# 4. Codex genera el migration
codex "Genera la migración de Alembic para la tabla tenants con 
row-level security habilitado"
```

---

## 5. Reglas del equipo

1. **Claude Code es el lead** — toma decisiones de arquitectura, revisa el trabajo de los otros.
2. **Gemini para research y contexto largo** — nunca le des permiso de editar archivos directamente.
3. **Codex para boilerplate rápido** — siempre revisar su output antes de comitear.
4. **Haiku para lo repetitivo** — tests, docstrings, schemas Pydantic, migraciones simples.
5. **Vos coordinás** — ninguna IA toma decisiones de negocio ni cambia la arquitectura sin tu ok.

---

## 6. Costos estimados por sesión de desarrollo

| Escenario | Costo aprox |
|-----------|-------------|
| Solo Claude Sonnet, 2h de trabajo | $0.50 - $2.00 |
| Claude Opus para arquitectura (30 min) | $1.00 - $3.00 |
| Claude Haiku para 20 tests | $0.05 |
| Gemini CLI (todo lo que quieras) | $0.00 |
| Codex CLI, 10 generaciones | $0.10 - $0.30 |

**Estrategia óptima:** Gemini para explorar/investigar (gratis), 
Haiku para tareas mecánicas (casi gratis), Sonnet para implementar features,
Opus solo para decisiones de arquitectura críticas.
