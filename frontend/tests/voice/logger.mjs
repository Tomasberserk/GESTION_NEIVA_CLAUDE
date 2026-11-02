// Logger relay para el harness: captura eventos del FSM sin ensuciar la salida.
export const events = []

export function setLogger() {
  console.warn = (...args) => {
    events.push(`WARN:${String(args[0])}`)
  }
  console.log = (...args) => {
    events.push(`LOG:${String(args[0])}`)
  }
}
