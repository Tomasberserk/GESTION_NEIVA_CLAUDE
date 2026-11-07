# Modelo de Datos — Módulo POS & Inventarios (Gestión Neiva)

**Motor:** PostgreSQL 16  
**ORM:** SQLAlchemy 2.0 (Modelos declarativos con `Mapped` y `mapped_column`)  
**Esquema:** Multi-Tenant con discriminador `tenant_id` por fila  

---

## 1. Tablas Principales

### Tabla: `tenants` (Empresas / Tiendas)
**Tabla 1**  
*Registro estructurado de especificaciones técnicas ( Sección 1 )*

| Columna | Tipo | Nulable | Restricción | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK | Identificador de la tienda |
| `nombre` | `VARCHAR(150)` | No | | Nombre de la tienda o razón social |
| `nit` | `VARCHAR(30)` | No | UNIQUE | Identificación fiscal |
| `is_active` | `BOOLEAN` | No | DEFAULT `TRUE` | Estado de suscripción |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | No | DEFAULT `NOW()` | Fecha de registro |

*Nota.* Especificación técnica sincronizada con la arquitectura vigente del proyecto. Fuente: Elaboración propia (2026).

### Tabla: `productos`
**Tabla 2**  
*Registro estructurado de especificaciones técnicas ( Sección 2 )*

| Columna | Tipo | Nulable | Restricción | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK | Identificador único del producto |
| `tenant_id` | `UUID` | No | FK -> `tenants(id)` | Tienda dueña del producto |
| `codigo_barras` | `VARCHAR(60)` | Sí | | Código de barras o SKU |
| `nombre` | `VARCHAR(150)` | No | | Nombre descriptivo |
| `precio` | `NUMERIC(12, 2)` | No | CHECK (`precio` >= 0) | Precio de venta actual |
| `costo` | `NUMERIC(12, 2)` | No | CHECK (`costo` >= 0) | Costo de adquisición |
| `stock` | `INT` | No | CHECK (`stock` >= 0) | Unidades físicas disponibles |
| `is_active` | `BOOLEAN` | No | DEFAULT `TRUE` | Soft delete / estado activo |
| `version` | `INT` | No | DEFAULT `1` | Token de concurrencia optimista |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | No | DEFAULT `NOW()` | Auditoría |
| `updated_at` | `TIMESTAMP WITH TIME ZONE` | No | DEFAULT `NOW()` | Auditoría |

*Nota.* Especificación técnica sincronizada con la arquitectura vigente del proyecto. Fuente: Elaboración propia (2026).

### Tabla: `ventas` (Cabecera)
**Tabla 3**  
*Registro estructurado de especificaciones técnicas ( Sección 3 )*

| Columna | Tipo | Nulable | Restricción | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK | Identificador de la transacción |
| `tenant_id` | `UUID` | No | FK -> `tenants(id)` | Tienda donde ocurrió la venta |
| `usuario_id` | `UUID` | No | FK -> `usuarios(id)` | Cajero que registró la venta |
| `cliente_id` | `UUID` | Sí | FK -> `clientes(id)` | Cliente (opcional) |
| `medio_pago` | `VARCHAR(30)` | No | | Efectivo, Nequi, Tarjeta, etc. |
| `fecha_venta` | `TIMESTAMP WITH TIME ZONE` | No | DEFAULT `NOW()` | Momento exacto de la venta |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | No | DEFAULT `NOW()` | Auditoría |

*Nota.* Especificación técnica sincronizada con la arquitectura vigente del proyecto. Fuente: Elaboración propia (2026).

> **Nota Constitucional:** No se incluye columna estática `total`. Se calcula sumando `(cantidad * precio_unitario)` de las líneas de detalle.

### Tabla: `detalles_venta` (Líneas de Venta / Snapshot)
**Tabla 4**  
*Registro estructurado de especificaciones técnicas ( Sección 4 )*

| Columna | Tipo | Nulable | Restricción | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | PK | Identificador de la línea |
| `tenant_id` | `UUID` | No | FK -> `tenants(id)` | Tienda (desnormalizado para auditoría) |
| `venta_id` | `UUID` | No | FK -> `ventas(id)` ON DELETE CASCADE | Venta asociada |
| `producto_id` | `UUID` | No | FK -> `productos(id)` | Producto vendido |
| `nombre_historico` | `VARCHAR(150)` | No | | **Snapshot:** Nombre del producto al vender |
| `precio_unitario` | `NUMERIC(12, 2)` | No | CHECK (`precio_unitario` >= 0) | **Snapshot:** Precio congelado |
| `cantidad` | `INT` | No | CHECK (`cantidad` > 0) | Cantidad vendida |

*Nota.* Especificación técnica sincronizada con la arquitectura vigente del proyecto. Fuente: Elaboración propia (2026).

---

## 2. Índices de Alto Rendimiento

**Tabla 5**  
*Registro estructurado de especificaciones técnicas ( Sección 5 )*

| Tabla | Columnas | Propósito / Consulta protegida |
|---|---|---|
| `productos` | `(tenant_id, codigo_barras)` | Búsqueda ultrarrápida en caja por lector de código de barras. |
| `productos` | `(tenant_id, is_active, nombre)` | Catálogo y búsqueda por texto en la interfaz del POS. |
| `ventas` | `(tenant_id, fecha_venta)` | Reportes de ventas por turnos, días o rangos de fecha por tienda. |
| `detalles_venta` | `(venta_id)` | Carga inmediata de los productos de un ticket de venta. |

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
