# 🚀 PLAN DE MIGRACIÓN: TIENDAPP → ARQUITECTURA ORQUESTADA POR CLAUDE CODE

**Objetivo**: Reconstruir Tiendapp manteniendo funcionalidad pero con arquitectura moderna, escalable y mantenible.

**Principio de Oro**: "No reescribas lo que funciona. Refactoriza lo que es frágil."

---

## FASE 1: PREPARACIÓN (Semana 1)

### 1.1 Auditoría de Dependencias
```bash
# Backend
pip freeze > requirements.txt.current
# Revisar: ¿FastAPI 0.104? ¿SQLAlchemy 2.0? ¿pydantic 2.0?

# Frontend
npm list > dependencies.current.txt
# Revisar: ¿React 19? ¿Vite 8? ¿Tailwind 4?
```

### 1.2 Backup de Base de Datos
```bash
# PostgreSQL
pg_dump gestion_neiva_db > backup_$(date +%Y%m%d).sql

# Verificar integridad
psql gestion_neiva_db < backup_20260505.sql --dry-run
```

### 1.3 Documentar Todas las Rutas Activas
- [x] POST `/registro`
- [x] POST `/token`
- [x] GET `/me`
- [x] POST `/empresas/`
- [x] POST `/productos/`
- [x] GET `/productos/{empresa_id}`
- [x] PUT `/productos/{id}`
- [x] DELETE `/productos/{id}`
- [x] POST `/productos/{id}/imagen`
- [x] POST `/ventas/{empresa_id}`
- [x] GET `/ventas/{empresa_id}`
- [x] GET `/reportes/ventas/excel/{empresa_id}`

---

## FASE 2: REFACTORIZACIÓN BACKEND (Claude Code Iter. 1-3)

### 2.1 Normalizar Esquemas Pydantic

**ANTES** (Problemas):
```python
# main.py línea 57-62
class DetalleVentaCrear(BaseModel):
    producto_id: uuid.UUID
    cantidad: int

# main.py línea 64-82
class DetalleVentaRespuesta(BaseModel):
    id: uuid.UUID
    cantidad: int
    ...

# main.py línea 371-389 - REPETIDO
class DetalleVentaRespuesta(BaseModel):  # ⚠️ DUPLICADO
    id: uuid.UUID
    ...

# main.py línea 468-486 - REPETIDO OTRA VEZ
class DetalleVentaRespuesta(BaseModel):  # ⚠️ TRIPLICADO
    id: uuid.UUID
    ...
```

**DESPUÉS** (Propuesta):
```python
# app/schemas/venta.py
from pydantic import BaseModel, EmailStr, validator
from typing import List
from datetime import datetime
from uuid import UUID

# LECTURA
class DetalleVentaRespuesta(BaseModel):
    id: UUID
    cantidad: int
    precio_unitario: float
    subtotal: float
    producto_nombre: str

    class Config:
        from_attributes = True

class VentaRespuesta(BaseModel):
    id: UUID
    fecha_venta: str
    total: float
    detalles: List[DetalleVentaRespuesta]

    class Config:
        from_attributes = True

# ESCRITURA
class DetalleVentaCrear(BaseModel):
    producto_id: UUID
    cantidad: int
    
    @validator('cantidad')
    def cantidad_positiva(cls, v):
        if v <= 0:
            raise ValueError('Cantidad debe ser > 0')
        return v

class VentaCrear(BaseModel):
    detalles: List[DetalleVentaCrear]
    
    @validator('detalles')
    def detalles_no_vacio(cls, v):
        if not v:
            raise ValueError('Carrito no puede estar vacío')
        return v
```

### 2.2 Crear Módulos Separados

**Estructura propuesta:**
```
app/
├── __init__.py
├── main.py (solo rutas)
├── database.py
├── models.py
├── security.py
├── schemas/
│   ├── __init__.py
│   ├── empresa.py
│   ├── usuario.py
│   ├── producto.py
│   └── venta.py
├── services/
│   ├── __init__.py
│   ├── empresa_service.py
│   ├── producto_service.py
│   ├── venta_service.py
│   └── usuario_service.py
├── dependencies.py (get_current_user, get_current_user_admin)
└── exceptions.py (CustomExceptions)
```

### 2.3 Implementar Manejo de Errores Global

```python
# app/exceptions.py
from fastapi import HTTPException, status

class TiendappException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

class StockInsuficienteException(TiendappException):
    def __init__(self, producto: str, disponible: int, solicitado: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock insuficiente para {producto}. Disponible: {disponible}, Solicitado: {solicitado}"
        )

class ProductoDuplicadoException(TiendappException):
    def __init__(self, codigo_barras: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Producto con código {codigo_barras} ya existe"
        )

class EmailDuplicadoException(TiendappException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email {email} ya está registrado"
        )

# En main.py
from app.exceptions import TiendappException

@app.exception_handler(TiendappException)
async def tiendapp_exception_handler(request, exc: TiendappException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

### 2.4 Agregar Logging Estructurado

```python
# app/logging.py
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# En main.py
@app.post("/ventas/{empresa_id}")
def registrar_venta(...):
    logger.info("venta_iniciada", extra={
        "empresa_id": str(empresa_id),
        "usuario_id": str(current_user.id),
        "cantidad_items": len(venta.detalles)
    })
    try:
        # ... lógica
        logger.info("venta_completada", extra={"total": total_venta})
    except Exception as e:
        logger.error("venta_fallida", extra={"error": str(e)})
        raise
```

### 2.5 Implementar Enums para Estados

```python
# app/models.py (agregar)
from enum import Enum

class RolUsuario(str, Enum):
    ADMIN = "admin"
    TENDERO = "tendero"

class Estado(str, Enum):
    ACTIVO = "activo"
    INACTIVO = "inactivo"

# Usar en modelo
class Usuario(Base):
    __tablename__ = 'usuarios'
    rol = Column(String(50), nullable=False, default=RolUsuario.TENDERO.value)
```

---

## FASE 3: REFACTORIZACIÓN FRONTEND (Claude Code Iter. 4-6)

### 3.1 Implementar Context API (Estado Global)

```javascript
// frontend/src/context/AuthContext.jsx
import { createContext, useContext, useState, useEffect } from 'react'
import authService from '../services/authService'

const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const verificarAutenticacion = async () => {
      try {
        const token = authService.getToken()
        if (token) {
          const user = await authService.getCurrentUser()
          setCurrentUser(user)
        }
      } catch (error) {
        authService.clearToken()
      } finally {
        setIsLoading(false)
      }
    }
    verificarAutenticacion()
  }, [])

  return (
    <AuthContext.Provider value={{ currentUser, setCurrentUser, isLoading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth debe estar dentro de AuthProvider')
  return context
}
```

```javascript
// frontend/src/context/CartContext.jsx
import { createContext, useContext, useState } from 'react'

const CartContext = createContext()

export function CartProvider({ children }) {
  const [cart, setCart] = useState([])
  const [isOpen, setIsOpen] = useState(false)

  const agregarAlCarrito = (producto) => {
    setCart(prevCart => {
      const existe = prevCart.find(item => item.id === producto.id)
      if (existe) {
        return prevCart.map(item =>
          item.id === producto.id 
            ? { ...item, cantidad: item.cantidad + 1 }
            : item
        )
      }
      return [...prevCart, { ...producto, cantidad: 1 }]
    })
    setIsOpen(true)
  }

  const restarDelCarrito = (productoId) =>
    setCart(prevCart =>
      prevCart.map(item =>
        item.id === productoId 
          ? { ...item, cantidad: item.cantidad - 1 }
          : item
      ).filter(item => item.cantidad > 0)
    )

  const eliminarDelCarrito = (productoId) =>
    setCart(prevCart => prevCart.filter(item => item.id !== productoId))

  const vaciarCarrito = () => setCart([])

  return (
    <CartContext.Provider value={{
      cart, setCart, isOpen, setIsOpen,
      agregarAlCarrito, restarDelCarrito, eliminarDelCarrito, vaciarCarrito
    }}>
      {children}
    </CartContext.Provider>
  )
}

export function useCart() {
  const context = useContext(CartContext)
  if (!context) throw new Error('useCart debe estar dentro de CartProvider')
  return context
}
```

### 3.2 Refactorizar App.jsx (Eliminando props drilling)

**ANTES:**
```javascript
// Props se pasan por 5 niveles
<CartSidebar
  cart={cart}
  isOpen={isCartOpen}
  toggleCart={() => setIsCartOpen(!isCartOpen)}
  handleCheckout={procesarVenta}
  agregarAlCarrito={agregarAlCarrito}
  restarDelCarrito={restarDelCarrito}
  eliminarDelCarrito={eliminarDelCarrito}
/>
```

**DESPUÉS:**
```javascript
// CartSidebar.jsx - Sin props
import { useCart, useAuth } from '../context'

export default function CartSidebar() {
  const { cart, isOpen, setIsOpen, vaciarCarrito } = useCart()
  const { currentUser } = useAuth()

  const procesarVenta = async () => {
    // ... lógica
    vaciarCarrito()
  }

  return <div>{/* Componente sin props */}</div>
}
```

### 3.3 Crear Hooks Reutilizables

```javascript
// frontend/src/hooks/useProductos.js
import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import authService from '../services/authService'

export function useProductos() {
  const { currentUser } = useAuth()
  const [productos, setProductos] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const cargarProductos = async () => {
    if (!currentUser) return

    setLoading(true)
    setError(null)
    try {
      const response = await authService.fetchWithAuth(
        `http://localhost:8000/productos/${currentUser.empresa_id}`
      )
      if (!response.ok) throw new Error('Error cargando productos')
      const data = await response.json()
      setProductos(data.inventario)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    cargarProductos()
  }, [currentUser])

  return { productos, loading, error, recargar: cargarProductos }
}

// frontend/src/hooks/useVentas.js
export function useVentas() {
  const { currentUser } = useAuth()
  const [ventas, setVentas] = useState([])
  const [loading, setLoading] = useState(false)

  const cargarVentas = async () => {
    if (!currentUser) return
    setLoading(true)
    try {
      const response = await authService.fetchWithAuth(
        `http://localhost:8000/ventas/${currentUser.empresa_id}`
      )
      const data = await response.json()
      setVentas(data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    cargarVentas()
  }, [currentUser])

  return { ventas, loading }
}
```

### 3.4 Mejorar AuthService

```javascript
// frontend/src/services/authService.js
class AuthService {
  setToken(token) {
    localStorage.setItem('access_token', token)
  }

  getToken() {
    return localStorage.getItem('access_token')
  }

  clearToken() {
    localStorage.removeItem('access_token')
  }

  async getCurrentUser() {
    const response = await this.fetchWithAuth('http://localhost:8000/me')
    if (!response.ok) throw new Error('No autenticado')
    return response.json()
  }

  async login(email, password) {
    const response = await fetch('http://localhost:8000/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })
    if (!response.ok) throw new Error('Credenciales inválidas')
    const { access_token } = await response.json()
    this.setToken(access_token)
    return this.getCurrentUser()
  }

  async registrar(email, password, empresa_id) {
    const response = await fetch('http://localhost:8000/registro', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, empresa_id })
    })
    if (!response.ok) throw new Error('Registro fallido')
    const { access_token } = await response.json()
    this.setToken(access_token)
    return this.getCurrentUser()
  }

  logout() {
    this.clearToken()
  }

  async fetchWithAuth(url, options = {}) {
    const token = this.getToken()
    if (!token) throw new Error('No hay token')

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers
    }

    const response = await fetch(url, { ...options, headers })
    
    if (response.status === 401) {
      this.logout()
      window.location.href = '/login'
    }

    return response
  }
}

export default new AuthService()
```

---

## FASE 4: TESTING (Claude Code Iter. 7-8)

### 4.1 Tests de Backend

```python
# tests/test_auth.py
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal

client = TestClient(app)

def test_registro_usuario_ok():
    response = client.post("/registro", json={
        "email": "test@test.com",
        "password": "Test123!",
        "empresa_id": "461986b2-addd-418c-8cbc-a5e17b3717c7"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_registro_email_duplicado():
    client.post("/registro", json={
        "email": "dup@test.com",
        "password": "Pass123!",
        "empresa_id": "461986b2-addd-418c-8cbc-a5e17b3717c7"
    })
    response = client.post("/registro", json={
        "email": "dup@test.com",  # mismo email
        "password": "Pass123!",
        "empresa_id": "461986b2-addd-418c-8cbc-a5e17b3717c7"
    })
    assert response.status_code == 409  # Conflict

def test_login_credenciales_invalidas():
    response = client.post("/token", json={
        "email": "noexiste@test.com",
        "password": "WrongPass"
    })
    assert response.status_code == 401

# tests/test_ventas.py
def test_registrar_venta_stock_insuficiente():
    # Producto con stock 5
    response = client.post("/ventas/empresa-id", json={
        "detalles": [{"producto_id": "prod-id", "cantidad": 10}]  # Solicita 10
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    assert "Stock insuficiente" in response.json()["detail"]

def test_registrar_venta_transaccion_atomica():
    # Verificar que si falla item 2, item 1 se revierte
    pass
```

### 4.2 Tests de Frontend

```javascript
// tests/useCart.test.jsx
import { renderHook, act } from '@testing-library/react'
import { CartProvider, useCart } from '../context/CartContext'

function wrapper({ children }) {
  return <CartProvider>{children}</CartProvider>
}

test('agregarAlCarrito debe agregar producto', () => {
  const { result } = renderHook(() => useCart(), { wrapper })
  const producto = { id: '1', nombre: 'Leche', precio: 5000 }

  act(() => {
    result.current.agregarAlCarrito(producto)
  })

  expect(result.current.cart).toHaveLength(1)
  expect(result.current.cart[0].cantidad).toBe(1)
})

test('agregarAlCarrito debe incrementar cantidad si existe', () => {
  const { result } = renderHook(() => useCart(), { wrapper })
  const producto = { id: '1', nombre: 'Leche', precio: 5000 }

  act(() => {
    result.current.agregarAlCarrito(producto)
    result.current.agregarAlCarrito(producto)
  })

  expect(result.current.cart).toHaveLength(1)
  expect(result.current.cart[0].cantidad).toBe(2)
})
```

---

## FASE 5: DEPLOYMENT (Claude Code Iter. 9)

### 5.1 Dockerizar Backend

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY main.py .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5.2 Dockerizar Frontend

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist dist
CMD ["serve", "-s", "dist", "-l", "5173"]
```

### 5.3 Docker Compose

```yaml
# docker-compose.yml
version: '3.9'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: gestion_neiva_db
      POSTGRES_PASSWORD: admin123
    volumes:
      - pg_data:/var/lib/postgresql/data

  backend:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://postgres:admin123@db:5432/gestion_neiva_db

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend

volumes:
  pg_data:
```

---

## FASE 6: DOCUMENTACIÓN FINAL (Claude Code Iter. 10)

- [ ] README.md actualizado
- [ ] API.md con OpenAPI/Swagger
- [ ] ARCHITECTURE.md explicando decisiones
- [ ] DEPLOYMENT.md guía de producción
- [ ] CONTRIBUTING.md para otros desarrolladores

---

## ✅ CHECKLIST DE MIGRACIÓN

### Pre-migración
- [ ] Backup completo de BD
- [ ] Documentar todas las APIs activas
- [ ] Identificar y listar todos los bugs conocidos
- [ ] Obtener aprobación del stakeholder

### Fase 1 (Backend Core)
- [ ] Normalizar esquemas Pydantic
- [ ] Crear estructura modular (services/)
- [ ] Implementar manejo de errores global
- [ ] Agregar logging estructurado
- [ ] Implementar Enums

### Fase 2 (Frontend Core)
- [ ] Implementar AuthContext
- [ ] Implementar CartContext
- [ ] Crear hooks reutilizables
- [ ] Refactorizar App.jsx
- [ ] Mejorar AuthService

### Fase 3 (Calidad)
- [ ] Tests unitarios backend (>80% coverage)
- [ ] Tests unitarios frontend (>60% coverage)
- [ ] Tests de integración
- [ ] Performance testing

### Fase 4 (DevOps)
- [ ] Dockerizar aplicación
- [ ] Configurar Docker Compose
- [ ] Configurar CI/CD (GitHub Actions)
- [ ] Documentación deployment

### Post-migración
- [ ] Migración de datos (si hubiera cambios de esquema)
- [ ] QA testing en staging
- [ ] Capacitación de usuarios
- [ ] Monitoreo en producción

---

## 🎯 OBJETIVOS FINALES

| Métrica | Actual | Objetivo |
|---------|--------|----------|
| **Mantenibilidad** | 5/10 | 9/10 |
| **Escalabilidad** | 6/10 | 9/10 |
| **Test Coverage** | 0% | 80% |
| **Deuda Técnica** | Alta | Baja |
| **Tiempo Deploy** | Manual | Automatizado |
| **Documentación** | Parcial | Completa |

---

**Fin de Plan de Migración**
