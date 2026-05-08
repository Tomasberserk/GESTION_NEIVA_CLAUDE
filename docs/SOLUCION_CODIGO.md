# 💾 SOLUCIÓN - CÓDIGO CORREGIDO PARA IMPLEMENTAR

Este documento contiene los cambios necesarios para **hacer el flujo de registro atómico y robusto**.

---

## 🎯 CAMBIO 1: Nuevo Schema para Registro Completo

**Archivo:** `app/schemas/usuario.py`

**Agregar al final del archivo:**

```python
class UsuarioCrearConEmpresa(BaseModel):
    """Schema para registro atómico de empresa + usuario en un solo endpoint.
    
    Garantiza transacción ACID:
    - Si la empresa falla, el usuario no se crea
    - Si el usuario falla, la empresa no se crea (rollback)
    """
    # Datos de la empresa
    nombre_comercial: str
    nit_o_cedula: str
    
    # Datos del usuario administrador
    email: EmailStr
    password: str
    rol: RolUsuario = RolUsuario.ADMIN
    
    @field_validator("nombre_comercial")
    @classmethod
    def nombre_empresa_valido(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre comercial no puede estar vacío")
        if len(v) > 150:
            raise ValueError("El nombre comercial no puede exceder 150 caracteres")
        return v
    
    @field_validator("nit_o_cedula")
    @classmethod
    def nit_valido(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El NIT/Cédula no puede estar vacío")
        if len(v) > 50:
            raise ValueError("El NIT/Cédula no puede exceder 50 caracteres")
        return v
    
    @field_validator("password")
    @classmethod
    def password_minimo(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v
```

---

## 🎯 CAMBIO 2: Nuevo Service para Registro Atómico

**Archivo:** `app/services/auth_service.py`

**Agregar esta función NUEVA al final:**

```python
def registrar_usuario_con_empresa(
    nombre_comercial: str,
    nit_o_cedula: str,
    email: str,
    password: str,
    rol: models.RolUsuario,
    db: Session,
) -> dict:
    """
    Registra empresa + usuario en UNA transacción atómica.
    
    Garantías:
    - Si la empresa falla → Usuario no se crea
    - Si el usuario falla → Empresa no se crea (rollback)
    - Ambos se crean o ninguno se crea
    
    Args:
        nombre_comercial: Nombre de la tienda
        nit_o_cedula: NIT o Cédula único
        email: Email único para el usuario administrador
        password: Contraseña (mínimo 8 caracteres)
        rol: Rol del usuario (normalmente ADMIN en el primer registro)
        db: Sesión de base de datos
    
    Returns:
        dict con access_token, token_type y usuario
    
    Raises:
        HTTPException: Si hay conflictos (email/NIT duplicado) o datos inválidos
    """
    try:
        # Pre-check 1: Email duplicado (previene HTTP 409)
        if db.query(models.Usuario).filter(
            models.Usuario.email == email
        ).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este email ya está registrado",
            )
        
        # Pre-check 2: NIT/Cédula duplicado (previene HTTP 409)
        if db.query(models.Empresa).filter(
            models.Empresa.nit_o_cedula == nit_o_cedula
        ).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una empresa con NIT/Cédula '{nit_o_cedula}'",
            )
        
        # PASO 1: Crear empresa
        empresa = models.Empresa(
            nombre_comercial=nombre_comercial.strip(),
            nit_o_cedula=nit_o_cedula.strip(),
        )
        db.add(empresa)
        db.flush()  # Genera el ID sin hacer commit (permite rollback si falla Paso 2)
        
        # PASO 2: Crear usuario con la empresa (si esto falla, empresa se descarta)
        usuario = models.Usuario(
            email=email,
            hashed_password=hash_password(password),
            empresa_id=empresa.id,  # ← FK a la empresa creada
            rol=rol,
        )
        db.add(usuario)
        
        # COMMIT ATÓMICO: Ambos se guardan o ninguno
        db.commit()
        db.refresh(usuario)
        
        # Crear token JWT
        token = crear_token_acceso({"sub": str(usuario.id)})
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "usuario": usuario,
        }
    
    except HTTPException:
        # Re-raise HTTPExceptions (validaciones de negocio)
        db.rollback()
        raise
    
    except Exception as e:
        # Catch any other database error and rollback
        db.rollback()
        import traceback
        traceback.print_exc()  # Log para debugging
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el registro: {str(e)}",
        )
```

---

## 🎯 CAMBIO 3: Nuevo Endpoint en Backend

**Archivo:** `app/routers/auth.py`

**Importar el nuevo schema:**

```python
from app.schemas.usuario import (
    LoginForm, 
    TokenRespuesta, 
    UsuarioCrear, 
    UsuarioCrearConEmpresa,  # ← NUEVO
    UsuarioRespuesta
)
```

**Agregar este endpoint NUEVO después del endpoint `/registro`:**

```python
@router.post("/registro-completo", response_model=TokenRespuesta, status_code=status.HTTP_201_CREATED)
def registro_completo(data: UsuarioCrearConEmpresa, db: Session = Depends(get_db)):
    """
    Endpoint ATÓMICO para registrar empresa + usuario en una transacción.
    
    Garantiza que si uno falla, el otro no se crea (rollback automático).
    
    Request:
        {
            "nombre_comercial": "Tienda La Esperanza",
            "nit_o_cedula": "900123456-1",
            "email": "admin@esperanza.com",
            "password": "Password123",
            "rol": "admin"
        }
    
    Response:
        {
            "access_token": "eyJhbGc...",
            "token_type": "bearer",
            "usuario": {
                "id": "...",
                "email": "admin@esperanza.com",
                "empresa_id": "...",
                "rol": "admin",
                "created_at": "...",
                "is_active": true
            }
        }
    
    Status Codes:
        201 Created: Registro exitoso
        409 Conflict: Email o NIT duplicado
        422 Unprocessable Entity: Datos inválidos (Pydantic)
        500 Internal Server Error: Error en la BD
    """
    result = auth_service.registrar_usuario_con_empresa(
        nombre_comercial=data.nombre_comercial,
        nit_o_cedula=data.nit_o_cedula,
        email=data.email,
        password=data.password,
        rol=data.rol,
        db=db,
    )
    return result
```

---

## 🎯 CAMBIO 4: Frontend - Simplificar a Paso Único

**Archivo:** `frontend/src/pages/Registro.jsx`

**VERSIÓN MEJORADA (Paso único atómico):**

```jsx
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Registro() {
  const { registrar } = useAuth()
  const navigate = useNavigate()

  const [form, setForm] = useState({
    nombre_comercial: '',
    nit_o_cedula: '',
    email: '',
    password: '',
  })
  const [error, setError] = useState(null)
  const [cargando, setCargando] = useState(false)

  const cambiar = (e) => setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))

  const handleRegistro = async (e) => {
    e.preventDefault()
    setCargando(true)
    setError(null)

    // Validación defensiva
    if (!form.nombre_comercial.trim()) {
      setError('El nombre comercial es obligatorio')
      setCargando(false)
      return
    }
    if (!form.nit_o_cedula.trim()) {
      setError('El NIT/Cédula es obligatorio')
      setCargando(false)
      return
    }
    if (!form.email.trim()) {
      setError('El email es obligatorio')
      setCargando(false)
      return
    }
    if (form.password.length < 8) {
      setError('La contraseña debe tener al menos 8 caracteres')
      setCargando(false)
      return
    }

    const payload = {
      nombre_comercial: form.nombre_comercial.trim(),
      nit_o_cedula: form.nit_o_cedula.trim(),
      email: form.email.trim().toLowerCase(),
      password: form.password,
      rol: 'admin',
    }

    console.debug('[Registro] Payload:', payload)

    try {
      // ✅ Ahora es TODO EN UNO (transacción atómica en el backend)
      await registrar(payload)
      navigate('/inventario', { replace: true })
    } catch (e) {
      console.error('[Registro] Error:', e)
      setError(e.message || 'Error en el registro')
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 to-violet-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm p-8">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800">Crear cuenta</h1>
          <p className="text-gray-500 text-sm mt-1">
            Registro de empresa + administrador
          </p>
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm text-center mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleRegistro} className="space-y-4">
          {/* Sección: Datos de la Empresa */}
          <div className="border-b pb-4 mb-4">
            <h2 className="text-sm font-semibold text-gray-700 mb-3">📦 Datos de la Empresa</h2>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nombre comercial
              </label>
              <input
                type="text"
                name="nombre_comercial"
                value={form.nombre_comercial}
                onChange={cambiar}
                required
                placeholder="Tienda La Esperanza"
                className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400"
              />
            </div>

            <div className="mt-3">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                NIT o Cédula
              </label>
              <input
                type="text"
                name="nit_o_cedula"
                value={form.nit_o_cedula}
                onChange={cambiar}
                required
                placeholder="900123456-1"
                className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400"
              />
            </div>
          </div>

          {/* Sección: Datos del Administrador */}
          <div>
            <h2 className="text-sm font-semibold text-gray-700 mb-3">👤 Datos del Administrador</h2>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Correo
              </label>
              <input
                type="email"
                name="email"
                value={form.email}
                onChange={cambiar}
                required
                autoComplete="email"
                placeholder="admin@empresa.com"
                className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400"
              />
            </div>

            <div className="mt-3">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contraseña
                <span className="text-gray-400 font-normal"> (mín. 8 caracteres)</span>
              </label>
              <input
                type="password"
                name="password"
                value={form.password}
                onChange={cambiar}
                required
                minLength={8}
                autoComplete="new-password"
                placeholder="••••••••"
                className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={cargando}
            className="w-full bg-violet-600 hover:bg-violet-700 disabled:bg-gray-200 text-white font-semibold py-3 rounded-lg transition-colors mt-6"
          >
            {cargando ? 'Creando cuenta...' : 'Crear cuenta'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          ¿Ya tienes cuenta?{' '}
          <Link to="/login" className="text-violet-600 hover:text-violet-700 font-medium">
            Ingresar
          </Link>
        </p>
      </div>
    </div>
  )
}
```

---

## 🎯 CAMBIO 5: Frontend - Actualizar AuthService

**Archivo:** `frontend/src/services/authService.js`

**Actualizar la función `registro()`:**

```javascript
async registro(payload) {
  // ✅ Detectar si es registro completo o solo usuario
  const endpoint = (payload.nombre_comercial) 
    ? `${BASE}/registro-completo`  // Nuevo: Empresa + Usuario atómico
    : `${BASE}/registro`;           // Legado: Solo usuario
  
  console.debug(`[authService] Usando endpoint: ${endpoint}`)
  console.debug(`[authService] Payload:`, payload)
  
  const res = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  
  if (!res.ok) {
    let errorDetail = 'Error en el registro'
    try {
      const err = await res.json()
      errorDetail = err.detail || errorDetail
    } catch {
      errorDetail = `Error HTTP ${res.status}`
    }
    console.error(`[authService] Error (${res.status}):`, errorDetail)
    throw new Error(errorDetail)
  }
  
  const data = await res.json()
  console.debug(`[authService] Registro exitoso, token guardado`)
  this.setToken(data.access_token)
  return data
}
```

---

## 🧪 CAMBIO 6: Tests - Validar Atomicidad

**Archivo:** `tests/test_registro_atomico.py` (NUEVO)

```python
import pytest
from app.models import Usuario, Empresa, RolUsuario
from app.services.auth_service import hash_password

@pytest.fixture
def client():
    """Fixture para cliente de prueba"""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)

@pytest.fixture
def db():
    """Fixture para sesión de BD"""
    from app.database import SessionLocal
    session = SessionLocal()
    yield session
    session.close()

def test_registro_completo_exitoso(client, db):
    """✅ Test: Registro exitoso de empresa + usuario"""
    payload = {
        "nombre_comercial": "Test Store Inc",
        "nit_o_cedula": "999888777-1",
        "email": "admin@teststore.com",
        "password": "TestPass1234",
        "rol": "admin",
    }
    
    response = client.post("/registro-completo", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["usuario"]["email"] == payload["email"]
    assert data["usuario"]["rol"] == "admin"
    
    # Verificar en BD
    usuario = db.query(Usuario).filter(Usuario.email == payload["email"]).first()
    assert usuario is not None
    empresa = db.query(Empresa).filter(Empresa.nit_o_cedula == payload["nit_o_cedula"]).first()
    assert empresa is not None
    assert usuario.empresa_id == empresa.id

def test_registro_email_duplicado(client, db):
    """❌ Test: Email duplicado → Rechazo"""
    # Crear primer usuario
    payload1 = {
        "nombre_comercial": "Store A",
        "nit_o_cedula": "111222333-1",
        "email": "admin@storeA.com",
        "password": "Pass1234",
        "rol": "admin",
    }
    client.post("/registro-completo", json=payload1)
    
    # Intentar crear con el mismo email
    payload2 = {
        "nombre_comercial": "Store B",
        "nit_o_cedula": "444555666-1",
        "email": "admin@storeA.com",  # ← Duplicado
        "password": "Pass1234",
        "rol": "admin",
    }
    response = client.post("/registro-completo", json=payload2)
    
    assert response.status_code == 409
    data = response.json()
    assert "email" in data["detail"].lower() or "registrado" in data["detail"].lower()
    
    # Verificar que la empresa B NO se creó (rollback)
    empresa_b = db.query(Empresa).filter(Empresa.nit_o_cedula == "444555666-1").first()
    assert empresa_b is None

def test_registro_nit_duplicado(client, db):
    """❌ Test: NIT duplicado → Rechazo + Rollback"""
    # Crear primera empresa
    payload1 = {
        "nombre_comercial": "Store X",
        "nit_o_cedula": "777888999-1",
        "email": "admin@storex.com",
        "password": "Pass1234",
        "rol": "admin",
    }
    client.post("/registro-completo", json=payload1)
    
    # Intentar crear con el mismo NIT
    payload2 = {
        "nombre_comercial": "Store Y",
        "nit_o_cedula": "777888999-1",  # ← Duplicado
        "email": "admin@storey.com",
        "password": "Pass1234",
        "rol": "admin",
    }
    response = client.post("/registro-completo", json=payload2)
    
    assert response.status_code == 409
    data = response.json()
    assert "nit" in data["detail"].lower() or "empresa" in data["detail"].lower()
    
    # Verificar que el usuario Y NO se creó (rollback)
    usuario_y = db.query(Usuario).filter(Usuario.email == "admin@storey.com").first()
    assert usuario_y is None

def test_registro_password_corta(client):
    """❌ Test: Contraseña muy corta → Error 422"""
    payload = {
        "nombre_comercial": "Store Z",
        "nit_o_cedula": "111111111-1",
        "email": "admin@storez.com",
        "password": "short",  # ← Menos de 8 caracteres
        "rol": "admin",
    }
    
    response = client.post("/registro-completo", json=payload)
    
    assert response.status_code == 422

def test_registro_email_invalido(client):
    """❌ Test: Email inválido → Error 422"""
    payload = {
        "nombre_comercial": "Store W",
        "nit_o_cedula": "222222222-1",
        "email": "not-an-email",  # ← Email inválido
        "password": "ValidPass1234",
        "rol": "admin",
    }
    
    response = client.post("/registro-completo", json=payload)
    
    assert response.status_code == 422
```

---

## 📊 RESUMEN DE CAMBIOS

| Archivo | Cambio | Impacto |
|---------|--------|--------|
| `app/schemas/usuario.py` | ✅ Agregar `UsuarioCrearConEmpresa` | Permite validar empresa+usuario juntos |
| `app/services/auth_service.py` | ✅ Agregar `registrar_usuario_con_empresa()` | Transacción atómica con rollback |
| `app/routers/auth.py` | ✅ Agregar endpoint `/registro-completo` | Expone la nueva funcionalidad |
| `frontend/src/pages/Registro.jsx` | ✅ Simplificar a 1 paso | UX mejorada + atomicidad garantizada |
| `frontend/src/services/authService.js` | ✅ Auto-detectar endpoint | Compatible con código antiguo |
| `tests/test_registro_atomico.py` | ✅ Agregar suite de tests | Valida atomicidad y rollback |

---

## 🚀 ORDEN DE IMPLEMENTACIÓN

**Paso 1:** Backend (menos riesgo de quiebre)
```bash
1. Actualizar app/schemas/usuario.py
2. Actualizar app/services/auth_service.py
3. Actualizar app/routers/auth.py
4. Probar con cURL manual
```

**Paso 2:** Tests
```bash
5. Crear tests/test_registro_atomico.py
6. Ejecutar: pytest tests/test_registro_atomico.py -v
```

**Paso 3:** Frontend (sin quiebre, fallback automático)
```bash
7. Actualizar frontend/src/pages/Registro.jsx
8. Actualizar frontend/src/services/authService.js
9. Probar en el navegador
```

---

## ✅ VALIDACIÓN POSTERIOR

Después de implementar, verifica:

```bash
# 1. ¿El endpoint nuevo existe?
curl http://localhost:8000/docs
# → Busca "/registro-completo" en Swagger

# 2. ¿Funciona el flujo atómico?
# → Prueba a registrarse → Debería funcionar al primer intento

# 3. ¿Se hace rollback si falla?
# → Intenta con email duplicado → Debe rechazar sin crear empresa

# 4. ¿Los tests pasan?
pytest tests/test_registro_atomico.py -v
```

---

**Implementación completada = Flujo robusto, atómico y con errores claros ✅**
