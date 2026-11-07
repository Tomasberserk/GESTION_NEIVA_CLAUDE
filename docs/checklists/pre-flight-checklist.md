# Checklist Pre-Vuelo de Calidad — Gestión Neiva

---

## ✈️ Fase 1: Antes de programar un nuevo endpoint o modelo
- [ ] ¿Identificaste la regla de negocio (`RN-xx`) que estás implementando?
- [ ] ¿La consulta o escritura incluye obligatoriamente el filtro `tenant_id`?
- [ ] Si estás en una transacción de venta, ¿los precios y nombres históricos se congelan en la línea de detalle?
- [ ] ¿Verificaste que no estás guardando totales derivados en tablas cabecera?
- [ ] ¿Estás usando la sesión asíncrona moderna `AsyncSession` (`get_async_db`) y no la sesión síncrona legada?

---

## 🛠️ Fase 2: Durante el desarrollo
- [ ] ¿Escribiste la prueba unitaria o de integración en `tests/` antes o a la par del código productivo?
- [ ] ¿Los nombres de métodos, variables y tablas están en inglés (`sales`, `products`, `tenants`)?
- [ ] ¿Los mensajes devueltos al usuario en la respuesta HTTP están en español correcto con tildes?
- [ ] ¿El nuevo endpoint maneja códigos de error semánticos (400, 401, 403, 404, 409, 422) con el formato estándar RFC 7807?

---

## 🏁 Fase 3: Antes de confirmar o cerrar sesión
- [ ] ¿Pasan todas las pruebas automáticas en verde?
  ```powershell
  .venv\Scripts\python.exe -m pytest tests/test_auth.py -v
  ```
- [ ] ¿El frontend compila sin errores?
  ```powershell
  cd frontend; npm run build; cd ..
  ```
- [ ] ¿Actualizaste `docs/traspaso/HANDOFF.md` reflejando el estado real y el siguiente paso?

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
