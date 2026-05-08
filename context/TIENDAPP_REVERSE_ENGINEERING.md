# 📋 TIENDAPP - Documento Técnico de Reverse Engineering
**Proyecto:** Gestión Inteligente Neiva - SaaS POS  
**Stack:** FastAPI (Backend) + React/Vite (Frontend) + PostgreSQL  
**Fecha de Análisis:** Mayo 5, 2026  
**Propósito:** Hoja de Ruta para migración hacia arquitectura orquestada por Claude Code

---

## 🏗️ 1. ESQUEMA DE DATOS (PostgreSQL)

### 1.1 Estructura de Tablas

#### **Tabla: `empresas`**
```sql
CREATE TABLE empresas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre_comercial VARCHAR(150) NOT NULL,
    nit_o_cedula VARCHAR(50) UNIQUE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);
```
**Características:**
- Identificador único para cada negocio (Multi-tenant)
- NIT o Cédula como dato único regulatorio
- Referencia para todas las otras tablas

---

#### **Tabla: `usuarios`**
```sql
CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR (NOT NULL),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    rol VARCHAR(50) NOT NULL DEFAULT 'tendero',  -- 'admin' o 'tendero'
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_usuarios_email ON usuarios(email);
```
**Características:**
- Autenticación por email + contraseña hasheada con bcrypt
- Rol basado en dos niveles: admin (puede crear productos) o tendero (solo vende)
- Aislamiento multi-tenant vinculado a empresa_id
- Index en email para búsquedas rápidas

---

#### **Tabla: `productos`**
```sql
CREATE TABLE productos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    nombre VARCHAR NOT NULL,
    codigo_barras VARCHAR(20) UNIQUE NOT NULL,
    precio_costo NUMERIC(10, 2) DEFAULT 0.00,
    precio_venta NUMERIC(10, 2) DEFAULT 0.00,
    cantidad_actual INTEGER DEFAULT 0,
    foto_url VARCHAR NULL,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);
```
**Características:**
- Precio con precisión `NUMERIC(10,2)` para evitar errores de punto flotante
- Código de barras único por negocio (validación en aplicación)
- Uso de `NUMERIC` en lugar de `FLOAT` para dinero
- URL de foto es ruta local relativa (`/media/{uuid}_filename`)
- Control de inventario en tiempo real

---

#### **Tabla: `ventas`**
```sql
CREATE TABLE ventas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    fecha_venta TIMESTAMP DEFAULT NOW(),
    total NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT NOW()
);
```
**Características:**
- Documento maestro que agrupa múltiples productos en una transacción
- Total calculado en backend (nunca en frontend)
- Multi-tenant: isolado por empresa_id

---

#### **Tabla: `detalles_venta`** (Relación 1:N con ventas)
```sql
CREATE TABLE detalles_venta (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    venta_id UUID NOT NULL REFERENCES ventas(id) ON DELETE CASCADE,
    producto_id UUID NOT NULL REFERENCES productos(id) ON DELETE RESTRICT,
    cantidad INTEGER NOT NULL,
    precio_unitario NUMERIC(10, 2) NOT NULL,  -- Congelado en el momento de venta
    subtotal NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```
**Características:**
- `precio_unitario` es snapshot histórico (si el precio del producto cambia después, el detalle conserva el precio original)
- ON DELETE RESTRICT previene borrar productos que ya fueron vendidos
- Cálculo: `subtotal = cantidad * precio_unitario`

---

### 1.2 Relaciones y Cardinalidades

```
┌─────────────────┐
│   EMPRESAS      │ (1)
└────────┬────────┘
         │
    ┌────┴─────────────────┬──────────────────┐
    │                      │                  │
(1) │                      │ (1)          (1) │
    ▼                      ▼                  ▼
┌──────────┐         ┌────────────┐   ┌───────────────┐
│ USUARIOS │ (N)     │ PRODUCTOS  │   │    VENTAS     │ (N)
└──────────┘         └────────────┘   └───────────────┘
                           │                    │
                      (1)  │              (1)   │
                           │                    │
                           └──────┬─────────────┘
                                  │
                              (N) │
                                  ▼
                          ┌──────────────────────┐
                          │  DETALLES_VENTA      │
                          │  (Relación muchos:1) │
                          └──────────────────────┘
```

---

## 🔄 2. LÓGICA DE NEGOCIO: FLUJO DE VENTAS

### 2.1 Ciclo de Vida de una Transacción POS

```
┌─────────────────────────────────────────────────────────────┐
│  1. CLIENTE SELECCIONA PRODUCTO EN VITRINA                  │
│     • Sistema busca en inventario                            │
│     • Se muestra: nombre, foto, precio_venta, stock         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  2. AGREGAR AL CARRITO (State en Frontend)                   │
│     • Cart state: [{id, nombre, cantidad, precio}]          │
│     • NO se descuenta stock aún                              │
│     • Es temporal en memoria del navegador                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  3. USUARIO HACE CLICK EN "COBRAR" (Checkout)               │
│     • Se envía POST /ventas/{empresa_id}                     │
│     • Payload: { detalles: [{producto_id, cantidad}, ...] } │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  4. BACKEND INICIA TRANSACCIÓN (ACID)                        │
│     • Valida empresa_id pertenece al usuario                 │
│     • Crea registro vacío en tabla VENTAS                    │
│     • db.flush() para obtener venta.id                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  5. POR CADA ITEM EN CARRITO:                                │
│     • .with_for_update() bloquea fila de producto            │
│     • Valida: cantidad_actual >= cantidad_solicitada        │
│     • Descuenta: producto.cantidad_actual -= cantidad       │
│     • Calcula: subtotal = precio_venta * cantidad           │
│     • Crea DetalleVenta congelando precio_unitario          │
│     • Suma a total_venta                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  6. COMMIT DE TRANSACCIÓN                                    │
│     • db.commit() persiste cambios                           │
│     • ON DELETE CASCADE garantiza integridad                 │
│     • Si hay error: db.rollback() y HTTP 400                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  7. RESPUESTA AL CLIENTE                                     │
│     • 200 OK: { "total": XXXX }                              │
│     • Carrito se vacía en frontend                           │
│     • Inventario se recarga                                  │
│     • Historial se actualiza (si usuario ve esa vista)       │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Cálculos y Validaciones Críticas

| Paso | Responsable | Validación | Error Code | Observación |
|------|-------------|-----------|-----------|-------------|
| Stock disponible | Backend | `cantidad_actual >= cantidad_solicitada` | 400 Bad Request | Bloqueo con `with_for_update()` |
| Empresa existe | Backend | `empresa_id` válido en DB | 404 Not Found | Anti-spoofing |
| Usuario pertenece empresa | Backend | `current_user.empresa_id == empresa_id` | 403 Forbidden | Seguridad multi-tenant |
| Producto existe | Backend | `producto_id` válido y pertenece empresa | 400 Bad Request | Inyección de SQL prevista |
| Cantidad > 0 | Backend | `cantidad > 0` | 400 Bad Request | Validación Pydantic |
| Autenticación JWT válida | Backend | Token no expirado, firma válida | 401 Unauthorized | OAuth2PasswordBearer |

### 2.3 Manejo de Errores 400 (Bad Request) - LECCIONES APRENDIDAS

**❌ Errores 400 encontrados en versión anterior:**

1. **"Stock insuficiente"**
   - Mensaje: `f"Stock insuficiente para {producto.nombre}. Quedan {producto.cantidad_actual}"`
   - **Causa raíz**: No se validaba antes de descontar
   - **Solución**: Usar `with_for_update()` para bloquear fila y validar ANTES de modificar

2. **"Producto no encontrado"**
   - Mensaje: `"Producto no encontrado"`
   - **Causa raíz**: `producto_id` no existe o pertenece a otra empresa
   - **Solución**: Query con ambas condiciones: `producto_id` AND `empresa_id`

3. **"Este email ya está registrado"**
   - Mensaje: `"Este email ya está registrado"`
   - **Causa raíz**: Duplicate key en email único
   - **Solución**: Pre-validar con `.first()` antes de crear

4. **"Ya existe un producto con este código de barras"**
   - Mensaje: `"Ya existe un producto con este código de barras"`
   - **Causa raíz**: Código no único a nivel tabla
   - **Solución**: Pre-validar antes de INSERT

---

## 🌐 3. PATRONES DE FRONTEND (React + Vite)

### 3.1 Arquitectura de Estados Globales

```
┌─────────────────────────────────────────────────────────────┐
│                        App.jsx (Root)                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Estado de Autenticación (Global a toda la app)      │   │
│  │  • currentUser {id, email, empresa_id, rol}        │   │
│  │  • isLoadingAuth boolean                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                   │
│        ┌─────────────────┼─────────────────┐               │
│        │                 │                 │               │
│        ▼                 ▼                 ▼               │
│   ┌─────────┐    ┌──────────────┐   ┌────────────┐        │
│   │ Login   │    │CartSidebar   │   │ProductGrid │        │
│   │Component│    │  (POS Modal)  │   │ / Historial│        │
│   └─────────┘    └──────────────┘   └────────────┘        │
│        │                 │                 │               │
│        └─────────────────┼─────────────────┘               │
│                          │ (Props drilling)                │
│        ┌─────────────────┴─────────────────┐               │
│        │                                   │               │
│        ▼                                   ▼               │
│   currentUser                        cart (Carrito)        │
│   setCurrentUser                     agregarAlCarrito      │
│   handleLogout                       restarDelCarrito      │
│                                      eliminarDelCarrito    │
│                                      procesarVenta         │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Estados Locales por Componente

#### **App.jsx**
```javascript
// Autenticación
const [currentUser, setCurrentUser] = useState(null)
const [isLoadingAuth, setIsLoadingAuth] = useState(true)

// POS
const [cart, setCart] = useState([])                    // [{id, nombre, cantidad, precio}]
const [isCartOpen, setIsCartOpen] = useState(false)
const [currentView, setCurrentView] = useState('productos') // 'productos' | 'historial'

// Inventario
const [inventario, setInventario] = useState([])        // Todos los productos de la empresa
const [tienda, setTienda] = useState("")                // nombre_comercial de la empresa

// CRUD de Productos (Admin)
const [showModal, setShowModal] = useState(false)
const [modoEdicion, setModoEdicion] = useState(false)
const [nuevoProd, setNuevoProd] = useState({...})
const [foto, setFoto] = useState(null)

// Calculated (NO es estado, es derivado)
const isAdmin = currentUser?.rol === 'admin'
```

#### **CartSidebar.jsx**
```javascript
const [procesandoVenta, setProcesandoVenta] = useState(false)
// Props: cart, isOpen, toggleCart, handleCheckout, agregarAlCarrito, restarDelCarrito, eliminarDelCarrito
```

#### **SalesHistory.jsx**
```javascript
const [ventas, setVentas] = useState([])           // [{id, fecha_venta, total, detalles}]
const [loading, setLoading] = useState(true)
const [expandedVentaId, setExpandedVentaId] = useState(null)  // UUID de la venta expandida

// Props: empresaId (para buscar en backend)
```

### 3.3 Flujo de Datos (Unidireccional)

```
Frontend useEffect()
    │
    ├─ authService.getToken()
    │  └─ localStorage['access_token']
    │
    ├─ authService.fetchWithAuth()
    │  ├─ Agrega "Authorization: Bearer {token}" header
    │  └─ Catch 401 → logout automático
    │
    └─ setInventario(data.inventario)
       └─ .map() en render para mostrar productos
```

### 3.4 Estilos y Paleta de Colores

**Tailwind Config (`tailwind.config.js`):**
```javascript
module.exports = {
  theme: {
    colors: {
      'neiva-dark-bg': '#0a0e27',        // Fondo oscuro principal
      'neiva-card': '#0f1632',           // Fondos de tarjetas
      'neiva-purple': '#a78bfa',         // Primario (Accent)
      'neiva-green': '#22c55e',          // Secundario (Éxito)
      // ... grays, reds, etc.
    }
  }
}
```

**Componentes Reutilizables:**
- Botones: `.bg-neiva-green .hover:scale-105 .rounded-full`
- Tarjetas: `.bg-neiva-card .border-gray-800 .rounded-2xl`
- Texto: `.text-gray-300 .font-bold`

### 3.5 Ciclo de Vida de Componentes

```javascript
useEffect(() => {
  // Se ejecuta SOLO al montar el componente
}, [])

useEffect(() => {
  if (currentUser) cargarInventario()
  // Se ejecuta cuando currentUser cambia (login)
}, [currentUser])

useEffect(() => {
  cargarVentas()
  // Se ejecuta cuando empresaId prop cambia
}, [empresaId])
```

---

## 🔌 4. ENDPOINTS API (REST)

### 4.1 Autenticación

| Método | Endpoint | Autenticado | Body | Respuesta | Error Codes |
|--------|----------|------------|------|-----------|------------|
| POST | `/registro` | No | `{email, password, empresa_id, rol?}` | `{access_token, token_type, usuario}` | 400 (email duplicado), 404 (empresa no existe) |
| POST | `/token` (Login) | No | `{email, password}` | `{access_token, token_type, usuario}` | 401 (credenciales incorrectas) |
| GET | `/me` | Sí (JWT) | N/A | `{id, email, empresa_id, rol, fecha_creacion}` | 401 (token inválido) |

**Headers requeridos en endpoints autenticados:**
```http
Authorization: Bearer {JWT_TOKEN}
```

### 4.2 Gestión de Empresas

| Método | Endpoint | Autenticado | Body | Respuesta |
|--------|----------|------------|------|-----------|
| POST | `/empresas/` | No | `{nombre_comercial, nit_o_cedula}` | `{mensaje, empresa}` |
| GET | `/empresas/{id}` | No | N/A | `{id, nombre_comercial, nit_o_cedula, fecha_creacion}` |

### 4.3 Gestión de Productos (Admin)

| Método | Endpoint | Requerido | Body | Respuesta | Error Codes |
|--------|----------|-----------|------|-----------|------------|
| POST | `/productos/` | `rol=admin` | `{nombre, codigo_barras, precio_costo, precio_venta, cantidad_actual, empresa_id}` | `{mensaje, producto}` | 400 (codigo duplicado), 403 (no admin) |
| GET | `/productos/{empresa_id}` | Sí (JWT) | N/A | `{tienda, total_items, inventario: []}` | 403 (no pertenece empresa), 404 (empresa no existe) |
| PUT | `/productos/{id}` | `rol=admin` | `{nombre, codigo_barras, precio_venta, ...}` | `{mensaje, producto}` | 403, 404 |
| DELETE | `/productos/{id}` | `rol=admin` | N/A | `{mensaje}` | 403, 404 |
| POST | `/productos/{id}/imagen` | Sí (JWT) | `FormData: file` | `{mensaje, url_acceso}` | 404 (producto no existe) |

### 4.4 Transacciones de Ventas (POS)

| Método | Endpoint | Autenticado | Body | Respuesta | Error Codes |
|--------|----------|------------|------|-----------|------------|
| POST | `/ventas/{empresa_id}` | Sí | `{detalles: [{producto_id, cantidad}]}` | `{mensaje, total}` | 400 (stock insuficiente, producto no existe), 403 (no pertenece empresa) |
| GET | `/ventas/{empresa_id}` | Sí | N/A | `[{id, fecha_venta, total, detalles: [{id, cantidad, precio_unitario, subtotal, producto_nombre}]}]` | 404 (empresa no existe) |

### 4.5 Reportes

| Método | Endpoint | Autenticado | Body | Respuesta |
|--------|----------|------------|------|-----------|
| GET | `/reportes/ventas/excel/{empresa_id}` | Sí | N/A | Archivo Excel (Content-Type: application/vnd.openxmlformats...) |

---

## 📊 5. LECCIONES APRENDIDAS: ERRORES 400 Y 405

### 5.1 ¿Por qué ocurrían errores 400 (Bad Request)?

#### **Error 400 #1: "No field specified"**
- **Síntoma**: Al crear producto, si falta `precio_venta`
- **Causa raíz**: Pydantic valida que es campo requerido
- **Solución**: Validar en frontend ANTES de enviar
- **Código correcto**:
```python
class ProductoCrear(BaseModel):
    precio_venta: float  # required=True by default
    # Si es opcional: precio_venta: float = 0.0
```

#### **Error 400 #2: "Stock insuficiente" (Sin transacción)`**
- **Síntoma**: Se descontaba stock pero fallaba después, quedando inconsistente
- **Causa raíz**: Sin `db.commit()` y sin `with_for_update()`
- **Solución**: Usar `with_for_update()` para bloquear fila
```python
producto = db.query(models.Producto).filter(...).with_for_update().first()
if producto.cantidad_actual < cantidad:
    raise ValueError("Stock insuficiente")  # Antes de modificar
```

#### **Error 400 #3: "Duplicate key value"**
- **Síntoma**: Al crear producto con código_barras que ya existe
- **Causa raíz**: No se pre-validaba en backend
- **Solución**: Pre-validar con `.first()`
```python
existente = db.query(models.Producto).filter(
    models.Producto.codigo_barras == codigo_barras
).first()
if existente:
    raise HTTPException(400, detail="Código duplicado")
```

#### **Error 400 #4: "Email already exists"**
- **Síntoma**: Al registrar usuario, si el email ya existe
- **Causa raíz**: Falta validación previa
- **Solución**: Pre-validar antes de crear
```python
usuario_existente = db.query(models.Usuario).filter(
    models.Usuario.email == usuario.email
).first()
if usuario_existente:
    raise HTTPException(400, detail="Email ya registrado")
```

---

### 5.2 ¿Por qué ocurrían errores 405 (Method Not Allowed)?

#### **Error 405 #1: POST a un endpoint GET-only**
- **Síntoma**: Intentar POST a `/productos/{empresa_id}` (debería ser GET)
- **Causa raíz**: Confusión entre crear (POST) vs listar (GET)
- **Solución correcta**:
  - `POST /productos/` → crear producto
  - `GET /productos/{empresa_id}` → listar productos

#### **Error 405 #2: Endpoint duplicado con mismo método**
- **Síntoma**: Dos rutas `@app.post("/ventas/{empresa_id}")` (líneas 399 y 492)
- **Causa raíz**: El agente cometió error y duplicó el endpoint
- **Síntoma observado**: La segunda ruta sobrescribía la primera
- **Solución**: Eliminar duplicados, mantener solo la versión con `get_current_user` dependency

#### **Error 405 #3: Falta de CORS**
- **Síntoma**: OPTIONS request devuelve 405
- **Causa raíz**: CORS no configurado para preflight
- **Solución**: Usar `CORSMiddleware`
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],  # GET, POST, PUT, DELETE, OPTIONS
    allow_headers=["*"],
)
```

---

### 5.3 Patrones Anti-Error Identificados

| Patrón | Previene | Ejemplo |
|--------|----------|---------|
| **Pre-validación** | 400 Duplicados/Nulos | `if db.query(...).first(): raise 400` |
| **Transaction Locks** | Inconsistencia de stock | `.with_for_update()` |
| **Multi-tenant Check** | Acceso no autorizado | Validar `current_user.empresa_id == path_empresa_id` |
| **JWT Dependencies** | 401 No autenticado | `Depends(get_current_user)` |
| **Role-based Access** | 403 Forbidden | `Depends(get_current_user_admin)` |
| **CORS Middleware** | 405 OPTIONS | `CORSMiddleware` en app |
| **Pydantic Schema Validation** | 400 Tipos | `BaseModel` con tipos fuertes |

---

## 🎯 6. MAPA DE FLUJO: REQUEST → RESPONSE

```
CLIENTE FRONTEND
    │
    ├─ USER CLICKS "Agregar al Carrito"
    │  └─ agregarAlCarrito(producto)
    │     └─ setState(cart = [...cart, {producto, cantidad: 1}])
    │
    ├─ USER CLICKS "COBRAR"
    │  └─ procesarVenta()
    │     └─ POST /ventas/{empresaId}
    │        ├─ Header: Authorization: Bearer {token}
    │        └─ Body: { detalles: [{producto_id, cantidad}] }
    │
    ▼ SERVIDOR BACKEND
    
    @app.post("/ventas/{empresa_id}")
    def registrar_venta(empresa_id: UUID, venta: VentaCrear, 
                        current_user: Usuario = Depends(get_current_user)):
    
    ├─ get_current_user(token):  # Verifica JWT
    │  └─ decode(token) → usuario_id
    │     └─ query(Usuario).filter(id=usuario_id).first()
    │
    ├─ Valida empresa_id:
    │  └─ if current_user.empresa_id != empresa_id: raise 403
    │
    ├─ Crea transacción:
    │  └─ nueva_venta = Venta(empresa_id, total=0)
    │     └─ db.add(nueva_venta)
    │        └─ db.flush()  # Obtener venta.id sin commit
    │
    ├─ Loop por cada detalle:
    │  ├─ query(Producto).filter(...).with_for_update().first()
    │  ├─ if producto.cantidad < cantidad: raise 400
    │  ├─ producto.cantidad_actual -= cantidad
    │  ├─ subtotal = producto.precio_venta * cantidad
    │  ├─ detalle = DetalleVenta(...)
    │  ├─ db.add(detalle)
    │  └─ total_venta += subtotal
    │
    ├─ db.commit()
    │  └─ Persiste cambios en PostgreSQL
    │
    └─ return {"mensaje": "...", "total": total_venta}
    
    ▼ CLIENTE FRONTEND
    
    if response.ok:
        ├─ setCart([])           # Vacía carrito
        ├─ cargarInventario()    # Recarga stocks
        └─ alert("¡Éxito!")
    else:
        └─ alert(response.detail)
```

---

## 🔐 7. SEGURIDAD: Medidas Implementadas

| Medida | Mecanismo | Beneficio |
|--------|-----------|----------|
| **JWT (Access Tokens)** | OAuth2PasswordBearer | Stateless auth, no requiere sesión |
| **Contraseñas Hasheadas** | bcrypt (passlib) | No se almacenan en texto plano |
| **Multi-tenant Isolation** | `empresa_id` en cada query | Un usuario no puede ver datos de otra empresa |
| **Role-based Authorization** | `rol` field en Usuario | Admins vs Tenderos tienen permisos diferentes |
| **CORS** | CORSMiddleware | Solo frontend autorizado puede acceder |
| **Transaction Locks** | `.with_for_update()` | Previene race conditions en stock |
| **ON DELETE CASCADE/RESTRICT** | Foreign keys | Integridad referencial |

---

## 📦 8. STACK TÉCNICO: Versiones y Dependencias

### Backend (Python)
```
Python 3.10+
FastAPI 0.104.1
SQLAlchemy 2.0
psycopg2-binary (PostgreSQL)
pydantic 2.0
passlib[bcrypt]
python-jose[cryptography]
python-multipart
```

### Frontend (Node.js)
```
React 19.2.5
Vite 8.0.10
Tailwind CSS 4.2.4
lucide-react 1.14.0
(No state management library - Props drilling)
```

### Base de Datos
```
PostgreSQL 14+
UUID extension
```

---

## 📝 9. ARCHIVOS CRÍTICOS

### Backend
- `app/main.py` (701 líneas) - Rutas, esquemas, lógica principal
- `app/models.py` (88 líneas) - ORM SQLAlchemy, relaciones
- `app/security.py` (122 líneas) - JWT, hashing, dependencies
- `app/database.py` (31 líneas) - Conexión PostgreSQL

### Frontend
- `frontend/src/App.jsx` (~280 líneas) - Root component, lógica POS
- `frontend/src/components/CartSidebar.jsx` - Carrito de compras
- `frontend/src/components/SalesHistory.jsx` - Historial de ventas
- `frontend/src/components/Login.jsx` - Autenticación
- `frontend/src/services/authService.js` - Wrapper para fetch + JWT

---

## 🎁 10. CONSIDERACIONES PARA MIGRACIÓN A CLAUDE CODE

### Ventajas de la arquitectura actual que hay que mantener:
1. ✅ Multi-tenant bien aislado (enterprise-ready)
2. ✅ Autenticación robusta con JWT
3. ✅ Transacciones ACID en ventas
4. ✅ Separación clara de responsabilidades (Backend/Frontend)
5. ✅ Validaciones en dos capas (Pydantic + Frontend)

### Oportunidades de mejora:
1. ❌ Props drilling en React (pasar a Context API o Zustand)
2. ❌ No hay manejo de errores global en frontend
3. ❌ Duplicidad de esquemas Pydantic (se repiten líneas 57-62, 64-82, 371-389, etc.)
4. ❌ Logs estructurados ausentes
5. ❌ No hay soft deletes (auditoría)
6. ❌ No hay versionado de API (v1/, v2/)

### Checklist para nueva arquitectura:
- [ ] Normalizar esquemas Pydantic (single source of truth)
- [ ] Implementar logging con `structlog` o `python-json-logger`
- [ ] Usar Context API en React para estados globales
- [ ] Agregar Enums para roles y estados de venta
- [ ] Implementar auditoría (created_by, updated_by, deleted_at)
- [ ] Agregar rate limiting
- [ ] Implementar refresh tokens
- [ ] Tests unitarios y de integración
- [ ] CI/CD pipeline (GitHub Actions)

---

## 📞 RESUMEN EJECUTIVO

**Tiendapp** es un sistema POS SaaS especializado en gestión de negocios pequeños en Neiva. Su arquitectura es **fundamentalmente sólida** pero requiere **refactorización y escalabilidad**. Los errores 400/405 no son defectos del diseño sino **inconsistencias de implementación** que pueden prevenirse con las pautas documentadas.

La migración hacia una arquitectura orquestada por Claude Code debe **preservar** la filosofía multi-tenant y ACID, mientras **moderniza** el frontend y centraliza la lógica de negocio.

---

**Fin del Documento**  
*Autogenerado por Reverse Engineering - Mayo 5, 2026*
