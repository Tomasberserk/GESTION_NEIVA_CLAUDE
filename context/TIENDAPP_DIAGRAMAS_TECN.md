# 📐 TIENDAPP - DIAGRAMAS TÉCNICOS Y MATRICES DE REFERENCIA

## 1. DIAGRAMA DE ARQUITECTURA GENERAL

```
┌──────────────────────────────────────────────────────────────────────┐
│                        INTERNET / USUARIOS                            │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
        ┌───────────▼──────────┐  ┌──────────▼─────────────┐
        │   FRONTEND REACT     │  │  (Futuro) MOBILE APP   │
        │   Vite 8.0           │  │  React Native / Flutter│
        │   Tailwind CSS       │  │                        │
        │   Port: 5173         │  │  (Mismo Backend)       │
        └───────────┬──────────┘  └──────────────────────────┘
                    │
                    │ HTTPS (Producción)
                    │ HTTP (Desarrollo)
                    │
        ┌───────────▼────────────────────────────────────┐
        │         CORS MIDDLEWARE (Validar origen)       │
        └───────────┬────────────────────────────────────┘
                    │
        ┌───────────▼────────────────────────────────────┐
        │       FASTAPI SERVER (Port 8000)               │
        │  ┌─────────────────────────────────────────┐  │
        │  │   OAuth2PasswordBearer (JWT)            │  │
        │  │   • Valida token en Authorization header │  │
        │  │   • Extrae usuario_id del payload       │  │
        │  │   • Valida empresa_id                   │  │
        │  └─────────────────────────────────────────┘  │
        │  ┌─────────────────────────────────────────┐  │
        │  │   Dependency Injection                  │  │
        │  │   • get_current_user                    │  │
        │  │   • get_current_user_admin              │  │
        │  │   • get_db (SessionLocal)               │  │
        │  └─────────────────────────────────────────┘  │
        │  ┌─────────────────────────────────────────┐  │
        │  │   Routes (Endpoints)                    │  │
        │  │   • Auth (/registro, /token, /me)       │  │
        │  │   • Products (/productos)               │  │
        │  │   • Sales (/ventas)                     │  │
        │  │   • Reports (/reportes)                 │  │
        │  └─────────────────────────────────────────┘  │
        │  ┌─────────────────────────────────────────┐  │
        │  │   Exception Handlers                    │  │
        │  │   • RequestValidationError              │  │
        │  │   • HTTPException                       │  │
        │  └─────────────────────────────────────────┘  │
        └───────────┬────────────────────────────────────┘
                    │
                    │ SQLAlchemy ORM
                    │ (Connection Pooling)
                    │
        ┌───────────▼────────────────────────────────────┐
        │   PostgreSQL 14+ (Port 5432)                   │
        │  ┌─────────────────────────────────────────┐  │
        │  │ Tablas:                                 │  │
        │  │ ├─ empresas (Multi-tenant root)         │  │
        │  │ ├─ usuarios (Auth + roles)              │  │
        │  │ ├─ productos (Inventario)               │  │
        │  │ ├─ ventas (Transacciones)               │  │
        │  │ └─ detalles_venta (Line items)          │  │
        │  │                                         │  │
        │  │ Relaciones: 1:N (empresas → productos) │  │
        │  │            1:N (ventas → detalles)      │  │
        │  │            1:RESTRICT (evita borrar)    │  │
        │  └─────────────────────────────────────────┘  │
        │  ┌─────────────────────────────────────────┐  │
        │  │ Estrategia de Seguridad:                │  │
        │  │ ├─ UUIDs para IDs (no secuenciales)    │  │
        │  │ ├─ Foreign Keys con CASCADE/RESTRICT   │  │
        │  │ ├─ Indexes en búsquedas frecuentes      │  │
        │  │ └─ NUMERIC para dinero (no FLOAT)      │  │
        │  └─────────────────────────────────────────┘  │
        └────────────────────────────────────────────────┘
                    │
        ┌───────────▼────────────────────────────────────┐
        │   FILE SYSTEM (uploads/)                       │
        │   └─ /media/{uuid}_filename.jpg (Fotos)       │
        └────────────────────────────────────────────────┘
```

---

## 2. FLUJO DE AUTENTICACIÓN (JWT)

```
┌─────────────────┐
│  Usuario entra  │
│  email + pass   │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│ POST /token                              │
│ Body: {email, password}                  │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│ Buscar usuario por email en BD           │
│ db.query(Usuario).filter(                │
│   Usuario.email == email                 │
│ ).first()                                │
└────────┬─────────────────────────────────┘
         │
    ┌────┴─────────────────┬────────────────┐
    │ User not found       │ User found     │
    ▼                      ▼
┌────────────────┐  ┌──────────────────────┐
│ 401 Unauthorized│  │ Verify password hash │
│                │  │ bcrypt.verify()      │
└────────────────┘  └──────┬───────────────┘
                           │
                      ┌────┴──────────────┐
                      │ Pass matches      │
                      ▼
            ┌─────────────────────────────┐
            │ Create JWT Token:           │
            │ payload = {                 │
            │   "sub": usuario_id,        │
            │   "exp": expiration_time    │
            │ }                           │
            │ jwt.encode(payload,         │
            │   SECRET_KEY,               │
            │   algorithm="HS256")        │
            └──────────┬──────────────────┘
                       │
                       ▼
            ┌─────────────────────────────┐
            │ Return 200 OK               │
            │ {                           │
            │   "access_token": "...",    │
            │   "token_type": "bearer",   │
            │   "usuario": {...}          │
            │ }                           │
            └──────────┬──────────────────┘
                       │
                       ▼
            ┌─────────────────────────────┐
            │ Frontend guarda token en    │
            │ localStorage['access_token']│
            └─────────────────────────────┘
                       │
       ┌───────────────┴───────────────────┬──────────────────┐
       │                                   │                  │
       ▼ (Para cada request protegido)     ▼                  ▼
       │                            (Si expira)        (Si usuario hace logout)
       │
┌──────────────────────────────────────┐
│ GET /productos/{empresa_id}          │
│ Headers: {                           │
│   Authorization: Bearer {token}      │
│ }                                    │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ Dependency: get_current_user()       │
│ • Extrae token del header            │
│ • jwt.decode(token, SECRET_KEY)      │
│ • Obtiene usuario_id del payload     │
│ • Busca usuario en BD                │
│ • Retorna objeto Usuario             │
└────────┬─────────────────────────────┘
         │
    ┌────┴───────────────────────┐
    │ Token válido y usuario ok  │
    ▼
┌──────────────────────────────────────┐
│ current_user inyectado en ruta       │
│ Continuar lógica del endpoint        │
└──────────────────────────────────────┘
```

---

## 3. FLUJO DE VENTA (ACID Transaction)

```
CARRITO (Frontend - Memory)
┌─────────────────────────────────────────┐
│ [                                       │
│   {id: "p1", nombre: "Leche",           │
│    cantidad: 2, precio: 3500},          │
│   {id: "p2", nombre: "Pan",             │
│    cantidad: 1, precio: 2000}           │
│ ]                                       │
└─────────────────────────────────────────┘
         │
         ▼ User clicks "COBRAR"
         │
POST /ventas/{empresa_id}
Body: {
  "detalles": [
    {"producto_id": "p1", "cantidad": 2},
    {"producto_id": "p2", "cantidad": 1}
  ]
}
         │
         ▼ Backend START TRANSACTION
         │
╔════════════════════════════════════════╗
║ 1. Valida empresa_id del usuario       ║
║ if current_user.empresa_id != empresa_id
║   → 403 Forbidden                      ║
╚════════════════┬═══════════════════════╝
                 │
╔════════════════▼═══════════════════════╗
║ 2. Crea nueva VENTA (con total = 0)    ║
║ nueva_venta = Venta(empresa_id, ...)   ║
║ db.add(nueva_venta)                    ║
║ db.flush() → obtiene venta.id (pero    ║
║             aún no hace commit)        ║
╚════════════════┬═══════════════════════╝
                 │
╔════════════════▼═══════════════════════╗
║ 3. LOOP por cada item del carrito      ║
║ for item in venta.detalles:            ║
╚════════════════┬═══════════════════════╝
                 │
    ┌────────────┴────────────┐
    │                         │ Item 1: Leche, cantidad 2
    ▼                         │
╔═════════════════════════════════════════╗
║ 3a. Bloquea fila de PRODUCTO            ║
║ producto = db.query(Producto)           ║
║   .filter(Producto.id == "p1",          ║
║           Producto.empresa_id == ...)   ║
║   .with_for_update()  ← LOCK            ║
║   .first()                              ║
║                                         ║
║ ¿Por qué? → Si otro proceso intenta    ║
║ modificar este producto simultáneamente,║
║ espera hasta que terminemos.            ║
╚════════════════┬════════════════════════╝
                 │
╔════════════════▼════════════════════════╗
║ 3b. Valida stock disponible             ║
║ if producto.cantidad_actual < 2:       ║
║   raise ValueError("Stock insuficiente")║
║   → 400 Bad Request                     ║
║ else: Continuar                         ║
╚════════════════┬════════════════════════╝
                 │
╔════════════════▼════════════════════════╗
║ 3c. Descuenta stock del PRODUCTO        ║
║ producto.cantidad_actual -= 2           ║
║ # Ahora: cantidad_actual = (antes - 2)  ║
╚════════════════┬════════════════════════╝
                 │
╔════════════════▼════════════════════════╗
║ 3d. Calcula SUBTOTAL                    ║
║ subtotal = producto.precio_venta * 2    ║
║ subtotal = 3500 * 2 = 7000              ║
║ total_venta += 7000                     ║
╚════════════════┬════════════════════════╝
                 │
╔════════════════▼════════════════════════╗
║ 3e. Crea DETALLE_VENTA (snapshot)       ║
║ detalle = DetalleVenta(                 ║
║   venta_id=nueva_venta.id,              ║
║   producto_id="p1",                     ║
║   cantidad=2,                           ║
║   precio_unitario=3500,  ← Congelado    ║
║   subtotal=7000                         ║
║ )                                       ║
║ db.add(detalle)                         ║
╚════════════════┬════════════════════════╝
                 │
                 │ Item 2: Pan, cantidad 1
                 │ [Repite pasos 3a-3e]
                 │
                 ▼
╔════════════════════════════════════════╗
║ 4. Actualiza total de VENTA             ║
║ nueva_venta.total = total_venta         ║
║ = 7000 + 2000 = 9000                    ║
╚════════════════┬════════════════════════╝
                 │
    ┌────────────┴────────────┐
    │ ¿TODO OK?              │
    │ (Sin excepciones)      │
    ▼                         ▼
╔════════════════╗    ╔═════════════════╗
║ 5. COMMIT      ║    ║ 5. ROLLBACK     ║
║ db.commit()    ║    ║ db.rollback()   ║
║                ║    ║ return 400      ║
║ ✅ PERSISTE   ║    ║ ✅ Revierte todo║
║ Cambios OK    ║    ║ (Stock OK)      ║
║ Stock OK      ║    ║ (Venta NO)      ║
║ Venta OK      ║    ║                 ║
╚────────┬───────╝    ╚─────────────────╝
         │
         ▼
    ┌────────────────────────┐
    │ Return 200 OK          │
    │ {                      │
    │   "mensaje": "...",    │
    │   "total": 9000        │
    │ }                      │
    └────────────────────────┘
         │
         ▼ Frontend
    ┌────────────────────────┐
    │ • Vacía carrito        │
    │ • Recarga inventario   │
    │ • Muestra confirmación │
    └────────────────────────┘
```

---

## 4. MATRIZ DE VALIDACIONES (Prevención de errores)

```
┌────────────────────────────────────────────────────────────────────┐
│ FLUJO: POST /ventas/{empresa_id}                                   │
├─────────────┬─────────────────────┬──────────┬───────────────────┤
│ Paso        │ Validación          │ Si Falla │ Responsable       │
├─────────────┼─────────────────────┼──────────┼───────────────────┤
│ 1. Autenticación
│             │ JWT válido, no exp. │ 401      │ OAuth2 (HTTP)     │
│             │ Usuario existe en BD│ 401      │ get_current_user()│
│
│ 2. Autorización
│             │ empresa_id coincide │ 403      │ Ruta + Dependency │
│             │ empresa existe en BD│ 404      │ Query antes       │
│
│ 3. Validación de entrada (Pydantic)
│             │ detalles no vacío   │ 400      │ VentaCrear schema │
│             │ cantidad > 0        │ 400      │ Validator         │
│             │ tipos correctos      │ 400      │ BaseModel         │
│
│ 4. Integridad de datos (Pre-check)
│             │ producto existe     │ 404      │ Query antes       │
│             │ pertenece empresa   │ 400      │ Query con filter  │
│             │ stock >= cantidad   │ 400      │ with_for_update() │
│
│ 5. Operación crítica (ACID)
│             │ INSERT ventas OK    │ 500      │ DB Connection     │
│             │ INSERT detalles OK  │ 500      │ DB Constraint     │
│             │ UPDATE productos OK │ 500      │ Lock + FK         │
│
│ 6. Post-operación
│             │ COMMIT éxito        │ 500      │ Transaction       │
│             │ Rollback si error   │ 400/500  │ Exception handler │
└─────────────┴─────────────────────┴──────────┴───────────────────┘
```

---

## 5. MATRIZ DE PERMISOS (RBAC)

```
┌─────────────────────────────────────────────────────────────────┐
│ Endpoint                  │ Usuario Anónimo │ Tendero │ Admin   │
├───────────────────────────┼─────────────────┼─────────┼─────────┤
│ POST /registro            │ ✅ Sí          │ N/A     │ N/A     │
│ POST /token               │ ✅ Sí          │ N/A     │ N/A     │
│                           │                │         │         │
│ GET /me                   │ ❌ No (401)    │ ✅ Sí  │ ✅ Sí  │
│ GET /productos/{emp_id}   │ ❌ No (401)    │ ✅ Sí  │ ✅ Sí  │
│ POST /ventas/{emp_id}     │ ❌ No (401)    │ ✅ Sí  │ ✅ Sí  │
│ GET /ventas/{emp_id}      │ ❌ No (401)    │ ✅ Sí  │ ✅ Sí  │
│                           │                │         │         │
│ POST /productos/          │ ❌ No (401)    │ ❌ No  │ ✅ Sí  │
│                           │                │ (403)   │         │
│ PUT /productos/{id}       │ ❌ No (401)    │ ❌ No  │ ✅ Sí  │
│                           │                │ (403)   │         │
│ DELETE /productos/{id}    │ ❌ No (401)    │ ❌ No  │ ✅ Sí  │
│                           │                │ (403)   │         │
│ POST /productos/{id}/img  │ ❌ No (401)    │ ❌ No  │ ✅ Sí  │
│                           │                │ (403)   │         │
└───────────────────────────┴─────────────────┴─────────┴─────────┘

Leyenda:
✅ Permitido
❌ Rechazado (con código indicado)

IMPORTANTE: Todos los endpoints validaban empresa_id
→ Un tendero de Empresa A NO puede ver datos de Empresa B
```

---

## 6. MATRIZ DE MODELOS DE DATOS

```
┌──────────────────────────────────────────────────────────────────┐
│ Modelo      │ PK Type│ FK Referencias  │ Índices          │ Notas│
├─────────────┼────────┼─────────────────┼──────────────────┼──────┤
│ Empresa     │ UUID   │ -               │ -                │ Root │
│             │        │                 │                  │ entity
│
│ Usuario     │ UUID   │ → empresas.id   │ email (UNIQUE)   │ Auth │
│             │        │   (CASCADE)     │                  │
│
│ Producto    │ UUID   │ → empresas.id   │ codigo_barras    │ Inv. │
│             │        │   (CASCADE)     │   (UNIQUE)       │
│
│ Venta       │ UUID   │ → empresas.id   │ fecha_venta      │ Venta│
│             │        │   (CASCADE)     │ empresa_id       │ Doc.
│
│ DetalleVenta│ UUID   │ → ventas.id     │ venta_id,        │ Line │
│             │        │   (CASCADE)     │ producto_id      │ Item │
│             │        │ → productos.id  │                  │
│             │        │   (RESTRICT)    │                  │
└──────────────┴────────┴─────────────────┴──────────────────┴──────┘

Relaciones Clave:
┌─────────────────────────────────────────────────────────────────┐
│ Empresa (1) ──────── (N) Producto                              │
│ Empresa (1) ──────── (N) Usuario                               │
│ Empresa (1) ──────── (N) Venta                                 │
│ Venta (1) ────────── (N) DetalleVenta                          │
│ Producto (1) ─────── (N) DetalleVenta                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. TABLA DE ERRORES COMUNES

```
┌──────┬───────────────────────┬────────────────────┬──────────────────┐
│Code  │ Descripción           │ Causa Probable     │ Solución         │
├──────┼───────────────────────┼────────────────────┼──────────────────┤
│ 400  │ Bad Request           │ Datos inválidos    │ Revisar request  │
│      │ • Stock insuficiente  │ • Carrito vacío    │ • Pre-validar    │
│      │ • Código duplicado    │ • Cantidad <= 0    │ • Alertar user   │
│      │ • Producto no existe  │ • Falta campo      │ • Formato JSON   │
│      │                       │ • Tipo incorrecto  │                  │
│
│ 401  │ Unauthorized          │ No autenticado     │ Login             │
│      │ • Token inválido      │ • Token expirado   │ • Refresh token   │
│      │ • Token faltante      │ • Usuario borrado  │ • Reautentica     │
│      │ • JWT tampering       │ • Firma inválida   │ • Logout/login    │
│
│ 403  │ Forbidden             │ No autorizado      │ Revisar rol       │
│      │ • Otra empresa        │ • Rol insuficiente │ • Cambiar usuario │
│      │ • Solo admin          │ • Permisos         │ • Contactar admin │
│      │                       │   insuficientes    │                  │
│
│ 404  │ Not Found             │ Recurso no existe  │ Verificar ID      │
│      │ • Empresa no existe   │ • Ya borrado       │ • Crear primero   │
│      │ • Producto no existe  │ • ID incorrecto    │ • Usar ID válido  │
│      │ • Usuario no existe   │ • Typo             │                  │
│
│ 409  │ Conflict              │ Recurso duplicado  │ Usar existente    │
│      │ • Email ya existe     │ • Código_barras    │ • No duplicar     │
│      │ • Código duplicado    │   duplicado        │ • Verificar antes │
│
│ 422  │ Unprocessable         │ Validación fallida │ Revisar formato   │
│ Entity                        │ Pydantic error     │ • Schema invalid  │
│
│ 500  │ Internal Server Error │ Error en backend   │ Contactar soporte │
│      │ • DB connection       │ • Transacción fall │ • Ver logs        │
│      │ • Rollback fallido    │ • Bug en código    │ • Reintentar      │
│      │ • Excepción no handle │                    │                  │
└──────┴───────────────────────┴────────────────────┴──────────────────┘
```

---

## 8. CHECKLIST DE SEGURIDAD (Pre-Deploy)

```
┌─ BACKEND ─────────────────────────────────────────┐
│                                                   │
│ ☐ SECRET_KEY ≠ "tu-clave-super-segura..."       │
│   • Usar env var verdaderamente random           │
│   • Min 32 caracteres                            │
│                                                   │
│ ☐ CORS configurado solo para dominio real        │
│   • NO allow_origins=["*"]                       │
│   • Específico: ["https://tiendapp.com.co"]     │
│                                                   │
│ ☐ HTTPS obligatorio en producción                │
│   • redirect HTTP → HTTPS                        │
│   • HSTS headers                                 │
│                                                   │
│ ☐ Rate limiting en /token y /registro            │
│   • Max 5 intentos / 15 min                      │
│   • Prevenir brute force                        │
│                                                   │
│ ☐ SQL injection previsto                         │
│   • ✅ SQLAlchemy + Pydantic (parameterized)    │
│   • ✅ NO f-strings en queries                   │
│                                                   │
│ ☐ Contraseñas hasheadas                          │
│   • ✅ bcrypt (passlib)                          │
│   • ✅ NO almacenar en texto plano               │
│                                                   │
│ ☐ JWT tokens con expiración                      │
│   • ☐ Aumentar a 15 min (actual: 30)            │
│   • ☐ Implementar refresh tokens                 │
│                                                   │
│ ☐ Validación input en 2 capas                    │
│   • ✅ Pydantic (backend)                        │
│   • ☐ Frontend (UX)                              │
│                                                   │
│ ☐ Logging sin datos sensibles                    │
│   • ☐ No log passwords                           │
│   • ☐ No log tokens completos                    │
│   • ☐ Mascarar emails en logs                    │
│                                                   │
│ ☐ Database credentials en env vars               │
│   • NO en código fuente                          │
│   • .env no commitea a Git                       │
│                                                   │
│ ☐ CORS en uploads                                │
│   • ☐ Validar tipo de archivo                    │
│   • ☐ Antivirus scan                             │
│   • ☐ Limite de tamaño                           │
│                                                   │
└───────────────────────────────────────────────────┘

┌─ FRONTEND ────────────────────────────────────────┐
│                                                   │
│ ☐ Token guardado seguro                          │
│   • ✅ localStorage (HTTPS solo)                 │
│   • ⚠️ NO en cookies (sin HttpOnly)              │
│                                                   │
│ ☐ Sanitizar inputs                               │
│   • Prevenir XSS                                 │
│   • React lo hace automático                     │
│                                                   │
│ ☐ Validar en 2 capas                             │
│   • Frontend (UX)                                │
│   • Backend (Seguridad)                          │
│                                                   │
│ ☐ Error messages genéricos                       │
│   • NO "Email no registrado"                     │
│   • Usar "Credenciales inválidas"                │
│                                                   │
│ ☐ Content Security Policy (CSP)                  │
│   • Header: Content-Security-Policy              │
│                                                   │
│ ☐ Protección CSRF                                │
│   • SameSite cookies                             │
│                                                   │
└───────────────────────────────────────────────────┘

┌─ DEVOPS ──────────────────────────────────────────┐
│                                                   │
│ ☐ Database password ≠ default                    │
│   • Cambiar de "admin123"                        │
│   • Min 16 caracteres                            │
│                                                   │
│ ☐ Backups automáticos                            │
│   • Daily, retención 30 días                     │
│                                                   │
│ ☐ Monitoring + alertas                           │
│   • CPU > 80%                                    │
│   • Disk > 90%                                   │
│   • Response time > 5s                           │
│                                                   │
│ ☐ Logs centralizados                             │
│   • ELK Stack o CloudWatch                       │
│                                                   │
│ ☐ Firewall configurado                           │
│   • Port 5432 (DB) solo desde backend            │
│   • Port 8000 (API) solo desde frontend          │
│                                                   │
└───────────────────────────────────────────────────┘
```

---

## 9. MATRIZ DE COMPATIBILIDAD DE VERSIONES

```
┌─────────────────────────────────────────────────────────┐
│ Componente      │ Versión │ EOL      │ Status    │ Acción│
├─────────────────┼─────────┼──────────┼───────────┼───────┤
│ Python          │ 3.10    │ Oct 2026 │ ⚠️ Cercano│ Upgrade
│                 │ 3.11    │ Oct 2027 │ ✅ OK     │ OK
│                 │ 3.12    │ Oct 2028 │ ✅ OK     │ OK
│
│ FastAPI         │ 0.104.1 │ N/A      │ ✅ OK     │ OK
│                 │ 1.0+    │ N/A      │ ✅ OK     │ OK
│
│ SQLAlchemy      │ 2.0     │ N/A      │ ✅ OK     │ OK
│
│ PostgreSQL      │ 14      │ Nov 2026 │ ⚠️ Cercano│ Upgrade
│                 │ 15      │ Nov 2027 │ ✅ OK     │ OK
│                 │ 16      │ Nov 2028 │ ✅ OK     │ OK
│
│ React           │ 19.2.5  │ N/A      │ ✅ OK     │ OK
│
│ Vite            │ 8.0.10  │ N/A      │ ✅ OK     │ OK
│                 │ 5.0+    │ N/A      │ ✅ OK     │ OK (EOL 24m)
│
│ Tailwind CSS    │ 4.2.4   │ N/A      │ ✅ OK     │ OK
│
│ Node.js         │ 18.x    │ Apr 2025 │ ⚠️ Cercano│ Upgrade
│                 │ 20.x    │ Apr 2026 │ ✅ OK     │ OK
│                 │ 22.x    │ Apr 2027 │ ✅ OK     │ OK
└─────────────────┴─────────┴──────────┴───────────┴───────┘

Recomendaciones de Upgrade:
1. Python 3.10 → 3.12 (Antes de Oct 2026)
2. PostgreSQL 14 → 15 (Antes de Nov 2026)
3. Node.js 18 → 20 (Antes de Apr 2025)
```

---

**Fin de Diagramas Técnicos**
