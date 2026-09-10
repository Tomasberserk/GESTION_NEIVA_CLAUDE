# Plan de Implementación: Voz Bidireccional Completa y Resiliencia en Modo Mostrador

Habilitar la experiencia completa de voz bidireccional (el asistente habla y escucha con voz natural colombiana), resolviendo definitivamente la inestabilidad de la Web Speech API en teléfonos Android mediante hardware directo (`MediaRecorder`), eliminando la presión de hablar rápido, y corrigiendo el loop de desambiguación con nombres limpios sin paréntesis.

---

## 1. Diagnóstico Previo y Certeza Empírica

1. **Evidencia en Capturas:** La Web Speech API en el dispositivo físico aborta sistemáticamente en 6–14 ms (`onerror: code: aborted`) o se queda muda sin disparar resultados.
2. **Evidencia de Hardware Directo:** La prueba con `MediaRecorder` (`test-voice.html`) confirmó al 100% que el chip de micrófono y altavoz funcionan impecablemente capturando y reproduciendo audio localmente.
3. **TTS (Síntesis de Voz):** El asistente no hablaba porque el micrófono abortaba antes de enviar nada al backend y la sesión iniciaba en silencio.

---

## 2. Decisiones de Diseño

- **Arquitectura Zero-Backend-Changes:** No se modifica el backend, ni la FSM transaccional, ni los modelos SQLAlchemy ni PostgreSQL.
- **Failover Inmediato a Hardware Directo (`BackendSTTProvider`):** Ante cualquier aborto o error de WebSpeech (o directamente en Android), el sistema conmuta sin fricción a grabación comprimida Opus/WebM y transcripción rápida en el servidor (`/api/agente/transcribir-audio`).
- **Cadencia de Voz Cómoda (7–8 segundos + Detección de Silencio):** El tendero ya no tendrá que apresurarse. Podrá hablar con pausas naturales.
- **Orbe Interactivo (Tap-to-Send):** Si el tendero termina de hablar en 2 segundos, puede tocar el orbe para enviar de inmediato sin esperar la pausa de silencio.
- **Voz Saliente (El Asistente Habla):**
  - Al abrir Modo Mostrador: Saludo de bienvenida en audio (*"¡Listo, te escucho! ¿Qué vendiste hoy?"*). Esto saluda al usuario y desbloquea el subsistema de audio en Android Chrome.
  - Al responder: Lee la respuesta de venta/consulta.
  - Al confirmar: Confirma verbalmente la transacción.
- **Desambiguación sin Paréntesis:** Los botones de opciones enviarán el nombre limpio (`opt.label.split('(')[0].trim()`) para evitar que números de precio (`$ 9.500`) confundan el detector del backend.

---

## 3. Cambios Propuestos por Componente

### Frontend: Servicios de Voz (`frontend/src/services/voice/`)

#### [MODIFY] [BackendSTTProvider.js](file:///c:/Users/merid/Documents/GESTION_NEIVA_CLAUDE/frontend/src/services/voice/stt/BackendSTTProvider.js)
- Implementar temporizador generoso de grabación de 8 segundos (en vez de 3.5s).
- Incorporar detector de silencio acústico (VAD ligero con `AudioContext` y `AnalyserNode`, o ventana de inactividad de 1.8s tras detectar voz) para auto-detener la grabación con suavidad.
- Permitir detención manual inmediata (`stop()`) al tocar el orbe.
- Liberar pistas de audio de forma limpia al terminar.

#### [MODIFY] [VoiceTurnManager.js](file:///c:/Users/merid/Documents/GESTION_NEIVA_CLAUDE/frontend/src/services/voice/VoiceTurnManager.js)
- En `_handleSTTError`: Si `err.code === 'aborted'` o `err.code === 'audio-capture'`, conmutar inmediatamente a `this.backendSTTProvider` y reanudar la escucha en vez de ignorar el error o volver a `READY`.
- En `activarSesion`: Soportar saludo inicial hablado opcional (`saludar: true`). El asistente dice *"¡Listo, te escucho! ¿Qué vendiste hoy?"*, transiciona por `SPEAKING` → `SETTLING (250ms)` → `LISTENING`, desbloqueando el audio en Android.
- Limpieza y pre-calentamiento del sintetizador de voz para evitar que el navegador suspenda el audio.

#### [MODIFY] [SpeechSynthesisProvider.js](file:///c:/Users/merid/Documents/GESTION_NEIVA_CLAUDE/frontend/src/services/voice/tts/SpeechSynthesisProvider.js)
- Pre-calentamiento de voz con `resume()` en la primera interacción táctil.
- Formateo de texto hablado: convertir montos monetarios (ej: `$ 9.500` ➔ `9500 pesos`) y eliminar markdown para una dicción fluida y natural.

---

### Frontend: Componentes e Interfaz (`frontend/src/components/voice/` y hooks)

#### [MODIFY] [MostradorMode.jsx](file:///c:/Users/merid/Documents/GESTION_NEIVA_CLAUDE/frontend/src/components/voice/MostradorMode.jsx)
- Limpiar nombres de productos en botones de aclaración:
  ```javascript
  const nombreLimpio = (opt.label || '').split('(')[0].trim()
  seleccionarOpcion(nombreLimpio)
  ```
- Hacer el `VoiceOrb` interactivo con `onClick`:
  - Si el estado es `LISTENING` o `SPEECH_DETECTED`: un toque al orbe detiene la grabación y envía inmediatamente el audio.
  - Si el estado es `READY`: un toque inicia la escucha.
- Ajustar etiquetas visuales para guiar al tendero (*"Toca el orbe para enviar o espera en silencio"*).

#### [MODIFY] [useVoiceAgent.js](file:///c:/Users/merid/Documents/GESTION_NEIVA_CLAUDE/frontend/src/hooks/useVoiceAgent.js)
- Integrar la opción de saludo inicial al activar el modo voz.
- Exponer método `detenerYEnviar()` para el toque manual en el orbe.

---

## 4. Plan de Verificación

### Pruebas Automatizadas
- Ejecutar suite de pruebas de regresión del backend para confirmar cero impacto en la FSM:
  ```powershell
  .venv/Scripts/pytest tests/ -v
  ```
- Validar build de Vite en el frontend para asegurar cero errores de sintaxis o empaquetado:
  ```powershell
  cd frontend ; npm run build
  ```

### Pruebas Manuales en el Dispositivo Móvil
1. **Despliegue a Vercel:** Commit y push a `main`.
2. **Apertura de Modo Mostrador:**
   - Tocar el botón de Modo Mostrador.
   - **Verificación:** El asistente saluda en voz alta (*"¡Listo, te escucho! ¿Qué vendiste hoy?"*).
3. **Captura de Voz Cómoda:**
   - Hablar a ritmo normal con pausas (*"Ey bro... vendí dos aceites"*).
   - **Verificación:** El orbe pasa a `SPEECH_DETECTED`, no se corta a los 3 segundos, y procesa al terminar.
4. **Respuesta Hablada del Asistente:**
   - **Verificación:** El asistente lee la respuesta por el altavoz.
5. **Prueba del Loop de Desambiguación:**
   - Si ofrece opciones de aceite, tocar la opción deseada.
   - **Verificación:** Envía el nombre limpio sin paréntesis y avanza de inmediato a confirmación sin ciclar.
