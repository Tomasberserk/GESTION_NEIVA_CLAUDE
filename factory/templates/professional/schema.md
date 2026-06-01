# Template Professional — Esquema de Base de Datos y Aislamiento Avanzado

Este documento define el estándar de base de datos relacional para los sistemas construidos bajo el **Tier Professional** de la fábrica. Este tier implementa aislamiento estricto de datos multi-tenant y soporte para operaciones complejas como suscripciones, integraciones externas (APIs) y facturación fiscal.

---

## 🏛️ 1. Estrategia de Aislamiento: Schema-per-Tenant

Para el Tier Professional, se descarta el filtrado lógico por `empresa_id` en tablas compartidas (usado en Basic/Medium). En su lugar, se implementa **aislamiento por esquemas lógicos dentro de la misma base de datos PostgreSQL** (`schema-per-tenant`).

```
                              Base de Datos PostgreSQL (SaaS)
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    ▼                                               ▼
         Esquema Público ("public")                   Esquemas de Tenants ("tenant_xxxx")
      ┌─────────────────────────────┐               ┌─────────────────────────────────────┐
      │  tenants (Registro Tenants) │               │  usuarios (Específico del Tenant)   │
      │  planes (Planes de Pago)    │               │  productos (Inventario del Tenant)  │
      │  api_keys (Acceso API Ext)  │               │  ventas (Transacciones POS)         │
      │  sso_accounts (Google/SSO)  │               │  resoluciones_dian (Fiscal Col)     │
      └─────────────────────────────┘               │  facturas_dian (XML / CUFE)         │
                                                    └─────────────────────────────────────┘
```

### Ventajas de este Modelo:
1. **Aislamiento de Datos Real:** Las consultas SQL del tenant ejecutan directamente en su propio namespace (`SET search_path TO tenant_abc`), eliminando la posibilidad de fuga de información entre empresas por un filtro `WHERE` olvidado.
2. **Escalabilidad y Backups:** Permite extraer y restaurar el esquema de un cliente corporativo de manera independiente con `pg_dump --schema`.
3. **Esquema de Conexiones:** Enrutamiento dinámico asíncrono en FastAPI gestionado por una sesión dinámica de SQLAlchemy que intercepta el subdominio o header `X-Tenant-Schema`.

---

## 🔑 2. Tablas del Esquema Público (`public`)

El esquema `public` almacena los datos de control global del SaaS, facturación de clientes y credenciales de acceso externas.

### A. Tabla `tenants`
Registra cada empresa cliente que contrata el servicio.
```sql
CREATE TABLE public.tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre_comercial VARCHAR(150) NOT NULL,
    nit_o_cedula VARCHAR(50) UNIQUE NOT NULL,
    schema_name VARCHAR(63) UNIQUE NOT NULL, -- Nombre del esquema PostgreSQL (ej. 'tenant_neiva_1')
    plan_id UUID REFERENCES public.planes(id),
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX idx_tenants_schema ON public.tenants(schema_name);
```

### B. Tabla `planes`
Controla los niveles de precios, límites de usuarios y de inventario.
```sql
CREATE TABLE public.planes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(50) UNIQUE NOT NULL, -- 'basic', 'medium', 'professional'
    precio_mensual NUMERIC(10, 2) NOT NULL,
    limite_usuarios INT NOT NULL, -- Límite de cuentas por tenant
    limite_productos INT NOT NULL, -- Límite de productos activos en inventario
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
```

### C. Tabla `api_keys`
Credenciales seguras para que terceros se conecten a la API pública de un tenant.
```sql
CREATE TABLE public.api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE NOT NULL,
    client_name VARCHAR(100) NOT NULL, -- Nombre de la app (ej. 'Shopify Sync')
    api_key_hashed VARCHAR(255) UNIQUE NOT NULL, -- Hash SHA-256 de la llave pública
    rate_limit INT DEFAULT 60 NOT NULL, -- Peticiones por minuto permitidas
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX idx_api_keys_hash ON public.api_keys(api_key_hashed);
```

### D. Tabla `sso_accounts`
Mapeo de inicios de sesión federados (como Google OAuth2).
```sql
CREATE TABLE public.sso_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    provider_name VARCHAR(50) NOT NULL, -- 'google'
    provider_user_id VARCHAR(255) NOT NULL, -- ID único del proveedor de SSO
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(provider_name, provider_user_id)
);
```

---

## 🏬 3. Tablas Específicas de cada Tenant (`tenant_xxxx`)

Cada vez que se registra un nuevo tenant, el sistema crea dinámicamente su esquema (`CREATE SCHEMA tenant_xxxx`) e inicializa este conjunto de tablas dentro de su namespace.

### A. Tabla `usuarios`
```sql
CREATE TABLE tenant_xxxx.usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    rol VARCHAR(30) DEFAULT 'tendero' NOT NULL, -- 'admin', 'tendero'
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
```

### B. Tabla `productos`
Inventario optimizado para productos físicos, fraccionados y con alertas fiscales.
```sql
CREATE TABLE tenant_xxxx.productos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(150) NOT NULL,
    codigo_barras VARCHAR(50) UNIQUE NOT NULL,
    precio_costo NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    precio_venta NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    cantidad_actual NUMERIC(10, 3) DEFAULT 0.000 NOT NULL,
    unidad_medida VARCHAR(20) DEFAULT 'unidad' NOT NULL, -- 'unidad', 'gramo', 'libra', 'kilo'
    categoria VARCHAR(50),
    fecha_vencimiento DATE,
    foto_url VARCHAR(255),
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
```

### C. Tabla `ventas`
```sql
CREATE TABLE tenant_xxxx.ventas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fecha_venta TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    total NUMERIC(10, 2) NOT NULL,
    creado_por UUID REFERENCES tenant_xxxx.usuarios(id),
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
```

### D. Tabla `detalles_venta`
```sql
CREATE TABLE tenant_xxxx.detalles_venta (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    venta_id UUID REFERENCES tenant_xxxx.ventas(id) ON DELETE CASCADE NOT NULL,
    producto_id UUID REFERENCES tenant_xxxx.productos(id) ON DELETE RESTRICT NOT NULL,
    cantidad NUMERIC(10, 3) NOT NULL,
    precio_unitario NUMERIC(10, 2) NOT NULL, -- Snapshot al momento de la venta
    subtotal NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
```

### E. Tabla `resoluciones_dian` (Fiscal Colombia)
Almacena las autorizaciones consecutivas de la DIAN para facturación POS electrónica.
```sql
CREATE TABLE tenant_xxxx.resoluciones_dian (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_resolucion VARCHAR(100) NOT NULL,
    prefijo VARCHAR(10),
    rango_desde INT NOT NULL,
    rango_hasta INT NOT NULL,
    consecutivo_actual INT NOT NULL, -- Siguiente número a facturar
    fecha_autorizacion DATE NOT NULL,
    vigencia_meses INT NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
```

### F. Tabla `facturas_dian` (Reportes DIAN)
Bitácora de emisión y validación de las facturas enviadas a la DIAN.
```sql
CREATE TABLE tenant_xxxx.facturas_dian (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    venta_id UUID REFERENCES tenant_xxxx.ventas(id) ON DELETE RESTRICT UNIQUE NOT NULL,
    resolucion_id UUID REFERENCES tenant_xxxx.resoluciones_dian(id) NOT NULL,
    numero_factura VARCHAR(50) NOT NULL, -- Ej: 'SETP184'
    cufe VARCHAR(100) UNIQUE NOT NULL, -- Código Único de Factura Electrónica
    xml_url VARCHAR(255) NOT NULL, -- Ruta de almacenamiento en S3/Cloud Storage del XML UBL firmado
    pdf_url VARCHAR(255) NOT NULL, -- Ruta del PDF con representación gráfica y código QR
    estado_dian VARCHAR(30) DEFAULT 'pendiente' NOT NULL, -- 'aprobado', 'rechazado', 'error_tecnico'
    mensaje_dian TEXT, -- Respuesta de error o validación de la DIAN
    fecha_emision TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
```
