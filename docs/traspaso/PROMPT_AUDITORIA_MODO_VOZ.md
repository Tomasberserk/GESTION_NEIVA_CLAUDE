# Prompt de Auditoría — Modo Voz "Manos Libres" (botones muertos / orbe muerto)

> **Uso:** pega este prompt completo en una sesión nueva (Gemini/Antigravity u otro auditor).
> El auditor NO debe proponer features nuevas: su única tarea es auditar el flujo de eventos
> de click del Modo Voz desde el DOM hasta el estado React y encontrar por qué los botones
> dejan de responder en el navegador del usuario (deploy: `gestion-neiva-claude.vercel.app`).

---

## Prompt

Eres un auditor senior de frontend con foco en QA de React. Audita el flujo de interacción
del "Modo Voz (Manos Libres)" de este proyecto (repo: Gestión Neiva). Tu único objetivo es
encontrar las causas por las que, en producción, después de loguearse, los botones del
Modo Voz ("Toca para Iniciar Escucha", "Reiniciar", "Salir") dejan de responder en el
navegador real del usuario, mientras los mismos botones funcionan en pruebas automatizadas.

### Síntomas reportados (timeline real)

1. Usuario se loguea (bundle `index-BRtgzhqd.js` en Vercel) y la UI lo manda al Modo Voz
   (se sospecha click accidental en el FAB del chat, cuyo botón "Modo Voz" abre el modo voz
   por diseño — `AgentWidget.jsx:215` y `Header.jsx:84` son los ÚNICOS abridores).
2. VozTurnManager monta, luego desmonta y remonta: ciclo
   `init IDLE → desmontaje → detenerSesion → READY → IDLE` en consola.
3. Ningún botón del overlay responde (ni orbe, ni Reiniciar, ni Salir).
4. Logger de diagnóstico en fase de captura (`[VOICE-UI] click capturado en fase-documento`)
   A VECES registra los clicks y A VECES no — esto es la señal clave a explicar.
5. Consola muestra errores de `200.js` (`TypeError: reading 'M_ID'` ×8) y
   `net::ERR_SOCKET_NOT_CONNECTED` en `css:2:1` — provienen de una extensión de Chrome,
   no del proyecto (verificarlo y documentar el descarte).
6. Ya se corrigieron y verificaron en vivo: violación de Rules of Hooks en `MostradorMode`
   (hooks tras early-return), crash al cerrar, "Salir" que deslogueaba, z-index con Sidebar.
   NO vuelvas a proponer esos fixes: ya están en `main` (commit `48b9c0c`).

### Preguntas que DEBES responder con evidencia de código

1. **Cadena de eventos completa:** traza el camino de un click en el orbe desde el evento
   nativo → fase de captura en `document` → `VoiceOrb.jsx` → `MostradorMode.handleOrbClick`
   → `useVoiceAgent.activarSesion` → `VoiceTurnManager`. Identifica TODOS los puntos donde
   un listener externo (extensión, service worker, `stopPropagation`/`stopImmediatePropagation`,
   `pointer-events`, overlay invisible con z-index mayor) puede cortar la cadena.
2. **Explica el signo intermitente:** ¿por qué `[VOICE-UI]` a veces registra los clicks y
   a veces no? ¿Qué estado del código (overlay montado/desmontado, orden de listeners con
   extensiones en `document_start`, BFCache restaurado) produce cada caso?
3. **Ciclo mount/unmount:** ¿quién puede desmontar y remontar el widget de voz sin acción
   del usuario? Revisa `ProtectedRoute`, `AgentWidget` (condiciones de render del `<aside>`),
   `AuthContext` (refetch de `/me`), y el remount por navegación del router.
4. **Apertura "espontánea":** confirma que `setModoVozAbierto(true)` solo es alcanzable por
   click del usuario (no existe efecto que lo abra solo), y evalúa si el FAB del chat
   (`AgentWidget.jsx:215`) es trivialmente confundible como causa de "me manda para la orbe".
5. **Robustez de los paracaidas existentes** (revisalos y evaluate si fallan):
   - Cable de emergencia nativo en `MostradorMode.jsx` (botón DOM puro, listener click/
     mousedown/touchend, remoción nuclear del overlay + `location.assign('/dashboard')`).
   - Respaldo por teclado (`Escape`/`Enter` en `window`).
   - Auto-recarga en `pageshow` con `event.persisted` (BFCache).
   Propón mejoras mínimas, no reescrituras.

### Archivos a auditar (en orden de prioridad)

- `frontend/src/components/voice/MostradorMode.jsx` (overlay, handlers, paracaidas, listener de diagnóstico)
- `frontend/src/components/voice/VoiceOrb.jsx` (elemento clicable del orbe)
- `frontend/src/components/AgentWidget.jsx` (montaje del widget, FAB, chat, MostradorMode SIEMPRE montado con `isOpen`)
- `frontend/src/hooks/useVoiceAgent.js` (ciclo de vida del manager, guard de cleanup)
- `frontend/src/services/voice/VoiceTurnManager.js` (FSM IDLE→READY→…→ERROR, watchdog)
- `frontend/src/services/voice/WebSpeechProvider.js` (mic/speak, permisos)
- `frontend/src/context/AgentContext.jsx` y `frontend/src/context/AuthContext.jsx`
- `frontend/src/components/layout/Header.jsx` (botón "Voz" y botón "Salir" de logout — confusión posible)
- `frontend/src/App.jsx` / `ProtectedRoute.jsx` (remounts por navegación)

### Formato de entrega

1. **Hallazgos**: tabla con `causa → evidencia (archivo:línea) → probabilidad (alta/media/baja)`
   → `fix propuesto (mínimo, con diff sugerido)`.
2. **Ranking final**: las 3 causas más probables del síntoma "botones muertos en producción",
   ordenadas, con la PRUEBA EXACTA (paso a paso en el navegador del usuario) que confirma o
   descarta cada una en menos de 60 segundos.
3. **Tesis principal a falsificar**: "una extensión de Chrome registrado en `document_start`
   llama `stopImmediatePropagation()` en fase de captura de `document` y traga los clicks
   antes de que React los vea (por eso `[VOICE-UI]` no aparece). Confirma o refuta con la
   prueba: navegador limpio / incógnito + mismo flujo".
4. NO propongas features, rediseños ni migraciones. Solo causas y fixes mínimos.

Contexto útil: el modo voz funciona E2E en Chromium automatizado (READY→SPEAKING→LISTENING→
ERROR→Reintentar, ciclo limPIO); falla SOLO en el navegador real del usuario, que tiene
varias extensiones (incluida una que inyecta `200.js`) y usa "Preguntar a Gemini".
