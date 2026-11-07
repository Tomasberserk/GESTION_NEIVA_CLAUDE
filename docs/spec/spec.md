# Especificación Funcional — Módulo POS & Inventarios (Gestión Neiva)

**Sistema:** Gestión Neiva — POS SaaS Multi-Tenant  
**Módulo:** Punto de Venta (POS), Ventas e Inventario  
**Versión:** 1.0  

---

## 1. Visión del Módulo POS

El módulo de Punto de Venta permite a los cajeros y administradores de tiendas en Neiva registrar ventas de forma ultrarrápida, gestionar medios de pago, emitir comprobantes y mantener el inventario sincronizado en tiempo real, garantizando el aislamiento absoluto de datos entre diferentes empresas suscritas al SaaS.

---

## 2. Historias de Usuario

### HU-POS-01: Registro y Cobro de Venta Rápida
> **Como** cajero de la tienda  
> **Quiero** escanear o buscar productos, agregarlos al carrito y registrar la venta con su medio de pago  
> **Para** cobrarle al cliente de forma ágil y que el inventario se descuente automáticamente sin errores.

#### Criterios de Aceptación
- **CA-01.1:** Si algún producto del carrito no tiene stock suficiente, el sistema cancela la operación atómicamente y devuelve un error descriptivo con el producto y la cantidad disponible (`422 Unprocessable Entity`).
- **CA-01.2:** Cada producto vendido almacena en la línea de venta el precio unitario y el nombre exacto que tenía al momento de la transacción (Snapshot inmutable).
- **CA-01.3:** La venta se asocia automáticamente al `tenant_id` y al `user_id` del usuario autenticado en el token JWT.
- **CA-01.4:** El stock del producto se reduce en exactamente la cantidad vendida.

### HU-POS-02: Consulta de Catálogo para el Terminal POS
> **Como** cajero de la tienda  
> **Quiero** buscar productos por código de barras o texto y ver su precio y stock actual  
> **Para** armar el ticket de venta en el terminal.

#### Criterios de Aceptación
- **CA-02.1:** Solo se listan productos pertenecientes a la empresa del cajero (`tenant_id`).
- **CA-02.2:** Solo se muestran productos con `is_active = True`.
- **CA-02.3:** La respuesta incluye SKU, nombre, precio de venta y existencias disponibles.

---

## 3. Catálogo de Reglas de Negocio (RN)

**Tabla 1**  
*Registro estructurado de especificaciones técnicas ( Sección 1 )*

| Código | Nombre de la Regla | Descripción | Severidad |
|---|---|---|---|
| `RN-01` | **No negatividad de stock** | Ninguna venta puede provocar que el stock de un producto sea menor a 0. | Bloqueante |
| `RN-02` | **Inmutabilidad de precios** | El precio registrado en la línea de venta jamás se actualiza, incluso si el catálogo cambia de precio posteriormente. | Bloqueante |
| `RN-03` | **Aislamiento Multi-Tenant** | Es imposible vender, descontar stock o consultar productos pertenecientes a otra empresa. | Bloqueante |
| `RN-04` | **Transaccionalidad Atómica** | La venta y el descuento de inventario ocurren en la misma transacción de base de datos; si una línea falla, se revierte todo. | Bloqueante |
| `RN-05` | **Baja lógica de productos** | Un producto con ventas históricas no puede borrarse físicamente; solo se marca `is_active = False`. | Bloqueante |
| `RN-06` | **Totales derivados** | El total de la venta es la suma de `(quantity * unit_price)` de sus líneas; no se almacena como dato estático redundante. | Bloqueante |

*Nota.* Especificación técnica sincronizada con la arquitectura vigente del proyecto. Fuente: Elaboración propia (2026).

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
