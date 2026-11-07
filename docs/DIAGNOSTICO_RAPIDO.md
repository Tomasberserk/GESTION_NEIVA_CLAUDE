# 🔧 GUÍA RÁPIDA DE DIAGNÓSTICO - "Failed to fetch" en Paso 2

## Paso 1: Verificar que el empresa_id se captura correctamente

### En el Frontend (React DevTools)

```javascript
// Abre la consola del navegador (F12) y ejecuta:
localStorage.getItem('access_token')
// Si muestra un token, significa que el registro del usuario funcionó ✅
// Si es null, el usuario no se registró ❌
```

### En el Network Tab (DevTools)

1. Abre DevTools (F12)
2. Ve a **Network**
3. Recarga y haz el registro de empresa (Paso 1)
4. Busca la solicitud `POST /empresas/`
5. Verifica la **Response**:

```json
{
  "mensaje": "Empresa creada exitosamente",
  "empresa": {
    "id": "AQUÍ_DEBE_HABER_UN_UUID",
    "nombre_comercial": "...",
    "nit_o_cedula": "...",
    "created_at": "...",
    "is_active": true
  }
}
```

✅ Si ves un UUID válido, Paso 1 funcionó.

---

## Paso 2: Capturar el error real del Paso 2

### Agregar Logging en Frontend

**Edita `frontend/src/pages/Registro.jsx`:**

```jsx
const registrarUsuario = async (e) => {
  e.preventDefault()
  setCargando(true)
  setError(null)
  
  console.log('🚀 Iniciando Paso 2...')
  console.log('empresaId:', empresaId)
  console.log('form:', form)
  
  try {
    const payload = { ...form, empresa_id: empresaId, rol: 'admin' }
    console.log('📤 Payload enviado:', JSON.stringify(payload, null, 2))
    
    await registrar(payload)
    navigate('/inventario', { replace: true })
  } catch (e) {
    console.error('❌ Error en registrar():', e)
    console.error('Mensaje:', e.message)
    console.error('Stack:', e.stack)
    setError(e.message)
  } finally {
    setCargando(false)
  }
}
```

### Ver en DevTools Network Tab

1. Ve a **Network**
2. Completa el formulario del Paso 2
3. Busca la solicitud `POST /registro`
4. Haz click en ella y ve a **Response**

**Si ves error 404:**
```json
{
  "detail": "Empresa no encontrada"
}
```

→ **La empresa NO se guardó en Paso 1** o se eliminó.

**Si ves error 409:**
```json
{
  "detail": "Este email ya está registrado"
}
```

→ **El email ya existe** en la BD.

**Si ves error 422:**
```json
{
  "detail": [
    {
      "type": "uuid_parsing",
      "loc": ["body", "empresa_id"],
      "msg": "Invalid UUID version"
    }
  ]
}
```

→ **El empresa_id no es un UUID válido** (el frontend envía algo inválido).

**Si ves error 500:**
```json
{
  "detail": "Internal Server Error"
}
```

→ **Bug en el backend** (revisar logs del server FastAPI).

---

## Paso 3: Revisar Logs del Backend

### En la terminal donde corre FastAPI:

Busca líneas como estas después de intentar Paso 2:

```
INFO:     POST /registro HTTP/1.1" 201 Created
```
✅ = Éxito

```
INFO:     POST /registro HTTP/1.1" 404 Not Found
```
❌ = Empresa no encontrada

```
INFO:     POST /registro HTTP/1.1" 422 Unprocessable Entity
```
❌ = Error de validación Pydantic

```
ERROR:    Traceback (most recent call last):
  ...
```
❌ = Error crítico en el backend

---

## Paso 4: Prueba de BD (SQL)

### Conectarse a PostgreSQL:

```bash
psql -h localhost -U tu_usuario -d nombre_db
```

### Verificar si la empresa se creó:

```sql
SELECT id, nombre_comercial, nit_o_cedula, is_active, created_at 
FROM empresas 
ORDER BY created_at DESC 
LIMIT 1;
```

**Si ves un registro:** ✅ La empresa se guardó bien.

**Si no ves registros:** ❌ El Paso 1 falló silenciosamente.

### Verificar si el usuario se creó:

```sql
SELECT id, email, rol, empresa_id, is_active, created_at 
FROM usuarios 
ORDER BY created_at DESC 
LIMIT 1;
```

**Si ves un registro:** ✅ El Paso 2 funcionó.

**Si ves NULL en empresa_id:** ❌ Hubo un problema con la referencia.

---

## Paso 5: Prueba de Endpoint Manual (cURL)

### Obtener un UUID de empresa válido:

```sql
SELECT id FROM empresas LIMIT 1;
```

Copia el UUID (ej: `550e8400-e29b-41d4-a716-446655440000`)

### Hacer request directo:

```bash
curl -X POST http://localhost:8000/registro \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Password123",
    "empresa_id": "550e8400-e29b-41d4-a716-446655440000",
    "rol": "admin"
  }' \
  | jq .
```

Si ves el token, entonces:
- ✅ El backend funciona bien
- ❌ El problema está en cómo el frontend envía los datos

---

## 🎯 Árbol de Decisión - ¿Cuál es el Problema?

```
¿Ves error "Failed to fetch" en el frontend?
    │
    ├─→ [SÍ] ¿Qué dice el Network tab?
    │   │
    │   ├─→ 404 "Empresa no encontrada"
    │   │   └─→ PROBLEMA: Empresa_id inválido o empresa no se guardó en Paso 1
    │   │       SOLUCIÓN: Verificar Paso 1 en BD, revisar cURL manual
    │   │
    │   ├─→ 409 "Email ya registrado"
    │   │   └─→ PROBLEMA: Email duplicado
    │   │       SOLUCIÓN: Usar un email diferente o limpiar BD
    │   │
    │   ├─→ 422 "UUID parsing"
    │   │   └─→ PROBLEMA: empresa_id no es UUID válido
    │   │       SOLUCIÓN: console.log(empresaId) en frontend
    │   │
    │   ├─→ 500 "Internal Server Error"
    │   │   └─→ PROBLEMA: Bug en el backend
    │   │       SOLUCIÓN: Revisar logs de FastAPI
    │   │
    │   └─→ Sin respuesta (timeout)
    │       └─→ PROBLEMA: CORS o servidor no responde
    │           SOLUCIÓN: Verificar que FastAPI está corriendo
    │
    └─→ [NO] ¿Funcionó el registro?
        └─→ [SÍ] ¿Hay token en localStorage?
            └─→ [SÍ] ✅ TODO FUNCIONÓ (probablemente fue un error transitorio)
            └─→ [NO] ❌ Frontend no guardó el token
```

---

## 💡 Checklist Rápido

- [ ] FastAPI está corriendo en `http://localhost:8000`
- [ ] Frontend Vite está corriendo en `http://localhost:5173` o `5174`
- [ ] PostgreSQL está accesible
- [ ] CORS está configurado (revisar `app/main.py`)
- [ ] Empresa se creó exitosamente en Paso 1 (verificar BD)
- [ ] Email no es duplicado
- [ ] empresa_id es un UUID válido (no null, no string vacío)
- [ ] Backend recibe el JSON con todos los campos

---

## 🚨 Si Nada Funciona

1. **Reinicia todo:**
   ```bash
   # Terminal 1: Backend
   cd app
   python dev.py
   
   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

2. **Limpia la BD de datos de prueba:**
   ```sql
   DELETE FROM empresas WHERE nombre_comercial LIKE 'Test%';
   ```

3. **Limpia localStorage en el navegador:**
   ```javascript
   localStorage.clear()
   ```

4. **Recarga todo (Ctrl+Shift+R)**

---

**Resuelto con este checklist? ¡Comenta cuál fue el problema!**

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
