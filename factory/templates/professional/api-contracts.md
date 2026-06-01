# Template Professional — Contratos de API REST

Este documento define la firma de los endpoints, payloads de entrada/salida y las políticas de seguridad para las funcionalidades exclusivas del **Tier Professional** de la fábrica de agentes.

---

## 🔑 1. Autenticación y Single Sign-On (SSO Google)

El sistema soporta inicio de sesión tradicional y federado con Google OAuth2.

### A. Obtener URL de Autorización Google
Redirecciona al usuario a la pantalla de consentimientos de Google.
* **Ruta:** `GET /api/v1/auth/sso/google`
* **Query Params:**
  * `redirect_uri` (string, obligatorio): URL del frontend para retornar el token de sesión final.
* **Respuesta (200 OK):**
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=..."
}
```

### B. Callback de Google OAuth
Recibe el código temporal de Google, intercambia perfil de usuario, verifica si existe el tenant/usuario, y emite el JWT.
* **Ruta:** `GET /api/v1/auth/sso/google/callback`
* **Query Params:**
  * `code` (string, obligatorio): Código de autorización temporal de Google.
  * `state` (string, opcional): Token CSRF.
* **Respuesta (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "usuario": {
    "id": "8c4a921d-72e2-45e0-82fe-02554737aa12",
    "email": "carlos.tendero@gmail.com",
    "rol": "admin"
  }
}
```

---

## 💳 2. Suscripciones y Webhooks de Pasarelas (Stripe / Wompi)

Maneja los pagos recurrentes para monetizar la plataforma POS SaaS.

### A. Crear Sesión de Checkout
Genera el enlace de cobro de suscripción en Stripe o Wompi.
* **Ruta:** `POST /api/v1/billing/checkout`
* **Cabecera obligatoria:** `Authorization: Bearer <token_jwt>`
* **Payload de entrada:**
```json
{
  "plan_id": "3b2a912d-12e2-45e0-82fe-02554737bb90",
  "success_url": "https://neiva.tiendapp.com/billing/success",
  "cancel_url": "https://neiva.tiendapp.com/billing/cancel"
}
```
* **Respuesta (201 Created):**
```json
{
  "session_id": "cs_test_a1b2c3d4...",
  "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_..."
}
```

### B. Webhook de Pasarela de Pagos (Asíncrono)
Procesa notificaciones de cobros exitosos, renovaciones y cancelaciones.
* **Ruta:** `POST /api/v1/billing/webhook`
* **Seguridad:** Requiere validar firma criptográfica en cabecera `Stripe-Signature` o `X-Wompi-Signature`.
* **Payload de entrada (Stripe Evento Ejemplo):**
```json
{
  "id": "evt_1N2b3c4d...",
  "type": "invoice.payment_succeeded",
  "data": {
    "object": {
      "subscription": "sub_1N2b3c...",
      "customer_email": "carlos.tendero@gmail.com",
      "amount_paid": 5000000,
      "currency": "cop"
    }
  }
}
```
* **Respuesta (200 OK):**
```json
{
  "status": "success",
  "processed": true
}
```

---

## 🔌 3. API Pública para Integraciones (eCommerce)

Permite a los comercios conectar sus inventarios y ventas con Shopify, WooCommerce u otras herramientas.

### A. Generar Llave de API Pública
* **Ruta:** `POST /api/v1/developer/keys`
* **Cabecera obligatoria:** `Authorization: Bearer <token_jwt>` (Rol ADMIN)
* **Payload de entrada:**
```json
{
  "client_name": "Sincronizador WooCommerce"
}
```
* **Respuesta (201 Created):**
```json
{
  "id": "e2a391cd-45e2-45e0-82fe-02554737cc55",
  "client_name": "Sincronizador WooCommerce",
  "api_key": "gn_live_9a8b7c6d5e4f3g2h1i0j...", -- Llave en texto plano (SE MUESTRA SOLO UNA VEZ)
  "created_at": "2026-05-24T20:12:45Z"
}
```

### B. Sincronizar Inventario (Acceso de Terceros)
* **Ruta:** `GET /api/v1/external/productos`
* **Cabecera obligatoria:** `X-API-Key: gn_live_9a8b7c6d5e4f3g2h1i0j...`
* **Respuesta (200 OK):**
```json
{
  "productos": [
    {
      "id": "a1b2c3d4-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
      "nombre": "Arroz Diana 1kg",
      "codigo_barras": "7701234567890",
      "precio_venta": 4500.0,
      "cantidad_actual": 82.5,
      "unidad_medida": "kilo"
    }
  ]
}
```

---

## 🇨🇴 4. Facturación Electrónica (DIAN Colombia)

API para registrar resoluciones autorizadas y emitir documentos electrónicos validados.

### A. Registrar Resolución de Facturación
* **Ruta:** `POST /api/v1/facturacion/resoluciones`
* **Cabecera obligatoria:** `Authorization: Bearer <token_jwt>` (Rol ADMIN)
* **Payload de entrada:**
```json
{
  "numero_resolucion": "18764000000123",
  "prefijo": "SETP",
  "rango_desde": 1,
  "rango_hasta": 5000,
  "fecha_autorizacion": "2026-01-15",
  "vigencia_meses": 12
}
```
* **Respuesta (201 Created):**
```json
{
  "id": "5c4a921d-72e2-45e0-82fe-02554737bb12",
  "numero_resolucion": "18764000000123",
  "prefijo": "SETP",
  "consecutivo_actual": 1,
  "is_active": true
}
```

### B. Emitir Factura Electrónica (DIAN / Webhook)
Genera el XML firmado, calcula el CUFE y comunica de forma asíncrona con el Proveedor Tecnológico para validación de la DIAN.
* **Ruta:** `POST /api/v1/facturacion/emitir/{venta_id}`
* **Cabecera obligatoria:** `Authorization: Bearer <token_jwt>`
* **Respuesta (202 Accepted):**
```json
{
  "venta_id": "a9b8c7d6-e5f4-3a2b-1c0d-9e8f7a6b5c4d",
  "estado": "procesando",
  "mensaje": "La factura electrónica ha sido encolada para firma y validación ante la DIAN."
}
```

* **Resultado Final del Callback / Consulta de Estado (`GET /api/v1/facturacion/estado/{venta_id}`):**
```json
{
  "venta_id": "a9b8c7d6-e5f4-3a2b-1c0d-9e8f7a6b5c4d",
  "numero_factura": "SETP1",
  "cufe": "f8a790184b84c8a8d7901c8e847a7d90e8f81a7b8e...", -- HASH SHA-384
  "xml_url": "https://storage.googleapis.com/tiendapp-facturas/xml/tenant_1/SETP1.xml",
  "pdf_url": "https://storage.googleapis.com/tiendapp-facturas/pdf/tenant_1/SETP1.pdf",
  "estado_dian": "aprobado",
  "mensaje_dian": "Documento validado exitosamente por la DIAN.",
  "fecha_emision": "2026-05-24T20:15:30Z"
}
```
