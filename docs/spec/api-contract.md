# Contrato de API — Módulo POS & Inventarios (Gestión Neiva)

**Base URL:** `/api/v1`  
**Autenticación:** `Authorization: Bearer <JWT>`  
**Formato de Fechas:** ISO 8601 UTC (`YYYY-MM-DDTHH:mm:ssZ`)  

---

## 1. Convención de Respuestas de Error (RFC 7807)

```json
{
  "type": "https://api.gestionneiva.com/errors/insufficient-stock",
  "title": "Stock Insuficiente",
  "status": 422,
  "detail": "El producto 'Arroz Roa 1kg' tiene 3 unidades disponibles y se intentó vender 5.",
  "instance": "/api/v1/sales"
}
```

---

## 2. Endpoints Principales

### `POST /api/v1/sales` — Registrar Venta POS
Registra la transacción de venta, congela precios y descuenta inventario de forma atómica.

#### Cabeceras
- `Authorization`: `Bearer <token>` (El token contiene `tenant_id` y `user_id`)

#### Request Body
```json
{
  "medioPago": "efectivo",
  "clienteId": null,
  "items": [
    {
      "productoId": "8f1a3a40-2a8b-4bfa-93e1-3829ad48b812",
      "cantidad": 2
    },
    {
      "productoId": "1b2c3d4e-5f6a-7b8c-9d0e-1f2a3b4c5d6e",
      "cantidad": 1
    }
  ]
}
```

#### Respuesta Exitosa (`201 Created`)
```json
{
  "id": "c7a8b9d0-1e2f-3a4b-5c6d-7e8f9a0b1c2d",
  "fechaVenta": "2026-09-28T23:15:00Z",
  "medioPago": "efectivo",
  "total": 34500.00,
  "items": [
    {
      "productoId": "8f1a3a40-2a8b-4bfa-93e1-3829ad48b812",
      "nombreHistorico": "Arroz Roa 1kg",
      "precioUnitario": 4500.00,
      "cantidad": 2,
      "subtotal": 9000.00
    },
    {
      "productoId": "1b2c3d4e-5f6a-7b8c-9d0e-1f2a3b4c5d6e",
      "nombreHistorico": "Aceite Gourmet 1000ml",
      "precioUnitario": 25500.00,
      "cantidad": 1,
      "subtotal": 25500.00
    }
  ]
}
```

#### Códigos de Error
- `400 Bad Request`: `items` vacío o cantidades <= 0.
- `404 Not Found`: Si algún producto no existe o pertenece a otra empresa (`tenant_id`).
- `409 Conflict`: Conflicto de versión / concurrencia en stock.
- `422 Unprocessable Entity`: Stock insuficiente para satisfacer la venta.

---

### `GET /api/v1/products/pos-search` — Búsqueda en Terminal POS
Permite buscar productos en caja por código de barras o término de búsqueda.

#### Query Parameters
- `q`: Término de búsqueda (SKU, código de barras o parte del nombre).

#### Respuesta Exitosa (`200 OK`)
```json
[
  {
    "id": "8f1a3a40-2a8b-4bfa-93e1-3829ad48b812",
    "codigoBarras": "7701234567890",
    "nombre": "Arroz Roa 1kg",
    "precio": 4500.00,
    "stock": 28
  }
]
```

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
