# Registro controlado por SuperAdmin — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminar el auto-registro público desde el Login y mover la creación de empresas al Panel Super Admin.

**Architecture:** Login.jsx pierde el link y App.jsx pierde la ruta `/registro`. SuperAdmin.jsx gana un componente `ModalNuevaEmpresa` que llama al endpoint ya existente `POST /auth/registro-completo`. Sin cambios de backend.

**Tech Stack:** React 19 JSX, TailwindCSS v4, Lucide icons, fetch nativo (no authService — el endpoint es público).

---

## File Map

| File | Action |
|------|--------|
| `frontend/src/pages/Login.jsx` | Modify — remove `Link` import + remove the "Registrar mi Negocio" paragraph |
| `frontend/src/App.jsx` | Modify — remove `Registro` import + remove `/registro` route |
| `frontend/src/pages/SuperAdmin.jsx` | Modify — add `ModalNuevaEmpresa` component + "Nueva Empresa" button in `TabComercios` |

---

### Task 1: Bloquear acceso público al registro

**Files:**
- Modify: `frontend/src/pages/Login.jsx:1-96`
- Modify: `frontend/src/App.jsx:1-36`

- [ ] **Step 1: Editar Login.jsx — quitar link de registro**

  Leer el archivo primero. Luego aplicar dos cambios:

  **Cambio A — quitar `Link` del import (línea 2):**
  ```jsx
  // ANTES
  import { Link, useNavigate } from 'react-router-dom'

  // DESPUÉS
  import { useNavigate } from 'react-router-dom'
  ```

  **Cambio B — eliminar el párrafo completo al final del return (líneas 87-92):**
  ```jsx
  // ELIMINAR COMPLETO — no reemplazar por nada:
  <p className="text-center text-[14px] text-[#64748b] mt-10 font-medium">
    ¿Aún no tienes cuenta?{' '}
    <Link to="/registro" className="text-[#3b82f6] hover:text-[#2563eb] font-bold transition-colors">
      Registrar mi Negocio
    </Link>
  </p>
  ```

- [ ] **Step 2: Editar App.jsx — quitar la ruta `/registro`**

  **Cambio A — quitar import:**
  ```jsx
  // ELIMINAR esta línea:
  import Registro from './pages/Registro'
  ```

  **Cambio B — quitar la ruta:**
  ```jsx
  // ELIMINAR esta línea:
  <Route path="/registro" element={<Registro />} />
  ```

  El archivo final de App.jsx debe quedar así:
  ```jsx
  import { Routes, Route, Navigate } from 'react-router-dom'
  import ProtectedRoute from './components/ProtectedRoute'
  import Layout from './components/layout/Layout'
  import Login from './pages/Login'
  import Dashboard from './pages/Dashboard'
  import Inventario from './pages/Inventario'
  import Ventas from './pages/Ventas'
  import Reportes from './pages/Reportes'
  import Soporte from './pages/Soporte'
  import SuperAdmin from './pages/SuperAdmin'

  export default function App() {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>
            <Route path="/" element={<Navigate to="/inventario" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/inventario" element={<Inventario />} />
            <Route path="/ventas" element={<Ventas />} />
            <Route path="/reportes" element={<Reportes />} />
            <Route path="/soporte" element={<Soporte />} />
          </Route>
        </Route>

        <Route path="/superadmin" element={<SuperAdmin />} />

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    )
  }
  ```

- [ ] **Step 3: Build para verificar sin errores**

  ```powershell
  cd frontend
  npm run build
  ```
  Esperado: `✓ built in Xs` sin errores. Si `Link` fue eliminado del import pero sigue referenciado en algún otro lugar, el build fallará con "Link is not defined" — revisar que el único uso era el link de registro.

- [ ] **Step 4: Commit**

  ```powershell
  git add frontend/src/pages/Login.jsx frontend/src/App.jsx
  git commit -m "feat(auth): remove public self-registration — access now via superadmin only"
  ```

---

### Task 2: Crear empresa desde el Panel Super Admin

**Files:**
- Modify: `frontend/src/pages/SuperAdmin.jsx`

El backend ya tiene `POST /auth/registro-completo` (público, sin auth). Acepta:
```json
{
  "nombre_comercial": "string",
  "nit_o_cedula": "string",
  "email": "string",
  "password": "string",
  "rol": "admin"
}
```
Responde 201 con `{ access_token, token_type }`.

- [ ] **Step 1: Añadir componente `ModalNuevaEmpresa` antes de `TabComercios`**

  Insertar este componente completo ANTES de la línea `// ─── Tab Comercios ───`:

  ```jsx
  // ─── Modal Nueva Empresa ──────────────────────────────────────────────────────

  function ModalNuevaEmpresa({ onClose, onCreada }) {
    const [form, setForm] = useState({
      nombre_comercial: '',
      nit_o_cedula: '',
      email: '',
      password: '',
    })
    const [cargando, setCargando] = useState(false)
    const [error, setError] = useState('')

    function cambiar(e) {
      setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
    }

    async function handleSubmit(e) {
      e.preventDefault()
      if (!form.nombre_comercial.trim() || !form.nit_o_cedula.trim() || !form.email.trim() || !form.password.trim()) {
        setError('Todos los campos son obligatorios.')
        return
      }
      setCargando(true)
      setError('')
      try {
        const res = await fetch(`${API}/auth/registro-completo`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ...form, rol: 'admin' }),
        })
        if (res.status === 201 || res.ok) {
          onCreada()
          onClose()
        } else {
          const data = await res.json().catch(() => ({}))
          setError(data?.detail || 'Error al crear la empresa.')
        }
      } catch {
        setError('Error de conexión.')
      } finally {
        setCargando(false)
      }
    }

    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm px-4">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 relative">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 transition-colors text-lg leading-none"
          >
            &times;
          </button>
          <h2 className="text-lg font-bold text-slate-800 mb-1">Nueva Empresa</h2>
          <p className="text-sm text-slate-500 mb-5">
            Se creara un usuario administrador junto con la empresa.
          </p>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{error}</p>
            )}
            {[
              { name: 'nombre_comercial', label: 'Nombre comercial', type: 'text', placeholder: 'Ej: Tienda Don Pedro' },
              { name: 'nit_o_cedula', label: 'NIT o Cedula', type: 'text', placeholder: 'Ej: 900123456' },
              { name: 'email', label: 'Email del admin', type: 'email', placeholder: 'admin@empresa.com' },
              { name: 'password', label: 'Contrasena inicial', type: 'password', placeholder: 'Min. 8 caracteres' },
            ].map(({ name, label, type, placeholder }) => (
              <div key={name}>
                <label className="block text-sm font-medium text-slate-700 mb-1">{label}</label>
                <input
                  type={type}
                  name={name}
                  value={form[name]}
                  onChange={cambiar}
                  placeholder={placeholder}
                  className="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent transition"
                />
              </div>
            ))}
            <div className="flex gap-3 pt-1">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 font-semibold py-2.5 rounded-xl transition-colors text-sm"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={cargando}
                className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold py-2.5 rounded-xl transition-colors text-sm"
              >
                {cargando ? 'Creando...' : 'Crear Empresa'}
              </button>
            </div>
          </form>
        </div>
      </div>
    )
  }
  ```

- [ ] **Step 2: Añadir state y botón en `TabComercios`**

  En el componente `TabComercios`, añadir el state del modal justo debajo de los estados existentes:

  ```jsx
  // Añadir junto a los useState existentes:
  const [mostrarModal, setMostrarModal] = useState(false)
  ```

  Luego en el `return` principal de `TabComercios`, reemplazar el encabezado donde están "N comercios registrados" y "Actualizar":

  ```jsx
  // ANTES:
  <div className="flex items-center justify-between mb-4">
    <p className="text-sm text-slate-500">{empresas.length} comercio{empresas.length !== 1 ? 's' : ''} registrado{empresas.length !== 1 ? 's' : ''}</p>
    <button
      onClick={cargarEmpresas}
      className="text-xs text-indigo-600 hover:text-indigo-800 font-medium transition-colors"
    >
      Actualizar
    </button>
  </div>

  // DESPUÉS:
  <div className="flex items-center justify-between mb-4">
    <p className="text-sm text-slate-500">{empresas.length} comercio{empresas.length !== 1 ? 's' : ''} registrado{empresas.length !== 1 ? 's' : ''}</p>
    <div className="flex items-center gap-3">
      <button
        onClick={cargarEmpresas}
        className="text-xs text-indigo-600 hover:text-indigo-800 font-medium transition-colors"
      >
        Actualizar
      </button>
      <button
        onClick={() => setMostrarModal(true)}
        className="text-xs bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-3 py-1.5 rounded-lg transition-colors"
      >
        + Nueva Empresa
      </button>
    </div>
  </div>
  {mostrarModal && (
    <ModalNuevaEmpresa
      onClose={() => setMostrarModal(false)}
      onCreada={cargarEmpresas}
    />
  )}
  ```

  También reemplazar el estado vacío para que muestre el botón incluso cuando no hay empresas:

  ```jsx
  // ANTES:
  if (empresas.length === 0) {
    return (
      <div className="flex items-center justify-center py-16 text-slate-400 text-sm">
        No hay comercios registrados.
      </div>
    )
  }

  // DESPUÉS: eliminar ese bloque completo. La lista vacía se maneja con el grid vacío.
  // (Si empresas.length === 0, el grid simplemente no renderiza tarjetas — el botón sigue visible)
  ```

- [ ] **Step 3: Build para verificar sin errores**

  ```powershell
  cd frontend
  npm run build
  ```
  Esperado: `✓ built in Xs` sin errores.

- [ ] **Step 4: Smoke test manual**

  1. Ve a `http://localhost:5173/superadmin`, autentícate con la clave.
  2. En la tab "Comercios", debe aparecer el botón **"+ Nueva Empresa"** en la cabecera.
  3. Click → se abre el modal con 4 campos.
  4. Completa: nombre, NIT, email, password (mínimo 8 chars con mayúscula y número).
  5. Click "Crear Empresa" → modal se cierra, la lista se recarga y aparece la nueva empresa.
  6. Ve a `http://localhost:5173/login` → NO debe aparecer el link "Registrar mi Negocio".
  7. Ve directamente a `http://localhost:5173/registro` → debe redirigir a `/login`.

- [ ] **Step 5: Commit**

  ```powershell
  git add frontend/src/pages/SuperAdmin.jsx
  git commit -m "feat(superadmin): add Nueva Empresa modal — registration now admin-controlled"
  ```
