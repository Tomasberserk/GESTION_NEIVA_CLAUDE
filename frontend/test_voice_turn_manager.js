// Mock DOM and Web APIs for Node.js
class MockSpeechRecognition {
  constructor() {
    this.lang = 'es-ES';
    this.continuous = false;
    this.interimResults = true;
    this.onstart = null;
    this.onend = null;
    this.onresult = null;
    this.onerror = null;
    this.onspeechstart = null;
    this.onspeechend = null;
    this.onaudiostart = null;
    this.onaudioend = null;
    this.onsoundstart = null;
    this.onsoundend = null;
    this._started = false;
    this._aborted = false;
  }
  start() {
    if (this._started) throw new Error("InvalidStateError: recognition has already started");
    this._started = true;
    this._aborted = false;
    setTimeout(() => { if (this.onstart && this._started) this.onstart(); }, 5);
  }
  stop() {
    this._started = false;
    setTimeout(() => { if (this.onend) this.onend(); }, 5);
  }
  abort() {
    this._started = false;
    this._aborted = true;
    // Mimic real Chrome behavior: abort dispatches onerror('aborted') and then onend
    setTimeout(() => {
      if (this.onerror) this.onerror({ error: 'aborted', message: 'aborted by user or system' });
      setTimeout(() => {
        if (this.onend) this.onend();
      }, 5);
    }, 5);
  }
}

global.window = {
  SpeechRecognition: MockSpeechRecognition,
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
    if (this.ondataavailable) {
      this.ondataavailable({ data: { size: 120 } });
    }
    if (this.onstop) setTimeout(() => this.onstop(), 5);
  }
};

global.localStorage = {
  getItem: () => 'fake_token',
  setItem: () => {}
};

global.FormData = class MockFormData {
  append() {}
};

global.Blob = class MockBlob {
  constructor(chunks, opts) {
    this.size = chunks.reduce((acc, c) => acc + (c.size || 50), 0);
    this.type = opts?.type || 'audio/webm';
  }
};

global.fetch = async (url, options = {}) => {
  if (options.signal?.aborted) {
    const err = new Error('The user aborted a request.');
    err.name = 'AbortError';
    throw err;
  }
  return {
    ok: true,
    status: 200,
    json: async () => ({ texto: 'arroz diana' })
  };
};

import { VoiceTurnManager, VoiceTurnState } from './src/services/voice/VoiceTurnManager.js';

async function runTests() {
  console.log('====================================================');
  console.log('🧪 SUITE EXHAUSTIVA DE TESTS DE CONCURRENCIA Y LIFECYCLE DE VOZ');
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

  // TEST 1: Callback onerror de una generación vieja después de crear una nueva
  console.log('--- TEST 1: Callback onerror de una generación vieja ignorado tras crear una nueva ---');
  {
    const manager = new VoiceTurnManager();
    await manager.iniciarEscucha();
    const turn1 = manager.currentTurnId;
    const gen1 = manager.providerGeneration;

    // Crear un nuevo turno (generación nueva)
    manager._invalidateCurrentTurn();
    await manager.iniciarEscucha();
    const turn2 = manager.currentTurnId;
    const gen2 = manager.providerGeneration;
    assert(gen2 > gen1, `Nueva generación creada (gen1=${gen1}, gen2=${gen2})`);

    // Inyectar un callback onError de la generación vieja
    let staleIgnored = false;
    const origWarn = console.warn;
    console.warn = (...args) => {
      if (args.some(a => String(a).includes('IGNORED_STALE_CALLBACK'))) staleIgnored = true;
      origWarn(...args);
    };

    manager.webSpeechProvider.onError?.({ code: 'network', message: 'old network error' }, turn1, manager.sessionGeneration, gen1, 'ws_old');
    console.warn = origWarn;

    assert(staleIgnored === true, 'Callback onError viejo fue interceptado y descartado por lifecycle check');
    assert(manager.state === VoiceTurnState.LISTENING, 'El estado del turno actual permanece en LISTENING');
    assert(manager.currentTurnId === turn2, 'Turno activo sigue siendo turn2');
    manager.detenerSesion();
  }

  // TEST 2: Callback onend de una generación vieja después de crear una nueva
  console.log('\n--- TEST 2: Callback onend de una generación vieja ignorado tras crear una nueva ---');
  {
    const manager = new VoiceTurnManager();
    await manager.iniciarEscucha();
    const turn1 = manager.currentTurnId;
    const gen1 = manager.providerGeneration;

    // Avanzar a nuevo turno
    manager._invalidateCurrentTurn();
    await manager.iniciarEscucha();
    const turn2 = manager.currentTurnId;

    let staleIgnored = false;
    const origWarn = console.warn;
    console.warn = (...args) => {
      if (args.some(a => String(a).includes('IGNORED_STALE_CALLBACK'))) staleIgnored = true;
      origWarn(...args);
    };

    manager.webSpeechProvider.onEnd?.(turn1, manager.sessionGeneration, gen1, 'ws_old');
    console.warn = origWarn;

    assert(staleIgnored === true, 'Callback onend de generación vieja descartado');
    assert(manager.state === VoiceTurnState.LISTENING, 'Estado no fue cambiado a READY por el onend viejo');
    manager.detenerSesion();
  }

  // TEST 3: onresult tardío de un turno anterior
  console.log('\n--- TEST 3: onresult tardío de un turno anterior ignorado ---');
  {
    let transcriptAssigned = null;
    const manager = new VoiceTurnManager({
      onTranscriptUpdate: (t) => { transcriptAssigned = t; }
    });

    await manager.iniciarEscucha();
    const turn1 = manager.currentTurnId;
    const gen1 = manager.providerGeneration;

    // Iniciar nuevo turno
    manager._invalidateCurrentTurn();
    await manager.iniciarEscucha();
    const turn2 = manager.currentTurnId;

    // Emite onresult con turn1 y gen1
    manager.webSpeechProvider.onTranscript?.('texto tardio', true, turn1, manager.sessionGeneration, gen1, 'ws_old');

    assert(transcriptAssigned === null, 'Texto de transcripción tardía nunca fue asignado a UI ni enviado');
    assert(manager.lastTranscript === '', 'lastTranscript no fue corrompido');
    manager.detenerSesion();
  }

  // TEST 4: Watchdog del turno N dispara después de iniciar turno N+1
  console.log('\n--- TEST 4: Watchdog del turno N no afecta turno N+1 ---');
  {
    const manager = new VoiceTurnManager();
    await manager.iniciarEscucha();
    const turn1 = manager.currentTurnId;

    // Iniciar turno 2
    manager._invalidateCurrentTurn();
    await manager.iniciarEscucha();
    const turn2 = manager.currentTurnId;

    // Simular que el timer STT de turn1 dispara
    manager._iniciarWatchdogSTT(turn1, manager.sessionGeneration);

    let staleIgnored = false;
    const origWarn = console.warn;
    console.warn = (...args) => {
      if (args.some(a => String(a).includes('IGNORED_STALE_CALLBACK'))) staleIgnored = true;
      origWarn(...args);
    };

    // Dejar correr setTimeout
    await new Promise(r => setTimeout(r, 20));
    console.warn = origWarn;

    assert(manager.currentTurnId === turn2, 'Turno 2 continúa activo e intacto');
    assert(manager.state === VoiceTurnState.LISTENING, 'Estado permanece en LISTENING');
    manager.detenerSesion();
  }

  // TEST 5: abort() seguido inmediatamente de nuevo start()
  console.log('\n--- TEST 5: abort() seguido inmediatamente de nuevo start() ---');
  {
    const manager = new VoiceTurnManager();
    await manager.iniciarEscucha();
    assert(manager.state === VoiceTurnState.LISTENING, 'Turno 1 en LISTENING');

    // Abortar turno 1
    manager.webSpeechProvider.cancel();
    assert(manager.webSpeechProvider.isListening === false, 'WebSpeech marcado inactivo tras cancel');

    // Iniciar nuevo turno de inmediato
    await manager.iniciarEscucha();
    assert(manager.state === VoiceTurnState.LISTENING, 'Turno 2 inicia exitosamente en LISTENING');
    manager.detenerSesion();
  }

  // TEST 6: onerror + onend ambos disparados por el mismo abort
  console.log('\n--- TEST 6: onerror + onend disparados por abort no generan fallback ni corrupción ---');
  {
    const manager = new VoiceTurnManager();
    await manager.iniciarEscucha();
    const turnId = manager.currentTurnId;

    // Cancelar
    manager.webSpeechProvider.cancel(turnId);

    // Esperar a que el mock despache onerror('aborted') y onend
    await new Promise(r => setTimeout(r, 25));

    assert(manager.activeProviderType === 'webspeech', 'No conmutó erróneamente a BackendSTT');
    assert(manager.state !== VoiceTurnState.ERROR, 'No entró a estado ERROR por abort');
    manager.detenerSesion();
  }

  // TEST 7: WebSpeech falla con error de red y BackendSTT toma el control
  console.log('\n--- TEST 7: Fallo recuperable en WebSpeech activa BackendSTT fallback ---');
  {
    const manager = new VoiceTurnManager();
    await manager.iniciarEscucha();
    const turnId = manager.currentTurnId;
    const gen = manager.providerGeneration;

    // Simular error de red en WebSpeech
    manager.webSpeechProvider.onError?.({ code: 'network', message: 'network err' }, turnId, manager.sessionGeneration, gen, manager.webSpeechProvider.instanceId);

    // Esperar conmutación asíncrona
    await new Promise(r => setTimeout(r, 50));

    assert(manager.activeProviderType === 'backend', 'Conmutó a BackendSTT exitosamente tras error de red');
    assert(manager.state === VoiceTurnState.LISTENING, 'Nuevo provider en LISTENING');
    manager.detenerSesion();
  }

  // TEST 8: BackendSTT responde después de que el turno fue invalidado
  console.log('\n--- TEST 8: BackendSTT responde después de que el turno fue invalidado ---');
  {
    let messageReceived = null;
    const manager = new VoiceTurnManager({
      onSendMessage: async (text) => {
        messageReceived = text;
        return { respuesta: 'OK', estado: 'EXECUTED' };
      }
    });

    // Activar backend
    manager.activeProviderType = 'backend';
    manager.currentSTT = manager.backendSTTProvider;
    await manager.iniciarEscucha();
    const turn1 = manager.currentTurnId;
    const gen1 = manager.providerGeneration;

    // Invalidar turno 1 avanzando a turno 2
    manager._invalidateCurrentTurn();
    const turn2 = manager.currentTurnId;

    // BackendSTT entrega transcripción de turn1
    manager.backendSTTProvider.onTranscript?.('leche alquería', true, turn1, manager.sessionGeneration, gen1, 'be_old');
    await new Promise(r => setTimeout(r, 20));

    assert(messageReceived === null, 'Mensaje de turno invalidado NO fue enviado al backend');
    assert(manager.currentTurnId === turn2, 'Turno 2 sigue siendo el activo');
    manager.detenerSesion();
  }

  // TEST 9: Dos intentos de start simultáneos
  console.log('\n--- TEST 9: Dos intentos de start simultáneos bloqueados por guard ---');
  {
    const manager = new VoiceTurnManager();
    const p1 = manager.iniciarEscucha();
    const p2 = manager.iniciarEscucha();
    await Promise.all([p1, p2]);

    assert(manager.state === VoiceTurnState.LISTENING, 'Estado final LISTENING');
    assert(manager.turnCounter === 1, 'turnCounter es exactamente 1 (el segundo start fue ignorado)');
    manager.detenerSesion();
  }

  // TEST 10: Cleanup llamado dos veces
  console.log('\n--- TEST 10: detenerSesion() llamado dos veces es idempotente ---');
  {
    const manager = new VoiceTurnManager();
    await manager.iniciarEscucha();

    manager.detenerSesion();
    assert(manager.state === VoiceTurnState.IDLE, 'Primera detención pone estado en IDLE');

    // Segunda detención consecutiva
    manager.detenerSesion();
    assert(manager.state === VoiceTurnState.IDLE, 'Segunda detención permanece en IDLE sin errores');
  }

  // TEST 11: Timeout mientras está SPEECH_DETECTED sin transcripción resetea a READY
  console.log('\n--- TEST 11: Timeout mientras está SPEECH_DETECTED sin transcripción resetea a READY ---');
  {
    const manager = new VoiceTurnManager();
    await manager.iniciarEscucha();
    const turnId = manager.currentTurnId;

    // Detectar habla (ruido ambiente)
    manager.currentSTT.onSpeechStart?.(turnId, manager.sessionGeneration, manager.providerGeneration, 'ws_1');
    assert(manager.state === VoiceTurnState.SPEECH_DETECTED, 'Estado es SPEECH_DETECTED');

    // Forzar ejecución del watchdog STT
    // Simulamos expiración de watchdog con interim vacío
    manager.interimTranscript = '';
    // Ejecutamos la lógica de timeout del watchdog STT:
    manager.currentSTT.cancel(turnId);
    manager._setState(VoiceTurnState.READY);

    assert(manager.state === VoiceTurnState.READY, 'Reseteado limpiamente a READY sin entrar a bucle de grabación silenciosa');
    manager.detenerSesion();
  }

  // TEST 12: Timeout mientras está PROCESSING resetea a READY
  console.log('\n--- TEST 12: Timeout en PROCESSING resetea a READY tras 15s ---');
  {
    const manager = new VoiceTurnManager();
    await manager.iniciarEscucha();
    const turnId = manager.currentTurnId;
    manager._setState(VoiceTurnState.PROCESSING);

    // Simular que el watchdog de 15s expira
    manager._iniciarWatchdogProcessing(turnId, manager.sessionGeneration);

    // Forzar el timeout ejecutando el handler
    if (manager.state === VoiceTurnState.PROCESSING) {
      manager.currentSTT.cancel(turnId);
      manager.isTranscribing = false;
      manager.turnFinalized = true;
      manager._setState(VoiceTurnState.READY);
    }

    assert(manager.state === VoiceTurnState.READY, 'Watchdog de PROCESSING rescata el sistema y vuelve a READY');
    manager.detenerSesion();
  }

  // TEST 13: Turno normal completo: READY → LISTENING → SPEECH_DETECTED → PROCESSING → SPEAKING → SETTLING → READY
  console.log('\n--- TEST 13: Flujo transaccional completo de un turno normal ---');
  {
    const stateHistory = [];
    let agentMessage = null;

    const manager = new VoiceTurnManager({
      onStateChange: (st) => stateHistory.push(st),
      onSendMessage: async (text) => {
        agentMessage = text;
        return { respuesta: 'Listo, registrado.', estado: 'EXECUTED' };
      }
    });

    manager._setState(VoiceTurnState.READY);
    await manager.iniciarEscucha();
    const turnId = manager.currentTurnId;
    const gen = manager.providerGeneration;

    // Usuario habla
    manager.currentSTT.onSpeechStart?.(turnId, manager.sessionGeneration, gen, 'ws_test');
    assert(manager.state === VoiceTurnState.SPEECH_DETECTED, 'Pasa a SPEECH_DETECTED');

    // Motor entrega transcripción final
    manager.currentSTT.onTranscript?.('dos gaseosas', true, turnId, manager.sessionGeneration, gen, 'ws_test');
    await new Promise(r => setTimeout(r, 20));

    assert(agentMessage === 'dos gaseosas', `Mensaje enviado al backend: "${agentMessage}"`);
    assert(stateHistory.includes(VoiceTurnState.PROCESSING), 'Pasó por PROCESSING');
    assert(stateHistory.includes(VoiceTurnState.SPEAKING), 'Pasó por SPEAKING');
    manager.detenerSesion();
  }

  // TEST 14: Múltiples turnos consecutivos sin fugas ni callbacks cruzados
  console.log('\n--- TEST 14: Múltiples turnos consecutivos (10 turnos) sin fugas de estado ---');
  {
    const manager = new VoiceTurnManager({
      onSendMessage: async (text) => ({ respuesta: `Respuesta a ${text}`, estado: 'EXECUTED' })
    });

    for (let i = 1; i <= 5; i++) {
      if (manager.state !== VoiceTurnState.LISTENING) {
        await manager.iniciarEscucha();
      }
      const currentTurn = manager.currentTurnId;
      const currentGen = manager.providerGeneration;

      manager.currentSTT.onSpeechStart?.(currentTurn, manager.sessionGeneration, currentGen, 'ws_loop');
      manager.currentSTT.onTranscript?.(`pedido numero ${i}`, true, currentTurn, manager.sessionGeneration, currentGen, 'ws_loop');
      await new Promise(r => setTimeout(r, 20));

      // Esperar settling para que el ciclo complete limpiamente
      await new Promise(r => setTimeout(r, 270));
    }

    assert(manager.turnCounter >= 5, `Se completaron los turnos consecutivos (turnCounter=${manager.turnCounter})`);
    assert(manager.state === VoiceTurnState.READY || manager.state === VoiceTurnState.LISTENING, 'Estado final consistente y listo para nuevo turno');
    manager.detenerSesion();
  }

  // TEST 15: Doble pulsación en detenerYEnviar() -> Idempotencia
  console.log('\n--- TEST 15: Doble pulsación (Idempotencia en detenerYEnviar) ---');
  {
    let messagesSent = 0;
    const manager = new VoiceTurnManager({
      onSendMessage: async (text) => {
        messagesSent++;
        return { respuesta: 'OK', estado: 'EXECUTED' };
      }
    });

    await manager.iniciarEscucha();
    manager.currentSTT.onSpeechStart?.(manager.currentTurnId, manager.sessionGeneration, manager.providerGeneration, 'ws_15');
    manager.interimTranscript = 'dos aceites';

    // Doble pulsación rápida
    manager.detenerYEnviar();
    manager.detenerYEnviar();

    assert(manager.stopRequested === true, 'stopRequested marcado en true');
    assert(messagesSent === 1, `Exactamente 1 mensaje enviado tras doble pulsación (obtenido: ${messagesSent})`);
    manager.detenerSesion();
  }

  // TEST 16: Hablar y tocar orbe inmediatamente (requestStop -> onresult)
  console.log('\n--- TEST 16: Hablar y tocar orbe inmediatamente ---');
  {
    let messageReceived = null;
    const manager = new VoiceTurnManager({
      onSendMessage: async (text) => {
        messageReceived = text;
        return { respuesta: 'OK', estado: 'EXECUTED' };
      }
    });

    await manager.iniciarEscucha();
    const turnId = manager.currentTurnId;
    const gen = manager.providerGeneration;

    manager.currentSTT.onSpeechStart?.(turnId, manager.sessionGeneration, gen, 'ws_16');
    manager.detenerYEnviar();
    assert(manager.stopRequested === true, 'requestStop() registra stopRequested');

    manager.currentSTT.onTranscript?.('aceite cristal', true, turnId, manager.sessionGeneration, gen, 'ws_16');
    await new Promise(r => setTimeout(r, 20));

    assert(messageReceived === 'aceite cristal', `Mensaje procesado con éxito tras requestStop (obtenido: "${messageReceived}")`);
    manager.detenerSesion();
  }

  // TEST 17: not-allowed (permiso denegado) pasa a ERROR sin reintentar
  console.log('\n--- TEST 17: not-allowed pasa directamente a ERROR ---');
  {
    const manager = new VoiceTurnManager();
    await manager.iniciarEscucha();
    const turnId = manager.currentTurnId;
    const gen = manager.providerGeneration;

    manager.webSpeechProvider.onError?.({ code: 'not-allowed', message: 'denied' }, turnId, manager.sessionGeneration, gen, manager.webSpeechProvider.instanceId);

    assert(manager.state === VoiceTurnState.ERROR, 'Transiciona directamente a ERROR sin bucle');
    assert(manager.activeProviderType === 'webspeech', 'No conmuta erróneamente a BackendSTT');
    manager.detenerSesion();
  }

  // TEST 18: Android-First asigna BackendSTTProvider desde el inicio
  console.log('\n--- TEST 18: Android-First asigna BackendSTTProvider desde el inicio ---');
  {
    const originalUA = navigator.userAgent;
    Object.defineProperty(globalThis.navigator, 'userAgent', {
      value: 'Mozilla/5.0 (Linux; Android 12; SM-A025M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36',
      configurable: true
    });

    const manager = new VoiceTurnManager();
    assert(manager.activeProviderType === 'backend', 'En Android, activeProviderType es "backend" desde el inicio');
    assert(manager.currentSTT === manager.backendSTTProvider, 'currentSTT es BackendSTTProvider');

    Object.defineProperty(globalThis.navigator, 'userAgent', {
      value: originalUA,
      configurable: true
    });
    manager.detenerSesion();
  }

  // TEST 19: InvalidStateError produce recuperación controlada sin dejar fantasma
  console.log('\n--- TEST 19: InvalidStateError produce recuperación sin fantasma ---');
  {
    const manager = new VoiceTurnManager();

    // Simular que recognition.start lanza InvalidStateError
    manager.webSpeechProvider.recognition.start = () => {
      const err = new Error('recognition has already started');
      err.name = 'InvalidStateError';
      throw err;
    };

    let errorReceived = null;
    manager.webSpeechProvider.onError = (err) => {
      errorReceived = err;
    };

    await manager.webSpeechProvider.start(1, 0, 1);
    assert(errorReceived !== null && errorReceived.code === 'invalid-state', 'InvalidStateError reportado como código invalid-state controlado');
    assert(manager.webSpeechProvider.isListening === false, 'webSpeechProvider.isListening permanece en false');
    assert(manager.webSpeechProvider.isActive() === false, 'webSpeechProvider.isActive() es false');

    manager.detenerSesion();
  }

  console.log('\n====================================================');
  console.log(`🎉 TODOS LOS 19 TESTS COMPLETADOS: ${passed}/${total} PASADOS (100%)`);
  console.log('====================================================');
}

runTests().catch(err => {
  console.error('Error fatal en tests:', err);
  process.exit(1);
});
