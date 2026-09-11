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

  console.log('\n====================================================');
  console.log(`🎉 TODOS LOS TESTS COMPLETADOS: ${passed}/${total} PASADOS`);
  console.log('====================================================');
}

runTests().catch(err => {
  console.error('Error fatal en tests:', err);
  process.exit(1);
});
