# ADR-002: Control de Concurrencia en Inventarios de Punto de Venta (POS)

- **Estado:** Aceptado  
- **Fecha:** 2026-09-28  
- **Decisores:** Equipo de Ingeniería Gestión Neiva  
- **Rige bajo:** `docs/spec/constitution.md` Artículo VI  

---

## 1. Contexto y Problema

En horas pico en tiendas con múltiples cajas o terminales simultáneos, dos cajeros pueden intentar facturar la última unidad de un producto al mismo instante. Sin un mecanismo de control de concurrencia, ambas transacciones podrían leer `stock = 1`, descontar 1 y dejar el inventario en -1 o vender productos no existentes.

---

## 2. Opciones Evaluadas

### Opción A: Bloqueo pesimista (`SELECT ... FOR UPDATE` en transacción corta)
- **Ventajas:** Garantía inmediata en PostgreSQL; el motor bloquea la fila del producto durante los microsegundos que tarda en insertar la venta y hacer `stock = stock - cantidad`.
- **Desventajas:** Mantiene un bloqueo exclusivo a nivel de fila durante la transacción (aunque sea muy corta).

### Opción B: Concurrencia optimista pura (Token de versión `version INT`)
- **Ventajas:** No bloquea la fila; si la versión cambió en el `UPDATE`, la consulta afecta 0 filas y se dispara una excepción en la app.
- **Desventajas:** Obliga al cajero a reintentar si otro cobró una milésima de segundo antes, lo que puede ser frustrante en la fila de una tienda si el producto aún tenía suficiente stock.

---

## 3. Decisión Adoptada

Se adopta una **estrategia combinada optimizada para POS**:

1. **Bloqueo a nivel de fila con transacción corta (`SELECT ... FOR UPDATE`) ordenado por ID de producto** durante la confirmación final de la venta.
2. Al ordenar el bloqueo de productos alfabéticamente por su UUID, se elimina por completo el riesgo de **deadlocks** (bloqueos mutuos).
3. La transacción se mantiene abierta únicamente durante la lectura del stock, validación de no negatividad (`stock >= cantidad`), descuento del inventario e inserción de la cabecera/detalles de venta.
4. Si el stock no alcanza, se aborta la transacción y se retorna un error claro `422 Unprocessable Entity` especificando qué producto agotó sus existencias.

---

## 4. Consecuencias

### Positivas
- Cero sobreventas ni stock negativo.
- Consistencia inmediata garantizada por PostgreSQL 16 sin obligar a reintentos complejos en el frontend.
- Cero deadlocks gracias al ordenamiento determinista por ID al bloquear múltiples productos en un ticket.

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
