# 🔍 INFORME TÉCNICO - DEPURACIÓN WIZARD DE REGISTRO (2 PASOS)
**Sistema:** Tiendapp - POS SaaS  
**Stack:** React (Vite) + FastAPI + PostgreSQL  
**Estado:** Paso 1 ✅ Exitoso | Paso 2 ❌ Falla "Failed to fetch"  
**Fecha de Análisis:** 2026-05-06

---

## 📋 RESUMEN EJECUTIVO

El flujo de registro de dos pasos implementa correctamente el Paso 1 (creación de empresa), pero el Paso 2 (creación de administrador) falla silenciosamente con "Failed to fetch". El análisis revela:

| Componente | Estado | Hallazgo |
|-----------|--------|---------|
| **Flujo Frontend** | ✅ Correcto | El `empresa_id` se captura y envía correctamente |
| **Esquemas Backend** | ✅ Alineados | Pydantic espera exactamente lo que envía el frontend |
| **Manejo de Errores** | ⚠️ **PROBLEMA** | Validación de Pydantic genera errores opacos |
| **Integración Paso 1→2** | ⚠️ **FALLA** | **NO hay transacción atómica** (rollback manual no existe) |

---

## 🔄 PARTE 1: FLUJO DE DATOS FRONTEND

### 1.1 Component Registro.jsx - Estado y Captura del empresa_id

**Archivo:** `frontend/src/pages/Registro.jsx`

#### ✅ Captura Correcta del empresa_id (Líneas 20-33)

```jsx
const crearEmpresa = async (e) => {
  e.preventDefault()
  setCargando(true)
  setError(null)
  try {
    const data = await authService.crearEmpresa(empresa)
    setEmpresaId(data.empresa.id)  // ✅ CORRECTO: Extrae UUID de la respuesta
    setPaso(2)
  } catch (e) {
    setError(e.message)
  } finally {
    setCargando(false)
  }
}
```

**Análisis:**
- El Paso 1 extrae `data.empresa.id` (UUID válido) ✅
- Se almacena en el estado `empresaId` (línea 12)
- Se avanza al Paso 2

#### ⚠️ Envío en Paso 2 (Líneas 35-47)

```jsx
const registrarUsuario = async (e) => {
  e.preventDefault()
  setCargando(true)
  setError(null)
  try {
    await registrar({
      ...form,
      empresa_id: empresaId,  // ✅ Incluye empresa_id
      rol: 'admin'             // ✅ Incluye rol
    })
    navigate('/inventario', { replace: true })
  } catch (e) {
    setError(e.message)
  } finally {
    setCargando(false)
  }
}
```

**Payload enviado al backend:**
```json
{
  "email": "admin@empresa.com",
  "password": "miContraseña123",
  "empresa_id": "550e8400-e29b-41d4-a716-446655440000",  // UUID válido
  "rol": "admin"
}
```

✅ **Conclusión Parte 1:** El frontend envía datos correctos.

---

## 📊 PARTE 2: ESQUEMAS Y VALIDACIÓN BACKEND

### 2.1 Schema de Creación de Usuario

**Archivo:** `app/schemas/usuario.py` (Líneas 8-19)

```python
class UsuarioCrear(BaseModel):
    email: EmailStr
    password: str
    empresa_id: UUID          # ✅ Espera UUID
    rol: RolUsuario = RolUsuario.TENDERO

    @field_validator("password")
    @classmethod
    def password_minimo(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v
```

**Campos que Pydantic valida:**
1. ✅ `email` → Validación `EmailStr` (existe, válido)
2. ✅ `password` → Mínimo 8 caracteres
3. ✅ `empresa_id` → UUID válido
4. ✅ `rol` → Enum `RolUsuario` (default: `TENDERO`, pero frontend envía `admin`)

### 2.2 Alineación Frontend ↔ Backend

| Campo | Frontend | Backend (Schema) | ¿Coinciden? |
|-------|----------|-----------------|-----------|
| `email` | string | `EmailStr` | ✅ Sí |
| `password` | string | `str` | ✅ Sí |
| `empresa_id` | UUID string | `UUID` | ✅ **Sí (Pydantic convierte automáticamente)** |
| `rol` | `"admin"` | `RolUsuario` enum | ⚠️ **Posible problema** |

### 2.3 ⚠️ PROBLEMA DETECTADO: Validación del `rol`

**En `app/models.py` (Línea 18-20):**
```python
class RolUsuario(str, enum.Enum):
    ADMIN = "admin"
    TENDERO = "tendero"
```

**¿Qué envía el frontend?** `"admin"` (string) ✅  
**¿Qué espera Pydantic?** Un valor del enum `RolUsuario` ✅

**En teoría:** Funciona porque `RolUsuario(str, enum.Enum)` hace que Pydantic acepte strings.

---

## 🚨 PARTE 3: MANEJO DE ERRORES - RAÍZ DEL PROBLEMA

### 3.1 Ruta de Registro en Backend

**Archivo:** `app/routers/auth.py` (Líneas 13-17)

```python
@router.post("/registro", response_model=TokenRespuesta, status_code=status.HTTP_201_CREATED)
def registro(data: UsuarioCrear, db: Session = Depends(get_db)):
    usuario = auth_service.registrar_usuario(data, db)
    token = auth_service.crear_token_acceso({"sub": str(usuario.id)})
    return {"access_token": token, "token_type": "bearer", "usuario": usuario}
```

### 3.2 Lógica de Validación en `auth_service.registrar_usuario()`

**Archivo:** `app/services/auth_service.py` (Líneas 53-83)

```python
def registrar_usuario(data: UsuarioCrear, db: Session) -> models.Usuario:
    # Pre-check 1: Email duplicado
    if db.query(models.Usuario).filter(
        models.Usuario.email == data.email
    ).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este email ya está registrado",
        )

    # Pre-check 2: Empresa existe y está activa
    empresa = db.query(models.Empresa).filter(
        models.Empresa.id == data.empresa_id,      # ⚠️ PUNTO CRÍTICO
        models.Empresa.is_active.is_(True),
    ).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada",
        )

    usuario = models.Usuario(
        email=data.email,
        hashed_password=hash_password(data.password),
        empresa_id=data.empresa_id,
        rol=data.rol,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
```

### 3.3 ⚠️ CAUSAS POTENCIALES DEL "Failed to fetch"

#### Opción A: Validación de Pydantic falla (422 Unprocessable Entity)
Si `empresa_id` no es un UUID válido, Pydantic rechaza la solicitud:

```python
# El frontend envía: "empresa_id": "abc123" (inválido)
# Pydantic genera error 422:
# {
#   "detail": [
#     {
#       "type": "uuid_parsing",
#       "loc": ["body", "empresa_id"],
#       "msg": "Invalid UUID version"
#     }
#   ]
# }
```

**¿Es este el caso?** Probablemente NO, porque:
- `data.empresa.id` viene de la BD (UUID válido)
- Pydantic maneja correctamente strings UUID

#### Opción B: La empresa NO existe en la BD
Si el `empresa_id` es válido pero la empresa fue:
1. No guardada correctamente en el Paso 1
2. Fue eliminada entre los pasos (raro)
3. Tiene `is_active = False`

El backend retorna:
```json
{
  "detail": "Empresa no encontrada"
}
```

**Estado HTTP:** 404 (NOT FOUND)

#### Opción C: Error de validación de Pydantic en `rol`
Si el frontend envía `"rol": "admin"` pero Pydantic no reconoce el enum:

```python
# Pydantic error 422:
# "rol": "Input should be 'admin' or 'tendero' [type=enum, input_value='admin']"
```

**¿Es este el caso?** Posible, porque:
- El enum está bien definido
- Pero hay conversión implícita string → enum que puede fallar

---

## 🔍 ESCENARIO MÁS PROBABLE: La Empresa No Existe

### Causa Raíz

**En `frontend/src/pages/Registro.jsx` línea 26:**
```jsx
const data = await authService.crearEmpresa(empresa)
setEmpresaId(data.empresa.id)  // Aquí se extrae el ID
```

**En `frontend/src/services/authService.js` líneas 46-57:**
```javascript
async crearEmpresa(payload) {
  const res = await fetch(`${BASE}/empresas/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Error creando empresa')
  }
  return res.json()  // ← Retorna { "mensaje": "...", "empresa": {...} }
}
```

**En `app/routers/empresas.py` líneas 13-19:**
```python
@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_empresa(data: EmpresaCrear, db: Session = Depends(get_db)):
    empresa = empresa_service.crear_empresa(data, db)
    return {
        "mensaje": "Empresa creada exitosamente",
        "empresa": EmpresaRespuesta.model_validate(empresa),
    }
```

✅ **La estructura es correcta y el UUID se extrae bien.**

---

## 🐛 PROBLEMA CRÍTICO: Falta de Transacción Atómica

### 4.1 El Flujo Actual (NO Transaccional)

```
┌─────────────────────────────────────────┐
│ Frontend: Paso 1 - Crear Empresa        │
└─────────────────────────────────────────┘
          │
          ▼ (commit aquí)
┌──────────────────────────┐
│ BD: INSERT INTO empresas │ ✅ Empresa guardada
└──────────────────────────┘
          │
          ▼ empresaId almacenado en estado React
┌─────────────────────────────────────────┐
│ Frontend: Paso 2 - Crear Usuario        │
└─────────────────────────────────────────┘
          │
          ▼ (POST /registro con empresa_id)
┌──────────────────────────────────────────┐
│ Backend: Validar empresa existe          │ ← Si falla aquí:
│ Backend: INSERT INTO usuarios            │   - Empresa está en BD
└──────────────────────────────────────────┘   - Usuario NO se crea
          │                                      - Limpieza manual: REQUIERE UI
          ▼
    ✅ O ❌ Fin
```

### 4.2 Problemas

**Problema 1: Sin Rollback Automático**
- Si Paso 2 falla, la empresa sigue en la BD huérfana
- No hay endpoint para eliminar la empresa (cleanup)

**Problema 2: Estados Inconsistentes Posibles**
1. Empresa creada pero usuario falla → Datos zombies
2. Usuario falla por validación en frontend no detectada → No hay intento
3. BD puede haber rechazado empresa por restricción no validada en frontend

**Problema 3: Violaciones de Constraints**
```sql
-- Si el usuario intenta registrarse 2 veces con el mismo email:
UNIQUE constraint `usuarios.email` violado
→ Backend retorna 409 CONFLICT
→ Frontend recibe error (pero empresa ya existe)
```

---

## 📋 PARTE 4: VALIDACIÓN DE PYDANTIC - ANÁLISIS PROFUNDO

### Potencial Bug con Rol Enum

**Si `rol` no se valida bien:**

```python
# En app/schemas/usuario.py
class UsuarioCrear(BaseModel):
    rol: RolUsuario = RolUsuario.TENDERO  # Pydantic espera un miembro del enum
```

**Si el frontend envía un string directo:**
```json
{
  "email": "admin@empresa.com",
  "password": "Pass1234",
  "empresa_id": "550e8400-e29b-41d4-a716-446655440000",
  "rol": "admin"  // ← String, no enum
}
```

**Pydantic debería:**
- ✅ Si `RolUsuario` hereda de `str` y `enum.Enum` → Acepta "admin"
- ❌ Si falla la coerción → Error 422

**Verificación en el código:**
```python
class RolUsuario(str, enum.Enum):  # ← Hereda de str, por lo que Pydantic lo coerciona
    ADMIN = "admin"
    TENDERO = "tendero"
```

**Conclusión:** Este no es el problema.

---

## 🎯 PARTE 5: PLAN DE MEJORA DETALLADO

### 5.1 Mejora Inmediata: Agregar Logging y Validación en Frontend

**Objetivo:** Capturar errores silenciosos en Paso 2

**Cambio en `frontend/src/pages/Registro.jsx`:**

```jsx
const registrarUsuario = async (e) => {
  e.preventDefault()
  setCargando(true)
  setError(null)
  
  // ✅ Validación: Verificar que empresaId existe
  if (!empresaId) {
    setError('Error interno: empresa_id no disponible')
    setCargando(false)
    return
  }
  
  // ✅ Loguear payload exacto para debugging
  const payload = {
    email: form.email,
    password: form.password,
    empresa_id: empresaId,
    rol: 'admin'
  }
  console.debug('[Registro Paso 2] Payload:', payload)
  
  try {
    await registrar(payload)
    navigate('/inventario', { replace: true })
  } catch (e) {
    // ✅ Loguear error completo
    console.error('[Registro Paso 2] Error:', e)
    setError(e.message)
  } finally {
    setCargando(false)
  }
}
```

---

### 5.2 Mejora Crítica: Transacción Atómica en Backend

**Objetivo:** Si falla Paso 2, rollback automático de Paso 1

#### Opción A: Crear Usuario ANTES de Empresa (Recomendado)

**Cambiar el flujo a:**
1. Crear Usuario (con validaciones)
2. Crear Empresa asociada
3. Si uno falla, ambos fallan

**Nuevo esquema `UsuarioCrearConEmpresa`:**

```python
# app/schemas/usuario.py
class UsuarioCrearConEmpresa(BaseModel):
    """Schema para registro atómico de empresa + usuario"""
    # Datos empresa
    nombre_comercial: str
    nit_o_cedula: str
    
    # Datos usuario
    email: EmailStr
    password: str
    rol: RolUsuario = RolUsuario.ADMIN
```

**Nuevo endpoint `/registro-completo`:**

```python
# app/routers/auth.py
@router.post("/registro-completo", 
             response_model=TokenRespuesta, 
             status_code=status.HTTP_201_CREATED)
def registro_completo(data: UsuarioCrearConEmpresa, db: Session = Depends(get_db)):
    """
    Registra empresa + usuario en una transacción atómica.
    Si cualquiera falla, ambos fallan y se hace rollback.
    """
    try:
        # Validación de email duplicado
        if db.query(models.Usuario).filter(
            models.Usuario.email == data.email
        ).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este email ya está registrado",
            )
        
        # Validación de NIT duplicado
        if db.query(models.Empresa).filter(
            models.Empresa.nit_o_cedula == data.nit_o_cedula
        ).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una empresa con NIT/Cédula '{data.nit_o_cedula}'",
            )
        
        # Crear empresa
        empresa = models.Empresa(
            nombre_comercial=data.nombre_comercial.strip(),
            nit_o_cedula=data.nit_o_cedula.strip(),
        )
        db.add(empresa)
        db.flush()  # Genera el ID sin commit
        
        # Crear usuario con la empresa
        usuario = models.Usuario(
            email=data.email,
            hashed_password=hash_password(data.password),
            empresa_id=empresa.id,
            rol=data.rol,
        )
        db.add(usuario)
        db.commit()  # Commit atómico de ambos
        db.refresh(usuario)
        
        token = auth_service.crear_token_acceso({"sub": str(usuario.id)})
        return {"access_token": token, "token_type": "bearer", "usuario": usuario}
    
    except HTTPException:
        raise  # Re-raise HTTPExceptions
    except Exception as e:
        db.rollback()  # Rollback de cualquier error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en registro: {str(e)}"
        )
```

#### Opción B: Usar Decorador `@transactional` (Alternativa)

```python
# Si usas SQLAlchemy con sessionmaker + context vars
from functools import wraps

def transactional(f):
    def wrapper(*args, db: Session, **kwargs):
        try:
            result = f(*args, db=db, **kwargs)
            db.commit()
            return result
        except Exception:
            db.rollback()
            raise
    return wrapper

@router.post("/registro")
@transactional
def registro(data: UsuarioCrear, db: Session = Depends(get_db)):
    # ... lógica aquí ...
```

---

### 5.3 Mejora en Frontend: Cambiar a Endpoint Atómico

**En `frontend/src/pages/Registro.jsx`:**

```jsx
export default function Registro() {
  const { registrar } = useAuth()
  const navigate = useNavigate()
  const [paso, setPaso] = useState(1)
  const [empresa, setEmpresa] = useState({ nombre_comercial: '', nit_o_cedula: '' })
  const [admin, setAdmin] = useState({ email: '', password: '' })
  const [error, setError] = useState(null)
  const [cargando, setCargando] = useState(false)

  const cambiarEmpresa = (e) => setEmpresa(prev => ({ ...prev, [e.target.name]: e.target.value }))
  const cambiarAdmin = (e) => setAdmin(prev => ({ ...prev, [e.target.name]: e.target.value }))

  const handleRegistro = async (e) => {
    e.preventDefault()
    setCargando(true)
    setError(null)
    
    try {
      // ✅ Ahora es TODO EN UNO (transacción atómica)
      await registrar({
        ...empresa,     // nombre_comercial, nit_o_cedula
        ...admin,       // email, password
        rol: 'admin'
      })
      navigate('/inventario', { replace: true })
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }

  // Render similar pero sin estado de empresaId
  // ...
}
```

**En `frontend/src/services/authService.js`:**

```javascript
async registro(payload) {
  const res = await fetch(`${BASE}/registro-completo`, {  // ← Nuevo endpoint
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Error en el registro')
  }
  const data = await res.json()
  this.setToken(data.access_token)
  return data
}
```

---

### 5.4 Mejora en Manejo de Errores: Respuestas Consistentes

**Objetivo:** El cliente reciba siempre `{ "detail": "mensaje" }`

**En `app/main.py` (ya está bien, pero agregar):**

```python
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all para errores no esperados"""
    import traceback
    traceback.print_exc()  # Log en backend
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor"},
    )
```

---

### 5.5 Testing: Casos de Prueba para Validar

**Test 1: Email Duplicado en Paso 2**
```python
def test_registro_email_duplicado(db):
    """Si usuario intenta registrarse con email existente"""
    usuario_existente = Usuario(
        email="admin@empresa.com",
        hashed_password=hash_password("Pass1234"),
        empresa_id=...,
        rol=RolUsuario.ADMIN
    )
    db.add(usuario_existente)
    db.commit()
    
    # Intento de registro con el mismo email
    response = client.post("/registro-completo", json={
        "nombre_comercial": "Otra Empresa",
        "nit_o_cedula": "999000000-1",
        "email": "admin@empresa.com",  # ← Duplicado
        "password": "Pass1234",
        "rol": "admin"
    })
    
    assert response.status_code == 409  # Conflict
    assert "ya está registrado" in response.json()["detail"]
```

**Test 2: Empresa Duplicada en Paso 2**
```python
def test_registro_nit_duplicado(db):
    """Si usuario intenta registrar empresa con NIT duplicado"""
    empresa_existente = Empresa(
        nombre_comercial="Empresa 1",
        nit_o_cedula="900123456-1"
    )
    db.add(empresa_existente)
    db.commit()
    
    response = client.post("/registro-completo", json={
        "nombre_comercial": "Otra Empresa",
        "nit_o_cedula": "900123456-1",  # ← Duplicado
        "email": "admin@otra.com",
        "password": "Pass1234",
        "rol": "admin"
    })
    
    assert response.status_code == 409
    assert "ya existe una empresa" in response.json()["detail"].lower()
```

**Test 3: Transacción Atómica**
```python
def test_registro_atomico_rollback(db):
    """Si Paso 2 falla, Paso 1 también debe fallar"""
    # Simular existencia de email previo
    usuario_existente = Usuario(
        email="admin@empresa.com",
        hashed_password=hash_password("Pass1234"),
        empresa_id=...,
        rol=RolUsuario.ADMIN
    )
    db.add(usuario_existente)
    db.commit()
    
    payload = {
        "nombre_comercial": "Nueva Empresa",
        "nit_o_cedula": "888000000-1",
        "email": "admin@empresa.com",  # ← Duplicado, falla
        "password": "Pass1234",
        "rol": "admin"
    }
    
    response = client.post("/registro-completo", json=payload)
    assert response.status_code != 201
    
    # Verificar que la empresa NO se creó (rollback funcionó)
    empresas = db.query(Empresa).filter(
        Empresa.nombre_comercial == "Nueva Empresa"
    ).all()
    assert len(empresas) == 0  # ✅ Rollback confirmado
```

---

## 📌 CONCLUSIONES Y RECOMENDACIONES

| Hallazgo | Severidad | Acción |
|----------|-----------|--------|
| Frontend captura `empresa_id` correctamente | ✅ OK | Mantener |
| Schemas alineados entre frontend y backend | ✅ OK | Mantener |
| **Sin transacción atómica** | 🔴 CRÍTICO | Implementar `/registro-completo` |
| **Falta validación en frontend** | 🟡 ALTO | Agregar checks de `empresaId` antes de Paso 2 |
| **Errores silenciosos "Failed to fetch"** | 🟡 ALTO | Agregar logging y error handling robusto |
| **Sin cleanup si falla Paso 2** | 🟡 MEDIO | Implementar transacción atómica |

---

## 🚀 HOJA DE RUTA DE IMPLEMENTACIÓN

### Fase 1: Corto Plazo (Diagnóstico)
1. Agregar `console.debug()` en frontend para ver payload exacto
2. Revisar logs del backend en `stderr`
3. Verificar que `empresa_id` no sea `null` en Paso 2

### Fase 2: Mediano Plazo (Fixes Rápidos)
1. Implementar validación defensiva en frontend
2. Mejorar manejo de errores en `authService.js`
3. Agregar endpoint `/registro-completo`

### Fase 3: Largo Plazo (Arquitectura)
1. Implementar transacciones atómicas en todos los endpoints de creación
2. Agregar suite de tests para validar rollback
3. Implementar `RequestContext` para mejor manejo de errores globales

---

## 📎 ANEXO: Fragmentos de Código Clave

### Fragmento A: Payload Esperado (Paso 2 Actual)
```json
POST /registro
{
  "email": "admin@empresa.com",
  "password": "MiPassword123",
  "empresa_id": "550e8400-e29b-41d4-a716-446655440000",
  "rol": "admin"
}
```

### Fragmento B: Respuesta Exitosa (Esperada)
```json
HTTP 201 Created
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "usuario": {
    "id": "660e8401-e29b-41d4-a716-446655440001",
    "email": "admin@empresa.com",
    "empresa_id": "550e8400-e29b-41d4-a716-446655440000",
    "rol": "admin",
    "created_at": "2026-05-06T20:55:54.611Z",
    "is_active": true
  }
}
```

### Fragmento C: Error Probable (Lo que probablemente está pasando)
```json
HTTP 404 Not Found
{
  "detail": "Empresa no encontrada"
}
```

---

**Análisis completado por:** Senior QA Automation Engineer  
**Estado:** Listo para implementación  
**Próximo paso:** Ejecutar Fase 1 (Diagnóstico)
