# Constitución de Arquitectura — Gestión Neiva (POS SaaS)

Principios innegociables del proyecto. Cada artículo define su justificación y el mecanismo objetivo de verificación. Un cambio que viole estos artículos debe ser rechazado de inmediato.

---

## Artículo I — Aislamiento Multi-Tenant Estricto (Fuga Cero)

Gestión Neiva es un SaaS multi-empresa. **Ninguna consulta de lectura o escritura en el sistema puede omitir el `tenant_id` (empresa)** a menos que sea una operación explícita de superadministrador de plataforma.

- **Por qué:** Una fuga de información donde la Tienda A pueda ver productos, ventas o clientes de la Tienda B es una catástrofe legal y operativa inadmisible.
- **Cómo se verifica:** Cada endpoint protegido inyecta el `tenant_id` del token JWT verificado. Los tests de integración incluyen aserciones de aislamiento: un usuario autenticado de la Empresa 1 intentando acceder por ID a un recurso de la Empresa 2 recibe `404 Not Found` (o `403 Forbidden`).

---

## Artículo II — Pureza de la Lógica de Negocio POS

La lógica de cálculo de ventas, descuentos, validación de inventario y corte de caja reside en la capa de servicios/dominio (`app/services/` o `app/domain/`), **totalmente desacoplada de FastAPI y de los controladores HTTP**.

- **Por qué:** Permite probar las reglas de facturación e inventario con tests unitarios en memoria a máxima velocidad, sin necesidad de levantar el servidor web ni emular peticiones HTTP.
- **Cómo se verifica:** Los servicios reciben tipos puros de Python o esquemas Pydantic; ningún servicio importa `Request`, `Response`, `HTTPException` o dependencias del framework web.

---

## Artículo III — Inmutabilidad de los Hechos Históricos (Principio del Snapshot)

En cada transacción de venta (`sale_item` / `detalle_venta`), **se congelan el precio unitario, el nombre del producto y la tasa impositiva** al momento exacto de la venta.

- **Por qué:** Si la tienda sube el precio de un producto la próxima semana o le cambia el nombre, el histórico de ventas y la contabilidad pasada no deben alterarse bajo ninguna circunstancia.
- **Cómo se verifica:** El reporte de ventas y la consulta de facturas históricas leen el precio congelado en el detalle de la venta, sin hacer `JOIN` con la tabla `product` para obtener el precio actual.

---

## Artículo IV — Lo derivado se calcula, nunca se almacena

El subtotal de línea, el IVA total y el total general de la venta **se calculan sumando las líneas hijas**. No existe una columna estática desincronizable en la tabla cabecera.

- **Por qué:** Evita que ante la edición o corrección de una línea el total quede desfasado.
- **Cómo se verifica:** El esquema de base de datos calcula el total como propiedad derivada o vista; las pruebas unitarias validan que la suma de los ítems equivalga exactamente al total emitido.

---

## Artículo V — Baja Lógica (Soft Delete) en Entidades con Historial

Los productos, clientes o usuarios que posean registros transaccionales históricos jamás se eliminan con `DELETE` físico de PostgreSQL; se desactivan (`is_active = False`).

- **Por qué:** El borrado físico rompe la integridad referencial y corrompe los reportes de auditoría y facturación de la DIAN / tributarios.
- **Cómo se verifica:** Los tests intentan dar de baja un producto vendido y confirman que sigue existiendo en base de datos con `is_active=False` y que sus ventas asociadas siguen siendo consultables.

---

## Artículo VI — Concurrencia Real en Inventario POS

El descuento de existencias al confirmar una venta en el punto de venta debe ejecutarse bajo una transacción atómica protegida contra condiciones de carrera (utilizando `SELECT ... FOR UPDATE` en transacciones cortas o tokens de versión/concurrencia optimista).

- **Por qué:** Evita sobreventas si dos cajeros facturan la última unidad disponible simultáneamente.
- **Cómo se verifica:** Pruebas de concurrencia que lanzan peticiones paralelas sobre la última unidad de stock comprueban que una triunfa y la otra devuelve un error de stock insuficiente (`422 Unprocessable Entity`).

---

## Artículo VII — Transición Limpia a SQLAlchemy 2.0 Async

Todo desarrollo nuevo en el backend debe implementarse utilizando el patrón moderno y asíncrono de SQLAlchemy 2.0 (`AsyncSession`, `select()`). Queda prohibido añadir nuevas dependencias o modelos a la sesión síncrona legada (`database.py`).

- **Por qué:** Unificar la base de código, evitar bloqueos en el event loop de FastAPI y garantizar alta concurrencia.
- **Cómo se verifica:** Las nuevas rutas y servicios inyectan exclusivamente `get_async_db`.

---

## Artículo VIII — Cero Secretos en el Repositorio

Ningún secreto, clave privada JWT (`SECRET_KEY`), contraseña de PostgreSQL o credencial de Redis se almacena en el código.

- **Por qué:** Seguridad estándar y protección de la infraestructura SaaS.
- **Cómo se verifica:** `.env.example` contiene todas las variables requeridas sin valores reales. Si falta `SECRET_KEY` o `DATABASE_URL`, la app se niega a arrancar ruidosamente.

---

## Artículo IX — Frontera de Idiomas

- **Inglés:** Código fuente, nombres de variables, funciones, clases, nombres de tablas, commits de Git y nombres de pruebas automáticas.
- **Español:** Textos de interfaz de usuario (React), mensajes de error y validación entregados al cliente, y documentación técnica de negocio.

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
