# ADR-001: Estrategia de Aislamiento Multi-Tenant en Gestión Neiva

- **Estado:** Aceptado  
- **Fecha:** 2026-09-28  
- **Decisores:** Equipo de Ingeniería Gestión Neiva  
- **Rige bajo:** `docs/spec/constitution.md` Artículo I  

---

## 1. Contexto y Problema

Gestión Neiva es una plataforma POS SaaS orientada a múltiples tiendas y microempresas en Neiva, Colombia. Cada tienda debe operar con independencia y estricta privacidad sobre su catálogo, precios, ventas y clientes. Debemos seleccionar una estrategia de arquitectura multi-tenant que combine costo eficiente de infraestructura, simplicidad en migraciones y garantía de aislamiento.

---

## 2. Opciones Evaluadas

### Opción A: Base de datos separada por tienda
- **Ventajas:** Aislamiento físico absoluto; fácil respaldo individual por tienda.
- **Desventajas:** Costos muy altos de infraestructura en nube; complejidad extrema para orquestar y aplicar migraciones de Alembic en cientos de bases de datos.

### Opción B: Esquemas separados de PostgreSQL (Schema-per-tenant)
- **Ventajas:** Aislamiento a nivel de esquema en una sola instancia de base de datos.
- **Desventajas:** Overhead de conexiones y tablas duplicadas; migraciones complejas.

### Opción C: Base de datos compartida con discriminador `tenant_id` por fila (Row-Level Multitenancy)
- **Ventajas:** Máxima eficiencia de recursos; una sola base de datos y un solo set de migraciones de Alembic; fácil agregación analítica de plataforma.
- **Desventajas:** Requiere disciplina estricta para garantizar que toda consulta filtre por `tenant_id`.

---

## 3. Decisión Adoptada

Se adopta la **Opción C (Discriminador `tenant_id` por fila)** combinada con **inyección de dependencias estricta en FastAPI**.

1. Cada tabla de negocio incluye la columna `tenant_id UUID NOT NULL REFERENCES tenants(id)`.
2. Los tokens JWT autenticados extraen y validan obligatoriamente el `tenant_id`.
3. Una dependencia centralizada de FastAPI (`get_current_tenant`) proporciona el contexto de empresa a todos los servicios y repositorios.
4. Índices compuestos `(tenant_id, ...)` garantizan que las búsquedas se ejecuten en milisegundos dentro del subconjunto de datos de la tienda.

---

## 4. Consecuencias

### Positivas
- Despliegue económico y escalable en PostgreSQL 16.
- Migraciones con Alembic centralizadas y homogéneas.
- Alta velocidad en consultas mediante índices compuestos bien afinados.

### Mitigaciones de Riesgo
- Pruebas automatizadas de aislamiento (un usuario de Tenant A no puede leer registros de Tenant B por ID).
- Prohibición de endpoints sin filtro de tenant a nivel de revisión de código.

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
