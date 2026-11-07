# Handoff — Estado Real y Sincronización de Gestión Neiva

**Fecha de actualización:** 2026-09-28  
**Propósito:** Sincronización viva entre desarrolladores y agentes de IA. Ninguna cifra en prosa sustituye la ejecución de los comandos que miden la realidad.

---

## 1. Comandos de Verificación Rápida (Ejecútalos al iniciar sesión)

Ejecuta estos comandos en la raíz `C:\Users\merid\Documents\GESTION_NEIVA_CLAUDE`:

**Tabla 1**  
*Registro estructurado de especificaciones técnicas ( Sección 1 )*

| Qué quieres saber | Comando exacto (PowerShell) | Resultado esperado |
|---|---|---|
| **¿Pasan las pruebas de Backend?** | `.venv\Scripts\python.exe -m pytest tests/test_auth.py -v` | `6 passed`, `0 failed`, `0 warnings` bloqueantes |
| **¿Compila el Frontend React?** | `cd frontend; npm run build; cd ..` | `Build succeeded`, dist generado |
| **¿Están los servicios arriba?** | `docker compose ps` | Contenedores de Postgres y Redis en `healthy / running` |
| **¿Están las migraciones al día?** | `.venv\Scripts\python.exe -m alembic current` | Muestra la última revisión aplicada |

*Nota.* Especificación técnica sincronizada con la arquitectura vigente del proyecto. Fuente: Elaboración propia (2026).

---

## 2. Estado Real del Sistema (Capacidades Verificadas)

Capacidades ya probadas y operativas en el entorno:

- [x] **Autenticación Multi-Tenant (Sprint 3):** Registro de usuario con empresa asociada, hash seguro de contraseñas, login con JWT, validación de emails duplicados y endpoint `/me` protegido (6/6 tests pasando en `tests/test_auth.py`).
- [x] **Compatibilidad de Tests SQLite:** Pool `StaticPool` y decorador `GUID` para soportar pruebas en memoria sin requerir Postgres local para tests unitarios rápidos.
- [x] **Modelos Base:** `Tenant` (Empresa) y `User` (Usuario) definidos con llaves UUID y banderas de actividad.
- [ ] **Módulo POS de Ventas:** En diseño arquitectónico (Sprint 4).
- [ ] **Control de Stock y Concurrencia:** En diseño arquitectónico (Sprint 4).

---

## 3. Próximo Paso Inmediato (Sprint 4)

1. **Diseñar el contrato de la API de Ventas (`docs/spec/api-contract.md`):** Endpoint `POST /api/v1/sales` con validación atómica de inventario.
2. **Definir el modelo de datos de Venta y Detalle de Venta (`docs/spec/data-model.md`):** Implementar snapshots de precios y relación con `tenant_id`.
3. **Escribir prueba roja de ventas:** Test que intente registrar una venta descontando inventario y falle primero.

---

## 4. Trampas y Lecciones Aprendidas (¡No tropezar aquí!)

- **SQLite vs Postgres:** En SQLite los UUIDs requieren el convertidor `TypeDecorator GUID` configurado en `tests/conftest.py`. No uses tipos nativos de Postgres directamente en modelos si pretendes correr tests rápidos en memoria SQLite.
- **Server Defaults:** SQLite no siempre resuelve los `server_default` en modelos en memoria; los servicios deben inicializar explícitamente `is_active=True`.
- **Sesión de BD:** Todo endpoint nuevo debe usar `get_async_db` para no incurrir en bloqueos con la sesión síncrona legada.

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
