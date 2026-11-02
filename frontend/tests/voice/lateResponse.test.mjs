/**
 * Regresión del FSM del Modo Voz — "acá no me vuelve nada" (02-11-2026).
 *
 * Corre con: npm run test:voice
 * Empaqueta VoiceTurnManager.js con esbuild (el .cache/ está gitignored) y
 * ejercita el ciclo real de turnos SIN navegador, con STT stub.
 *
 *   T1  Respuesta tardía (llega tras el watchdog) → SE ENTREGA y se habla.
 *   T2  Respuesta tardía con turno invalidado → se descarta (stale).
 *   T3  Respuesta normal (antes del watchdog) → se entrega.
 *   T4  Envío manual dentro de la ventana tardía → la vieja se tira (seq),
 *       la del envío manual se entrega.
 */
import assert from 'node:assert'
import { VoiceTurnManager } from './.cache/vtm.mjs'
import { setLogger, events } from './logger.mjs'

const WATCHDOG_MS = 60

setLogger()

/** Crea un manager con STT stub muy mínimo pero suficiente para el ciclo de turnos. */
function makeManager(onSendMessage) {
  const m = new VoiceTurnManager({
    onStateChange: (s) => events.push(`STATE:${s}`),
    onAgentResponse: (r) => events.push(`AGENT:${JSON.stringify(r)}`),
    onSendMessage,
  })
  m.processingWatchdogMs = WATCHDOG_MS
  m.currentSTT = {
    generation: m.providerGeneration,
    cancel: (t) => events.push(`STT-CANCEL:${t}`),
    stop: (t) => events.push(`STT-STOP:${t}`),
    start: async () => {},
    isActive: () => false,
    isStarting: false,
    isListening: false,
  }
  m.turnCounter = 1
  m.currentTurnId = 1
  return m
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

async function t1_respuesta_tardia_se_entrega() {
  events.length = 0
  let resolveSend
  const m = makeManager(
    () =>
      new Promise((res) => {
        resolveSend = res
      })
  )
  m._finalizarTurnoVocal('hoy vendí dos coca-colas', 1, m.sessionGeneration)
  await sleep(WATCHDOG_MS + 40) // watchdog vence → READY + ventana tardía
  assert.equal(m.state, 'READY', 'T1 a: tras watchdog debe volver a READY')
  assert.ok(m.pendingLateResponse, 'T1 b: ventana tardía abierta')

  resolveSend({ estado: 'EXECUTED', respuesta: 'Venta registrada: 2 Coca-Colas' })
  await sleep(30)

  assert.ok(
    events.includes('AGENT:{"estado":"EXECUTED","respuesta":"Venta registrada: 2 Coca-Colas"}'),
    `T1 c: respuesta debe entregarse. events=${events.join(' | ')}`
  )
  assert.equal(m.pendingLateResponse, null, 'T1 d: ventana cerrada tras entrega')
  assert.ok(
    events.some((e) => e.startsWith('STATE:SPEAKING')),
    `T1 e: debe pasar a SPEAKING. events=${events.join(' | ')}`
  )
}

async function t2_turno_nuevo_descarta() {
  events.length = 0
  let resolveSend
  const m = makeManager(
    () =>
      new Promise((res) => {
        resolveSend = res
      })
  )
  m._finalizarTurnoVocal('pregunta vieja', 1, m.sessionGeneration)
  await sleep(WATCHDOG_MS + 40) // ventana tardía abierta
  assert.ok(m.pendingLateResponse, 'T2 a: ventana abierta')

  m._invalidateCurrentTurn() // turno nuevo (dueño toca el orbe)
  assert.equal(m.pendingLateResponse, null, 'T2 b: ventana cerrada al invalidar')

  resolveSend({ estado: 'EXECUTED', respuesta: 'respuesta de un turno viejo' })
  await sleep(30)

  assert.ok(
    !events.some((e) => e.startsWith('AGENT:')),
    `T2 c: NO debe entregar respuestas de turnos invalidados. events=${events.join(' | ')}`
  )
}

async function t3_respuesta_normal() {
  events.length = 0
  const m = makeManager(async () => ({ estado: 'IDLE', respuesta: 'Listo, ¿qué más?' }))
  await m.enviarMensajeManual('hola')
  assert.ok(
    events.some((e) => e.includes('"estado":"IDLE"')),
    `T3 a: entrega normal. events=${events.join(' | ')}`
  )
  assert.ok(['SPEAKING', 'SETTLING', 'READY'].includes(m.state), `T3 b: estado avanzó (=${m.state})`)
}

async function t4_manual_en_ventana_tardia() {
  events.length = 0
  const resolvers = []
  const m = makeManager(
    () =>
      new Promise((res) => {
        resolvers.push(res)
      })
  )
  m._finalizarTurnoVocal('primero', 1, m.sessionGeneration)
  await sleep(WATCHDOG_MS + 40) // ventana tardía abierta, primer send aún pendiente
  assert.ok(m.pendingLateResponse, 'T4 a: ventana abierta')

  // OJO: sin await — el envío manual queda pendiente hasta que resolvamos su promesa.
  m.enviarMensajeManual('sí, dale')
  await sleep(20) // deja que el envío manual llegue a su await
  resolvers[0]({ estado: 'EXECUTED', respuesta: 'LA TARDÍA VIEJA' })
  await sleep(30)
  assert.ok(
    !events.some((e) => e.includes('LA TARDÍA VIEJA')),
    `T4 b: la respuesta vieja NO debe hablarse. events=${events.join(' | ')}`
  )

  resolvers[1]({ estado: 'READY_TO_CONFIRM', respuesta: '¿Confirmas la venta?' })
  await sleep(30)
  assert.ok(
    events.some((e) => e.includes('¿Confirmas la venta?')),
    `T4 c: la respuesta del envío manual SÍ se entrega. events=${events.join(' | ')}`
  )
}

;(async () => {
  let passed = 0
  const tryIt = async (name, fn) => {
    await fn()
    passed++
    process.stdout.write(`${name} ✅\n`)
  }
  await tryIt('T1 respuesta tardía entregada y hablada', t1_respuesta_tardia_se_entrega)
  await tryIt('T2 turno nuevo descarta tardía vieja', t2_turno_nuevo_descarta)
  await tryIt('T3 flujo normal intacto', t3_respuesta_normal)
  await tryIt('T4 manual en ventana tardía (seq)', t4_manual_en_ventana_tardia)
  process.stdout.write(`\n${passed}/4 ✅ FSM del Modo Voz verificado\n`)
  // Windows: process.exit() inmediato trunca el pipe de stdout. Damos un tick
  // para que drene antes de forzar la salida (los timers del STT quedan vivos).
  process.exitCode = 0
  setTimeout(() => process.exit(0), 250)
})().catch((e) => {
  console.error('\n❌ FALLA:', e.message)
  console.error('events:', events.join(' | '))
  process.exit(1)
})
