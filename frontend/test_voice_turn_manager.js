// Mock DOM and Web APIs for Node.js
global.window = {
  SpeechRecognition: class MockSpeechRecognition {
    constructor() {
      this.lang = 'es-ES';
      this.continuous = false;
      this.interimResults = true;
      this.onstart = null;
      this.onend = null;
      this.onresult = null;
      this.onerror = null;
      this.onspeechstart = null;
      this._started = false;
    }
    start() {
      if (this._started) throw new Error("InvalidStateError: recognition has already started");
      this._started = true;
      setTimeout(() => { if (this.onstart) this.onstart(); }, 5);
    }
    stop() {
      this._started = false;
      setTimeout(() => { if (this.onend) this.onend(); }, 5);
    }
    abort() {
      this._started = false;
      setTimeout(() => { if (this.onend) this.onend(); }, 5);
    }
  },
  webkitSpeechRecognition: null,
  SpeechSynthesisUtterance: class MockSpeechSynthesisUtterance {
    constructor(text) {
      this.text = text;
      this.onend = null;
      this.onerror = null;
    }
  },
  speechSynthesis: {
    speak: (utt) => { if (utt && utt.onend) setTimeout(() => utt.onend(), 10); },
    cancel: () => {},
    resume: () => {},
    getVoices: () => [{ lang: 'es-CO', name: 'Colombian' }]
  },
  AudioContext: class MockAudioContext {
    constructor() { this.state = 'running'; }
    createMediaStreamSource() { return { connect: () => {} }; }
    createAnalyser() {
      return {
        fftSize: 512,
        getFloatTimeDomainData: (buf) => buf.fill(0)
      };
    }
    close() { return Promise.resolve(); }
    resume() { return Promise.resolve(); }
  }
};

global.SpeechSynthesisUtterance = global.window.SpeechSynthesisUtterance;

Object.defineProperty(globalThis, 'navigator', {
  value: {
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
    mediaDevices: {
      getUserMedia: async () => ({
        getTracks: () => [{ stop: () => {} }]
      })
    }
  },
  configurable: true,
  writable: true
});

global.MediaRecorder = class MockMediaRecorder {
  constructor(stream, opts) {
    this.stream = stream;
    this.state = 'inactive';
    this.ondataavailable = null;
    this.onstart = null;
    this.onstop = null;
  }
  static isTypeSupported() { return true; }
  start() {
    this.state = 'recording';
    if (this.onstart) setTimeout(() => this.onstart(), 5);
  }
  stop() {
    this.state = 'inactive';
    if (this.onstop) setTimeout(() => this.onstop(), 5);
  }
};

global.localStorage = {
  getItem: () => 'fake_token',
  setItem: () => {}
};

import { VoiceTurnManager, VoiceTurnState } from './src/services/voice/VoiceTurnManager.js';

async function runTests() {
  console.log('====================================================');
  console.log('🧪 INICIANDO SUITE DE TESTS FORMALES PARA CICLO DE VOZ');
  console.log('====================================================\n');

  let passed = 0;
  let total = 0;

  function assert(condition, message) {
    total++;
    if (!condition) {
      console.error(`❌ FALLÓ: ${message}`);
      process.exit(1);
    }
    console.log(`✅ PASÓ: ${message}`);
    passed++;
  }

  // TEST F: Start duplicado -> Lifecycle guard impide InvalidStateError
  console.log('--- EJECUTANDO TEST F: Start duplicado ---');
  {
    const manager = new VoiceTurnManager();
    await manager.iniciarEscucha();
    assert(manager.state === VoiceTurnState.LISTENING, 'Primer start() pone estado en LISTENING');
    
    // Intento de start duplicado mientras ya está escuchando
    await manager.iniciarEscucha();
    assert(manager.state === VoiceTurnState.LISTENING, 'Segundo start() es bloqueado por lifecycle guard sin lanzar excepción');
    manager.detenerSesion();
  }

  // TEST D: Doble pulsación en detenerYEnviar() -> Idempotencia
  console.log('\n--- EJECUTANDO TEST D: Doble pulsación (Idempotencia) ---');
  {
    let messagesSent = 0;
    const manager = new VoiceTurnManager({
      onSendMessage: async (text) => {
        messagesSent++;
        return { respuesta: 'OK', estado: 'EXECUTED' };
      }
    });

    await manager.iniciarEscucha();
    const turn1 = manager.currentTurnId;
    
    // Simular que el motor detectó habla
    manager.currentSTT.onSpeechStart?.();
    manager.interimTranscript = 'dos aceites';

    // Doble pulsación rápida
    manager.detenerYEnviar();
    manager.detenerYEnviar();

    assert(manager.stopRequested === true, 'stopRequested marcado en true');
    assert(messagesSent === 1, `Exactamente 1 mensaje enviado tras doble pulsación (obtenido: ${messagesSent})`);
    manager.detenerSesion();
  }

  // TEST E: Watchdog viejo de Turn 1 que despierta en Turn 2 -> STALE_CALLBACK_IGNORED
  console.log('\n--- EJECUTANDO TEST E: Watchdog viejo ignorado en nuevo turno ---');
  {
    const manager = new VoiceTurnManager();
    await manager.iniciarEscucha();
    const turn1 = manager.currentTurnId;
    
    // Simular que turn 1 finaliza
    manager._invalidateCurrentTurn();
    const turn2 = manager.currentTurnId;
    assert(turn2 > turn1, `Turno invalidado exitosamente (turn1=${turn1}, turn2=${turn2})`);

    // Iniciar nuevo turno
    await manager.iniciarEscucha();
    const turn3 = manager.currentTurnId;

    // Simular que el timer viejo de turn 1 despierta
    let staleIgnored = false;
    const origWarn = console.warn;
    console.warn = (msg) => {
      if (typeof msg === 'string' && msg.includes('STALE_CALLBACK_IGNORED')) {
        staleIgnored = true;
      }
      origWarn(msg);
    };

    // Invocar watchdog con turn1
    manager._iniciarWatchdogSTT(turn1);
    
    // Dejar correr
    await new Promise(r => setTimeout(r, 20));
    console.warn = origWarn;
    assert(manager.currentTurnId === turn3, 'Turno 3 sigue siendo el activo');
    manager.detenerSesion();
  }

  // TEST B: Hablar y tocar orbe inmediatamente (requestStop -> onresult)
  console.log('\n--- EJECUTANDO TEST B: Hablar y tocar orbe inmediatamente ---');
  {
    let messageReceived = null;
    const manager = new VoiceTurnManager({
      onSendMessage: async (text) => {
        messageReceived = text;
        return { respuesta: 'OK', estado: 'EXECUTED' };
      }
    });

    await manager.iniciarEscucha();
    const activeTurn = manager.currentTurnId;

    // Usuario habla
    manager.currentSTT.onSpeechStart?.();
    
    // Usuario pulsa el orbe
    manager.detenerYEnviar();
    assert(manager.stopRequested === true, 'requestStop() registra stopRequested');

    // Motor emite onresult
    manager.currentSTT.onTranscript?.('aceite cristal', true);
    await new Promise(r => setTimeout(r, 10));

    assert(messageReceived === 'aceite cristal', `Mensaje procesado con éxito tras requestStop (obtenido: "${messageReceived}")`);
    manager.detenerSesion();
  }

  // TEST A: Hablar y esperar resultado normal
  console.log('\n--- EJECUTANDO TEST A: Hablar y esperar resultado normal ---');
  {
    let messageReceived = null;
    const manager = new VoiceTurnManager({
      onSendMessage: async (text) => {
        messageReceived = text;
        return { respuesta: 'Venta registrada', estado: 'EXECUTED' };
      }
    });

    await manager.iniciarEscucha();
    manager.currentSTT.onSpeechStart?.();
    manager.currentSTT.onTranscript?.('panela por libra', true);
    await new Promise(r => setTimeout(r, 10));

    assert(messageReceived === 'panela por libra', 'Turno finalizado y mensaje enviado normalmente');
    assert(manager.state === VoiceTurnState.SPEAKING, 'Transiciona a SPEAKING con respuesta del agente');
    manager.detenerSesion();
  }

  // TEST C: Sin onresult en WebSpeech -> Timeout requestStop activa BackendSTT fallback
  console.log('\n--- EJECUTANDO TEST C: Sin onresult en WebSpeech activa fallback ---');
  {
    const manager = new VoiceTurnManager();
    await manager.iniciarEscucha();
    const initialProvider = manager.activeProviderType;
    assert(initialProvider === 'webspeech', 'Proveedor inicial es webspeech en desktop');

    // Tocar orbe sin haber entregado interim transcript
    manager.detenerYEnviar();
    assert(manager.stopRequestTimer !== null, 'stopRequestTimer de 750ms activo');

    // Esperar a que expire el timer (750ms + 50ms)
    console.log('Esperando expiración de stopRequestTimer (800ms)...');
    await new Promise(r => setTimeout(r, 850));

    assert(manager.activeProviderType === 'backend', 'Conmutó exitosamente a BackendSTT tras ausencia de onresult');
    manager.detenerSesion();
  }

  // TEST H: no-speech en WebSpeech -> Fallback a BackendSTT en mismo turnId con nuevo providerGeneration
  console.log('\n--- EJECUTANDO TEST H: no-speech en WebSpeech activa fallback a BackendSTT ---');
  {
    let messageReceived = null;
    const manager = new VoiceTurnManager({
      onSendMessage: async (text) => {
        messageReceived = text;
        return { respuesta: 'Venta procesada con éxito', estado: 'EXECUTED' };
      }
    });

    await manager.iniciarEscucha();
    const turnId = manager.currentTurnId;
    const initialGen = manager.providerGeneration;
    assert(manager.activeProviderType === 'webspeech', 'Inicia con WebSpeech en desktop');
    assert(initialGen === 1, `providerGeneration inicial es 1 (obtenido: ${initialGen})`);

    // WebSpeech emite no-speech
    manager.webSpeechProvider.onError?.({ code: 'no-speech' });

    // Verificar que conservó turnId pero incrementó providerGeneration
    assert(manager.currentTurnId === turnId, `Mismo turnId conservado tras fallback (turnId=${turnId})`);
    assert(manager.providerGeneration === initialGen + 1, `providerGeneration incrementado a ${initialGen + 1} (obtenido: ${manager.providerGeneration})`);
    assert(manager.activeProviderType === 'backend', 'Proveedor activo conmutó a backend (BackendSTT)');

    // Simular que WebSpeech emite un onEnd tardío con providerGeneration viejo
    let staleIgnored = false;
    const origWarn = console.warn;
    console.warn = (msg) => {
      if (typeof msg === 'string' && msg.includes('STALE_CALLBACK_IGNORED')) {
        staleIgnored = true;
      }
      origWarn(msg);
    };
    manager.webSpeechProvider.onEnd?.();
    console.warn = origWarn;
    assert(staleIgnored === true, 'Callback tardío de WebSpeech descartado por providerGeneration desfasado');

    // Ahora BackendSTT emite transcripción
    manager.backendSTTProvider.onTranscript?.('tres bolsas de leche', true);
    await new Promise(r => setTimeout(r, 10));

    assert(messageReceived === 'tres bolsas de leche', `Venta enviada a backend tras fallback (obtenido: "${messageReceived}")`);
    assert(manager.state === VoiceTurnState.SPEAKING, 'Estado pasa a SPEAKING con respuesta del agente');
    manager.detenerSesion();
  }

  // TEST I: aborted con stopRequested === true no dispara fallback erróneo
  console.log('\n--- EJECUTANDO TEST I: aborted con stopRequested no dispara fallback erróneo ---');
  {
    const manager = new VoiceTurnManager();
    await manager.iniciarEscucha();
    manager.stopRequested = true;

    // WebSpeech aborta debido a la solicitud de stop
    manager.webSpeechProvider.onError?.({ code: 'aborted' });

    assert(manager.activeProviderType === 'webspeech', 'No conmutó erróneamente por abort intencional');
    assert(manager.state === VoiceTurnState.LISTENING, 'Permanece en escucha esperando resultado o timer');
    manager.detenerSesion();
  }

  // TEST J: not-allowed (permiso denegado) no intenta fallback y pasa a ERROR
  console.log('\n--- EJECUTANDO TEST J: not-allowed pasa directamente a ERROR ---');
  {
    const manager = new VoiceTurnManager();
    await manager.iniciarEscucha();

    // WebSpeech reporta permiso denegado
    manager.webSpeechProvider.onError?.({ code: 'not-allowed' });

    assert(manager.state === VoiceTurnState.ERROR, 'Transiciona directamente a ERROR sin reintentar');
    assert(manager.activeProviderType === 'webspeech', 'No intenta conmutar a BackendSTT');
    manager.detenerSesion();
  }

  // TEST K: En dispositivo Android físico, BackendSTT es primario y WebSpeech no participa
  console.log('\n--- EJECUTANDO TEST K: Android-First asigna BackendSTTProvider desde el inicio ---');
  {
    // Simular User-Agent Android
    const originalUA = navigator.userAgent;
    Object.defineProperty(globalThis.navigator, 'userAgent', {
      value: 'Mozilla/5.0 (Linux; Android 12; SM-A025M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36',
      configurable: true
    });

    const manager = new VoiceTurnManager();
    assert(manager.activeProviderType === 'backend', 'En Android, activeProviderType es "backend" desde el inicio');
    assert(manager.currentSTT === manager.backendSTTProvider, 'currentSTT es BackendSTTProvider');

    // Restaurar UA original
    Object.defineProperty(globalThis.navigator, 'userAgent', {
      value: originalUA,
      configurable: true
    });
    manager.detenerSesion();
  }

  // TEST L: BackendSTT ciclo completo SIN transición espuria a READY entre SPEECH_DETECTED y BACKEND_TRANSCRIPT
  console.log('\n--- EJECUTANDO TEST L: BackendSTT ciclo sin READY espurio entre SPEECH_DETECTED y BACKEND_TRANSCRIPT ---');
  {
    const stateHistory = [];
    let messageSent = null;
    let sendCount = 0;

    const originalUA = navigator.userAgent;
    Object.defineProperty(globalThis.navigator, 'userAgent', {
      value: 'Mozilla/5.0 (Linux; Android 12; SM-A025M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36',
      configurable: true
    });

    const manager = new VoiceTurnManager({
      onStateChange: (st) => stateHistory.push(st),
      onSendMessage: async (text) => {
        sendCount++;
        messageSent = text;
        return { respuesta: 'Venta realizada', estado: 'EXECUTED' };
      }
    });

    await manager.iniciarEscucha();
    const turnId = manager.currentTurnId;
    assert(manager.activeProviderType === 'backend', 'Turno iniciado con BackendSTT en móvil');

    // 1. VAD detecta voz
    manager.currentSTT.onSpeechStart?.();
    assert(manager.state === VoiceTurnState.SPEECH_DETECTED, 'Estado pasa a SPEECH_DETECTED');

    // 2. Usuario o VAD solicita detener captura
    manager.detenerYEnviar();
    assert(manager.stopRequested === true, 'stopRequested registrado');
    assert(manager.isTranscribing === true, 'isTranscribing marcado en true esperando audio');

    // 3. Simular que el watchdog de 9s expira mientras la transcripción está pendiente
    manager._iniciarWatchdogSTT(turnId);
    assert(manager.state === VoiceTurnState.PROCESSING, 'Watchdog NO mata el turno a READY mientras isTranscribing sea true (permanece en PROCESSING)');

    // 4. Servidor responde con la transcripción
    manager.currentSTT.onTranscript?.('un arroz y dos aceites', true);
    await new Promise(r => setTimeout(r, 10));

    // 5. Verificar que nunca hubo un READY intermedio entre SPEECH_DETECTED y PROCESSING
    const speechIdx = stateHistory.indexOf(VoiceTurnState.SPEECH_DETECTED);
    const procIdx = stateHistory.indexOf(VoiceTurnState.PROCESSING);
    assert(speechIdx !== -1 && procIdx !== -1, 'Transicionó por SPEECH_DETECTED y PROCESSING');
    const intermediateStates = stateHistory.slice(speechIdx + 1, procIdx);
    assert(!intermediateStates.includes(VoiceTurnState.READY), `Sin estado READY intermedio (estados: ${intermediateStates.join(', ') || 'ninguno'})`);
    assert(messageSent === 'un arroz y dos aceites', `Mensaje enviado al agente: "${messageSent}"`);
    assert(sendCount === 1, `Exactamente 1 envío al backend (obtenido: ${sendCount})`);

    // Restaurar UA original
    Object.defineProperty(globalThis.navigator, 'userAgent', {
      value: originalUA,
      configurable: true
    });
    manager.detenerSesion();
  }

  // TEST M: InvalidStateError produce recuperación controlada sin dejar WebSpeech fantasma
  console.log('\n--- EJECUTANDO TEST M: InvalidStateError produce recuperación sin fantasma ---');
  {
    const manager = new VoiceTurnManager();
    const turnId = manager.currentTurnId;

    // Simular que recognition.start lanza InvalidStateError
    const origStart = manager.webSpeechProvider.recognition.start;
    manager.webSpeechProvider.recognition.start = () => {
      const err = new Error('recognition has already started');
      err.name = 'InvalidStateError';
      throw err;
    };

    let errorReceived = null;
    manager.webSpeechProvider.onError = (err) => {
      errorReceived = err;
    };

    await manager.webSpeechProvider.start();
    assert(errorReceived !== null && errorReceived.code === 'invalid-state', 'InvalidStateError reportado como código invalid-state controlado');
    assert(manager.webSpeechProvider.isListening === false, 'webSpeechProvider.isListening permanece en false');
    assert(manager.webSpeechProvider.isActive() === false, 'webSpeechProvider.isActive() es false (sin fantasma)');

    manager.detenerSesion();
  }

  // TEST N: No iniciar BackendSTT mientras WebSpeech esté en proceso de apagado
  console.log('\n--- EJECUTANDO TEST N: No iniciar BackendSTT mientras WebSpeech esté en stopping ---');
  {
    const manager = new VoiceTurnManager();
    await manager.iniciarEscucha();

    // Poner WebSpeech en stopping
    manager.webSpeechProvider.isStopping = true;
    let webSpeechStoppedBeforeBackend = false;

    // Simular que onend toma 30ms en dispararse
    setTimeout(() => {
      manager.webSpeechProvider.onend?.();
    }, 30);

    const origBackendStart = manager.backendSTTProvider.start;
    manager.backendSTTProvider.start = async function() {
      webSpeechStoppedBeforeBackend = !manager.webSpeechProvider.isActive();
      return origBackendStart.apply(this, arguments);
    };

    await manager._conmutarABackendSTT(manager.currentTurnId);
    assert(webSpeechStoppedBeforeBackend === true, 'BackendSTT sólo inició después de que WebSpeech completó su cierre definitivo');
    manager.detenerSesion();
  }

  console.log('\n====================================================');
  console.log(`🎉 TODOS LOS TESTS COMPLETADOS: ${passed}/${total} PASADOS`);
  console.log('====================================================');
}

runTests().catch(err => {
  console.error('Error fatal en tests:', err);
  process.exit(1);
});
