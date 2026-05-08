# 📋 ANÁLISIS COMPLETO: WIZARD DE REGISTRO - 2 PASOS

## 📁 Documentos Incluidos

Este análisis incluye **3 documentos principales** en este directorio:

1. **`INFORME_TECNICO_WIZARD_REGISTRO.md`** ← 📌 **LEER PRIMERO**
   - Análisis detallado del problema
   - Flujo de datos frontend → backend
   - Comparación de esquemas
   - Causa raíz del "Failed to fetch"

2. **`DIAGNOSTICO_RAPIDO.md`**
   - Checklist de 5 pasos para diagnosticar el error
   - Comandos cURL y SQL para testear
   - Árbol de decisión (¿cuál es el problema?)

3. **`SOLUCION_CODIGO.md`** ← 💾 **CÓDIGO LISTO PARA IMPLEMENTAR**
   - Cambios en backend (schemas, services, routers)
   - Cambios en frontend (React, Registro.jsx)
   - Suite completa de tests
   - Orden de implementación

---

## 🎯 RESUMEN EJECUTIVO

### El Problema
- ✅ Paso 1 (Crear Empresa) funciona y guarda en BD
- ❌ Paso 2 (Crear Administrador) falla con "Failed to fetch" silencioso

### La Raíz Causa
1. **Probable:** El `empresa_id` no existe en BD (falla al validar en Paso 2)
2. **O bien:** Falta de transacción atómica → Si Paso 2 falla, empresa queda huérfana

### La Solución
- ✅ Crear endpoint nuevo `/registro-completo` que hace **TODO EN UNO**
- ✅ Transacción ACID: Empresa + Usuario se crean juntos o no se crean
- ✅ Si falla uno, el otro se descarta (rollback automático)

---

## 🚀 Quick Start: Cómo Usar Este Análisis

### 📍 SI QUIERES DIAGNOSTICAR RÁPIDO
```
1. Lee: DIAGNOSTICO_RAPIDO.md
2. Ejecuta los checks (consola, Network tab, BD)
3. Identifica el error real
```

### 📍 SI QUIERES ENTENDER EL PROBLEMA A FONDO
```
1. Lee: INFORME_TECNICO_WIZARD_REGISTRO.md (completo)
2. Mira los fragmentos de código donde está el desajuste
3. Revisa las mejoras propuestas
```

### 📍 SI QUIERES IMPLEMENTAR LA SOLUCIÓN AHORA
```
1. Abre: SOLUCION_CODIGO.md
2. Copia cada cambio en orden (backend → tests → frontend)
3. Prueba manualmente en el navegador
4. Ejecuta: pytest tests/test_registro_atomico.py -v
```

---

## 📊 Tabla de Hallazgos

| Componente | Estado | Problema | Severidad |
|-----------|--------|---------|-----------|
| Frontend: Captura empresa_id | ✅ OK | Ninguno | - |
| Frontend: Envío Paso 2 | ✅ OK | Ninguno | - |
| Backend: Esquemas | ✅ OK | Alineados con frontend | - |
| Backend: Validación | ⚠️ BIEN | Error 404 opaco | 🟡 MEDIO |
| **Transacción atómica** | ❌ **NO EXISTE** | **SIN ROLLBACK** | 🔴 **CRÍTICO** |
| Manejo de errores | ⚠️ PARCIAL | "Failed to fetch" silencioso | 🟡 ALTO |

---

## 💡 3 Mejoras Principales

### Mejora 1️⃣ - Diagnosticar el Error Real
**Antes:** Error "Failed to fetch" → ¿Qué salió mal? 🤷
**Después:** Error claro (404/409/422) → Mensaje legible

### Mejora 2️⃣ - Hacer Transacción Atómica
**Antes:** Empresa creada + Usuario falla → Datos zombies 🧟
**Después:** Ambos se crean O ambos se descartan ✅

### Mejora 3️⃣ - Simplificar UX
**Antes:** 2 pasos separados (estado complejo) 🔄
**Después:** 1 formulario atómico (más simple) ✅

---

## 🔍 Snippets Clave del Análisis

### ❌ Problema: Sin Rollback
```
Paso 1: CREATE empresa            ✅ commit
Paso 2: CREATE usuario (falla)    ❌ error 404
Resultado: Empresa existe, usuario NO existe ← INCONSISTENCIA
```

### ✅ Solución: Transacción Atómica
```
Paso 1: CREATE empresa            + flush (sin commit)
Paso 2: CREATE usuario            + flush (sin commit)
Si ambos OK: COMMIT (ambos se guardan)
Si uno falla: ROLLBACK (ambos se descartan)
```

---

## 📋 Checklist: ¿Qué Hay Que Hacer?

### Fase 1: Diagnosticar (15 min)
- [ ] Abre DevTools Network tab
- [ ] Intenta registrar en Paso 2
- [ ] Mira qué error HTTP devuelve (404/409/422/500)
- [ ] Revisa logs del backend

### Fase 2: Solucionar (1 hora)
- [ ] Implementa cambios en `app/services/auth_service.py`
- [ ] Implementa cambios en `app/routers/auth.py`
- [ ] Implementa cambios en `frontend/src/pages/Registro.jsx`
- [ ] Prueba en navegador

### Fase 3: Validar (30 min)
- [ ] Registra empresa + usuario → Debe funcionar
- [ ] Intenta con email duplicado → Debe rechazar
- [ ] Ejecuta tests: `pytest tests/test_registro_atomico.py -v`
- [ ] Verifica que token se guarda en localStorage

---

## 🛠️ Comandos Rápidos

### Ver el endpoint actual
```bash
curl http://localhost:8000/docs
# → Busca POST /registro
```

### Testear si el backend funciona (cURL)
```bash
curl -X POST http://localhost:8000/registro \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Password123",
    "empresa_id": "550e8400-e29b-41d4-a716-446655440000",
    "rol": "admin"
  }' | jq .
```

### Ver si la empresa se creó en BD
```sql
SELECT id, nombre_comercial FROM empresas ORDER BY created_at DESC LIMIT 5;
```

### Ver si el usuario se creó en BD
```sql
SELECT id, email, empresa_id FROM usuarios ORDER BY created_at DESC LIMIT 5;
```

---

## 📞 Preguntas Frecuentes

**P: ¿Por qué "Failed to fetch" es un error silencioso?**
> R: El frontend solo recibe "Failed to fetch" si hay error de red/CORS. Si es error HTTP (4xx/5xx), debería ver el JSON. Probable: la BD no tiene la empresa → Error 404 → Frontend lo captura.

**P: ¿Por qué no basta con el endpoint actual `/registro`?**
> R: Porque el flujo es: Paso 1 (empresa_id se genera) → Paso 2 (se envía empresa_id). Si hay gap, puede fallar. La nueva solución es: TODO EN UNO en el backend → Atomicidad garantizada.

**P: ¿Se puede arreglar solo el frontend?**
> R: Parcialmente. Agregar logging ayuda a diagnosticar, pero no soluciona la falta de transacción atómica. La verdadera solución es en el backend.

**P: ¿Cuándo debo usar `/registro` vs `/registro-completo`?**
> R: `/registro-completo` es el nuevo (para registro con empresa). `/registro` solo para usuarios sin empresa (futuro: tendering).

---

## 📚 Estructura del Análisis

```
.
├── README.md (este archivo)
├── INFORME_TECNICO_WIZARD_REGISTRO.md
│   ├── Parte 1: Flujo Frontend ← Captura empresa_id
│   ├── Parte 2: Esquemas Backend ← Validación Pydantic
│   ├── Parte 3: Manejo Errores ← "Failed to fetch"
│   ├── Parte 4: Transacción ← SIN ROLLBACK (problema)
│   └── Parte 5: Plan Mejora ← Soluciones
├── DIAGNOSTICO_RAPIDO.md
│   ├── Paso 1: DevTools Network
│   ├── Paso 2: Logging Frontend
│   ├── Paso 3: Logs Backend
│   ├── Paso 4: SQL Queries
│   ├── Paso 5: cURL Manual
│   └── Árbol Decisión: ¿Cuál es el error?
└── SOLUCION_CODIGO.md
    ├── Cambio 1: Nuevo Schema
    ├── Cambio 2: Nuevo Service
    ├── Cambio 3: Nuevo Endpoint
    ├── Cambio 4: Frontend Simplificado
    ├── Cambio 5: AuthService Mejorado
    ├── Cambio 6: Tests Completos
    └── Orden Implementación
```

---

## 🎓 Lecciones Aprendidas

1. **Transacciones:** Siempre hacer operaciones relacionadas en UNA transacción, no en dos llamadas separadas.

2. **Error Handling:** "Failed to fetch" es vago. Mejor: devolver JSON con `{ "detail": "mensaje legible" }`.

3. **UX:** 2 pasos separados + estado compartido = complejidad. Mejor: 1 formulario con validación frontend + 1 endpoint atómico en backend.

4. **Testing:** Tests de rollback son **críticos**. Sin ellos, los bugs escondidos se descubren en producción.

---

## ✨ Estado Final Deseado

```
Usuario abre navegador
    ↓
Completa: Nombre empresa, NIT, Email, Password
    ↓
Click "Crear cuenta"
    ↓
Frontend valida (8+ caracteres, email válido, etc.)
    ↓
POST /registro-completo {empresa + usuario}
    ↓
Backend (atómico):
   - Validar email no duplicado ✅
   - Validar NIT no duplicado ✅
   - Crear empresa ✅
   - Crear usuario ✅
   - COMMIT AMBOS ✅
    ↓
Retorna token JWT
    ↓
Frontend: localStorage.setItem(token)
    ↓
Redirige a /inventario
    ↓
Usuario ve dashboard ✨
```

---

## 📞 Contacto / Preguntas

Si después de leer los 3 documentos aún tienes dudas:

1. Revisa el **árbol de decisión** en `DIAGNOSTICO_RAPIDO.md`
2. Ejecuta los comandos de diagnosis
3. Comienza la implementación desde `SOLUCION_CODIGO.md`

---

**Análisis completado: Mayo 6, 2026**  
**Tipo: QA Automation Engineering Review**  
**Estado: Listo para implementación ✅**

Leer primero: [`INFORME_TECNICO_WIZARD_REGISTRO.md`](./INFORME_TECNICO_WIZARD_REGISTRO.md)
