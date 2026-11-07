# Workflow Multi-Agente — Claude Code + Gemini CLI

Cómo sacarle el máximo a estos dos juntos en Gestión Neiva.

---

## La lógica del combo

```
Gemini CLI                         Claude Code
(gratis, 1M tokens)                (de pago, el cerebro principal)

  Lee todo el repo                   Implementa
  Investiga librerías                Arquitectura
  Revisa código extenso              Debugging complejo
  Genera docs / SRS                  Agent teams internos
  Primera pasada de review           Decisión final
       │                                   │
       └──── vos coordinás ───────────────┘
```

**Regla de oro:** Gemini lee y analiza (gratis). Claude actúa y decide (de pago).
Así gastás tokens de Claude solo donde importa.

---

## Instalación Gemini CLI

```bash
npm install -g @google/gemini-cli
gemini auth login   # abre el navegador, loguear con Google
gemini              # verificar que funciona
```

Límite gratuito: 60 requests/min · 1,000 requests/día · 1M tokens de contexto.

---

## Claude Code — modelos por tarea

Dentro de Claude Code usás distintos modelos según la complejidad:

**Tabla 1**  
*Registro estructurado de especificaciones técnicas ( Sección 1 )*

| Modelo | Cuándo usarlo |
|--------|--------------|
| `claude-opus-4-7` | Decisiones de arquitectura críticas, diseño del sistema |
| `claude-sonnet-4-6` | Features nuevas, debugging, refactors (el default) |
| `claude-haiku-4-5-20251001` | Tests, schemas, boilerplate, migraciones simples |

*Nota.* Especificación técnica sincronizada con la arquitectura vigente del proyecto. Fuente: Elaboración propia (2026).

### Invocar Haiku para tareas livianas (en Claude Code):

```
Spawn a haiku-worker teammate to write unit tests for app/routers/auth.py
```

```
Spawn a haiku-worker teammate to generate Pydantic schemas 
for the Tenant model in app/models/tenant.py
```

El agente `haiku-worker` ya está definido en `.claude/agents/haiku-worker.md`.

---

## Workflows concretos

### Workflow 1 — Feature nueva

```
1. [Gemini] Investigar el mejor enfoque
   gemini "¿Cómo implementar JWT refresh tokens en FastAPI?
   Dame el patrón más simple para un SaaS pequeño con SQLAlchemy async."

2. [Vos] Llevás el resultado a Claude Code
   "Basado en este approach: [pegar respuesta de Gemini]
   Implementá refresh tokens en app/routers/auth.py"

3. [Claude Haiku en team] Escribir los tests
   "Spawn a haiku-worker to write tests for the refresh token endpoint"
```

---

### Workflow 2 — Review de código

```
1. [Gemini] Review completo del backend
   gemini --all_files "Revisá el código en app/routers/ y app/models.py.
   Buscá: endpoints sin validación, queries N+1, datos sensibles expuestos.
   Dame un reporte con severidad Alta/Media/Baja."

2. [Vos] Priorizás los issues

3. [Claude Sonnet] Corregís los de alta severidad
   "Corregí estos problemas que encontró Gemini: [lista]"
```

---

### Workflow 3 — Entender código legacy

```
[Gemini] Tiene 1M de contexto, puede leer todo el proyecto de una vez:

gemini "Lee todos los archivos en app/routers/ y app/services/.
Explicame el flujo completo de una venta: desde el endpoint POST /ventas
hasta cómo se actualiza el stock del producto."
```

Esto lo hace gratis. No gastar tokens de Claude en leer código que Gemini puede leer.

---

### Workflow 4 — Completar el SRS

```
[Gemini] Con el contexto del código real:

gemini --file docs/srs/SRS_MVP_v1.md --file app/models.py --file app/routers/ventas.py
"Completá las secciones vacías [POR COMPLETAR] de este SRS basándote en el código real.
Infería los requerimientos funcionales del comportamiento que ves en los modelos y routers."
```

---

### Workflow 5 — Debugging

```
1. [Claude] Primero intentá con Claude (tiene contexto de la conversación)
   "El endpoint POST /ventas falla con 422 cuando precio es null"

2. [Gemini] Si Claude no lo resuelve, tirále todo el contexto:
   gemini --file app/routers/ventas.py --file app/schemas/venta.py
   "Este endpoint falla con 422 cuando precio es null. 
   Encontrá el problema exacto y dame la corrección."

3. [Claude] Aplicás la corrección con Claude (para que quede en su contexto)
```

---

### Workflow 6 — Sprint planning

```
[Gemini] Para analizar el estado del proyecto antes de planificar:

gemini --all_files "Analizá este proyecto y decime:
1. Qué funcionalidades están implementadas y funcionando
2. Qué está incompleto o roto
3. Qué deuda técnica existe
4. Sugerí las 5 tareas más impactantes para el próximo sprint"
```

---

## Prompt base para Gemini en este proyecto

Guardalo como snippet o alias:

```bash
# Alias sugerido (agregar a tu .bashrc o $PROFILE de PowerShell)
function gn { gemini "Contexto: Gestión Neiva, sistema POS SaaS multi-tenant. Stack: FastAPI + SQLAlchemy async + PostgreSQL + React 19 JSX + TailwindCSS v4. Backend en app/, frontend en frontend/src/. NO TypeScript, NO carpeta backend/. $args" }

# Uso:
gn "¿Cómo implemento paginación en los endpoints de productos?"
```

---

## Qué hace cada uno — resumen rápido

**Tabla 2**  
*Registro estructurado de especificaciones técnicas ( Sección 2 )*

| Tarea | Herramienta | Por qué |
|-------|-------------|---------|
| Diseñar arquitectura | Claude Sonnet/Opus | Necesita criterio y contexto de la conversación |
| Implementar feature | Claude Sonnet | El mejor para código correcto y seguro |
| Tests / schemas / docs | Claude Haiku (team) | 20x más barato que Sonnet |
| Investigar librerías | Gemini | Gratis, rápido |
| Leer todo el codebase | Gemini | 1M tokens, gratis |
| Review de seguridad | Gemini primero, Claude confirma | Gemini lee todo, Claude decide |
| Completar SRS/README | Gemini | Puede leer código + doc al mismo tiempo |
| Debugging con mucho contexto | Gemini para analizar, Claude para corregir | División de trabajo óptima |

*Nota.* Especificación técnica sincronizada con la arquitectura vigente del proyecto. Fuente: Elaboración propia (2026).

---

## Lo que NO hacer

- **No usar Claude para leer archivos que no vas a modificar** — usá Gemini (gratis).
- **No usar Opus para tareas rutinarias** — Haiku o Sonnet cubren el 90% de los casos.
- **No abrir una sesión nueva de Claude Code por cada pregunta pequeña** — el contexto acumulado es valioso.
- **No pedirle a Gemini que edite archivos directamente** — solo análisis y sugerencias. Claude edita.

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
