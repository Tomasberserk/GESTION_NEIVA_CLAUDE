# Template Professional — Guía de Personalización y Despliegue

Este documento contiene los pasos detallados que un desarrollador o un agente Haiku-worker de la fábrica debe seguir para configurar, personalizar y desplegar un sistema SaaS corporativo de gama alta bajo el **Tier Professional**.

---

## ⚙️ 1. Configuración de Variables de Entorno (.env)

El archivo `.env` del Tier Professional requiere configurar credenciales seguras para pasarelas de pago, autenticación federada, colas de tareas y conexión remota a la base de datos PostgreSQL.

```ini
# =============================================================================
# ENTORNO Y BASE DE DATOS ASINCRÓNICA (asyncpg)
# =============================================================================
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/pos_professional
PG_MAX_OVERFLOW=20
PG_POOL_SIZE=10

# =============================================================================
# BROKER Y CACHÉ (Redis para Celery y Rate Limiting)
# =============================================================================
REDIS_URL=redis://localhost:6379/0

# =============================================================================
# OAUTH2 / SSO GOOGLE
# =============================================================================
GOOGLE_CLIENT_ID=google-oauth-client-id-a1b2c3d4.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=google-oauth-client-secret-key-xyz
GOOGLE_REDIRECT_URI=https://neiva.tiendapp.com/api/v1/auth/sso/google/callback

# =============================================================================
# PASARELA DE PAGOS (Stripe o Wompi)
# =============================================================================
PAYMENT_GATEWAY_API_KEY=sk_test_51N2b3c4d...
PAYMENT_GATEWAY_WEBHOOK_SECRET=whsec_a1b2c3d4...

# =============================================================================
# PROVEEDOR TECNOLÓGICO DIAN (Colombia)
# =============================================================================
PROVEEDOR_TECNOLOGICO_URL=https://api.proveedor.com/v1
PROVEEDOR_TECNOLOGICO_TOKEN=pt_live_a1b2c3d4e5...
```

---

## 🏛️ 2. Guía de Configuración e Infraestructura Paso a Paso

### Paso 1: Inicializar Esquema Multi-Tenant Base
1. Crea el esquema global público en tu base de datos PostgreSQL.
2. Corre las migraciones base de Alembic para el esquema `public`:
   ```bash
   .venv/bin/alembic -cfg alembic_public.ini upgrade head
   ```
3. Registra la plantilla DDL del esquema de tenant (`tenant_xxxx.sql`) que la aplicación ejecutará dinámicamente cada vez que un cliente complete su registro corporativo.

### Paso 2: Configurar Enrutamiento Dinámico de Esquemas en FastAPI
1. Implementa la clase `TenantSessionManager` en `app/database.py` que herede de `AsyncSession` de SQLAlchemy.
2. Diseña un middleware de FastAPI que capture la cabecera `X-Tenant-Schema` o resuelva el subdominio (`tenant1.tiendapp.com` $\rightarrow$ esquema `tenant_1`).
3. Antes de ejecutar la consulta, inyecta la instrucción SQL de enrutamiento:
   ```python
   async def set_tenant_schema(db_session, schema_name: str):
       await db_session.execute(text(f"SET search_path TO {schema_name}"))
   ```

### Paso 3: Inicializar la Cola de Tareas (Celery + Redis)
1. Instala Celery en el entorno virtual:
   ```bash
   .venv/bin/pip install celery redis
   ```
2. Inicializa el worker de Celery apuntando a tu broker de Redis en la configuración de la infraestructura de Docker/Servidor:
   ```bash
   .venv/bin/celery -A app.core.celery_app worker --loglevel=info
   ```
3. Mapea la tarea `emitir_factura_dian_task` como una tarea asíncrona (`@celery_app.task`).

### Paso 4: Configurar los Webhooks Seguros de Pago
1. Registra la URL del Webhook de pagos (`https://api.tu-app.com/api/v1/billing/webhook`) en el panel de desarrollador de Stripe o Wompi.
2. Al procesar la llamada de la pasarela, implementa la verificación criptográfica del payload:
   ```python
   # Ejemplo de validación criptográfica en Python
   signature = request.headers.get("Stripe-Signature")
   try:
       event = stripe.Webhook.construct_event(
           payload, signature, settings.PAYMENT_GATEWAY_WEBHOOK_SECRET
       )
   except ValueError as e:
       raise HTTPException(status_code=400, detail="Payload inválido")
   except stripe.error.SignatureVerificationError as e:
       raise HTTPException(status_code=400, detail="Firma inválida")
   ```

### Paso 5: Registro del Portal DIAN (Ambiente de Habilitación)
1. Inicia sesión en el portal oficial de habilitación de la DIAN mediante el NIT de tu empresa SaaS.
2. Registra el software y obtén el **Código de Habilitación**.
3. Realiza la tanda de pruebas obligatoria (emisión de 10 facturas, 5 notas débito, 5 notas crédito de prueba) de manera automática consumiendo la API de sandbox del Proveedor Tecnológico para habilitar tu software en ambiente de producción real.
