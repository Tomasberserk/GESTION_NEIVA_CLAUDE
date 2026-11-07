# Gestión Neiva — Sistema POS SaaS

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green?logo=fastapi)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)

Sistema de punto de venta (POS) SaaS multi-tenant para gestión de tiendas en Neiva, Colombia.

---

## Tech Stack

**Tabla 1**  
*Registro estructurado de especificaciones técnicas ( Sección 1 )*

| Capa | Tecnología |
|------|-----------|
| Backend | FastAPI + SQLAlchemy 2.0 (sync + async) |
| Base de datos | PostgreSQL 16 |
| Caché / Sesiones | Redis 7 |
| Frontend | React 19 + Vite + TailwindCSS v4 |
| Migraciones | Alembic |

*Nota.* Especificación técnica sincronizada con la arquitectura vigente del proyecto. Fuente: Elaboración propia (2026).

---

## Estructura del proyecto

```
GESTION_NEIVA_CLAUDE/
├── app/
│   ├── core/           # Config y base de datos async
│   ├── models/         # Modelos nuevos (Tenant, ...)
│   ├── routers/        # Endpoints FastAPI
│   ├── schemas/        # Schemas Pydantic
│   ├── services/       # Lógica de negocio
│   ├── database.py     # Conexión sync (legado)
│   ├── models.py       # Modelos sync (legado)
│   └── main.py         # Entry point FastAPI
├── frontend/
│   ├── src/
│   │   ├── components/ # Componentes React
│   │   ├── pages/      # Páginas de la app
│   │   ├── context/    # Contextos globales
│   │   └── hooks/      # Custom hooks
│   └── package.json
├── docs/
│   └── srs/            # Documentos de requerimientos
├── alembic/            # Migraciones de BD
├── docker-compose.yml  # Servicios locales
└── requirements.txt
```

---

## Requisitos

- Python 3.11+
- Node.js 20+
- Docker y Docker Compose (para servicios locales)

---

## Instalación rápida

### 1. Clonar y configurar entorno

```bash
git clone <repo-url>
cd GESTION_NEIVA_CLAUDE

# Backend — entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

### 2. Variables de entorno

```bash
cp .env.example .env   # Editar con tus credenciales
```

### 3. Levantar servicios con Docker

```bash
docker compose up -d
```

Esto levanta PostgreSQL en `localhost:5432` y Redis en `localhost:6379`.

### 4. Correr migraciones

```bash
alembic upgrade head
```

### 5. Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Variables de entorno (.env)

```env
DATABASE_URL=postgresql://gestion_user:gestion_pass@localhost:5432/gestion_neiva
ASYNC_DATABASE_URL=postgresql+asyncpg://gestion_user:gestion_pass@localhost:5432/gestion_neiva
SECRET_KEY=tu-clave-secreta-aqui
ENVIRONMENT=development
REDIS_URL=redis://localhost:6379
```

---

## Comandos útiles

```bash
# Correr backend
uvicorn app.main:app --reload

# Correr frontend
cd frontend && npm run dev

# Correr tests
pytest

# Nueva migración
alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
alembic upgrade head
```

**Backend:** http://localhost:8000  
**Docs API:** http://localhost:8000/docs  
**Frontend:** http://localhost:5173

---

## Contribución

1. Crea un branch desde `main`
2. Haz tus cambios
3. Corre los tests antes de hacer PR
4. El PR debe tener descripción clara del cambio

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
