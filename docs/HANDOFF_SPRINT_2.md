# Handoff — Gestión Neiva / Sprint 2

> Pegá este contenido completo al inicio de una nueva sesión de Claude Code.

---

## Contexto del proyecto

Sistema POS SaaS multi-tenant para tiendas en Neiva, Colombia.
Repo: https://github.com/Tomasberserk/GESTION_NEIVA_CLAUDE
Working directory: C:\Users\merid\Documents\GESTION_NEIVA_CLAUDE

## Stack

- Backend: FastAPI + SQLAlchemy 2.0 (sync legado en `app/` + async nuevo en `app/core/`)
- DB: PostgreSQL 16 (local via Docker) + Redis 7
- Frontend: React 19 + Vite + TailwindCSS v4 + Shadcn/UI (JSX, no TypeScript)
- Migraciones: Alembic

## Lo que existe y funciona (Sprint 1 — completado)

### Backend (`app/`)
- `app/main.py` — FastAPI con CORS, routers, health check
- `app/database.py` — SQLAlchemy sync (legado, no tocar)
- `app/models.py` — Empresa, Usuario, Producto, Venta, DetalleVenta (sync, no tocar)
- `app/routers/` — auth, empresas, productos, ventas, reportes
- `app/core/config.py` — Settings con pydantic-settings (DATABASE_URL, ASYNC_DATABASE_URL, SECRET_KEY, REDIS_URL, etc.)
- `app/core/database.py` — async engine + AsyncSession + get_async_db()
- `app/models/tenant.py` — modelo Tenant (id, nombre, slug, plan, is_active)

### Frontend (`frontend/src/`)
- `pages/Login.jsx` — página de login existente
- `components/layout/Layout.jsx` — wrapper principal (sidebar + header + children)
- `components/layout/Sidebar.jsx` — nav con íconos lucide-react, links a rutas
- `components/layout/Header.jsx` — header con título y usuario placeholder
- `lib/utils.js` — función cn() para Tailwind

### Docs
- `README.md` — instrucciones completas de instalación
- `docker-compose.yml` — PostgreSQL 16 + Redis 7
- `docs/srs/SRS_MVP_v1.md` — template SRS vacío listo para completar

## Estado actual — qué NO está listo

1. **`npm install` pendiente** — se agregaron dependencias de Shadcn/UI al package.json
   pero no se corrió `npm install`. El frontend NO compila todavía.
   Solución: `cd frontend && npm install && npm run build`

2. **asyncpg no instala en Windows** — falla porque necesita compilador C.
   En Codespaces (Linux) instala sin problema.
   Workaround local: usar psycopg2 sync para desarrollo en Windows.

3. **Base de datos no configurada** — falta `.env` con las credenciales.
   Template en README.md sección "Variables de entorno".

4. **No hay migración para Tenant** — el modelo existe pero no tiene migration de Alembic.

5. **Layout no está conectado al router** — `Layout.jsx` creado pero `App.jsx`
   todavía usa la estructura vieja sin el layout.

## Próximos pasos sugeridos (Sprint 2)

### Prioridad alta
- [ ] Correr `npm install` y verificar build del frontend
- [ ] Conectar `Layout.jsx` en `App.jsx` para rutas autenticadas
- [ ] Crear migración Alembic para tabla `tenants`
- [ ] Configurar `.env` y levantar Docker con PostgreSQL + Redis
- [ ] Verificar que el login funciona end-to-end

### Prioridad media
- [ ] Completar `docs/srs/SRS_MVP_v1.md` con requerimientos reales
- [ ] Agregar primer componente Shadcn/UI (Button, Card, Input) al Login
- [ ] Crear página Dashboard con layout aplicado
- [ ] Agregar router guards (ProtectedRoute ya existe en components)

### Prioridad baja
- [ ] Migrar routers legados a async (uno por uno, empezar por auth)
- [ ] Agregar tests para los nuevos endpoints
- [ ] Configurar `.devcontainer/devcontainer.json` para Codespaces

## Convenciones importantes

- El backend es **JSX, no TypeScript**. No migrar a .tsx.
- El backend tiene dos capas: la sync legada (`app/database.py`, `app/models.py`)
  y la async nueva (`app/core/`). Nuevos features usan async.
- No crear carpeta `backend/` — todo el backend vive en `app/`.
- Antes de mover o renombrar archivos existentes, preguntar al usuario.
- El `.env` nunca va a git (está en .gitignore).

## Comandos para arrancar

```bash
# 1. Levantar base de datos
docker compose up -d

# 2. Instalar dependencias frontend
cd frontend && npm install

# 3. Correr backend
cd ..
.venv\Scripts\activate
uvicorn app.main:app --reload

# 4. Correr frontend (en otra terminal)
cd frontend && npm run dev
```

Backend en: http://localhost:8000/docs
Frontend en: http://localhost:5173

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
