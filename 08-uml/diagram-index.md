# 08 — Diagram Index

## Diagrams

| Diagram | Level / Type | Source file | Kept current by |
|---|---|---|---|
| System Context | C4 Context | [`diagrams/source/c4-context.mmd`](./diagrams/source/c4-context.mmd) | Pull request adding/removing external APIs |
| Single Deployable | C4 Container | [`diagrams/source/c4-container.mmd`](./diagrams/source/c4-container.mmd) | Pull request changing deployment topology |
| POS Atomic Checkout | Sequence Diagram | [`diagrams/source/sequence-pos-checkout.mmd`](./diagrams/source/sequence-pos-checkout.mmd) | Pull request changing `pos_ventas` checkout logic |
| In-App Voice AI Turn | Sequence Diagram | [`diagrams/source/sequence-voice-turn.mmd`](./diagrams/source/sequence-voice-turn.mmd) | Pull request changing `agente_ia` FSM or STT |

## What each diagram answers

| Diagram | Question answered | Elements drawn |
|---|---|---|
| Context | Who uses the system, and what external services are called? | Tenderos, Cajeros, SuperAdmin, Groq Whisper, Google Gemini, Vercel/Render |
| Container | What runtime containers execute the single deployable? | React 19 SPA, FastAPI Backend process, PostgreSQL 16 DB, Redis Cache |
| POS Checkout | How does the system guarantee zero overselling under race conditions? | Cart, `InventarioFacade`, `SELECT ... FOR UPDATE`, snapshot write, commit |
| Voice Turn | How does an audio snippet turn into an idempotent business action? | `VoiceTurnManager`, Whisper STT, FSM intent, `AgentCommand`, Facade execution |

## Where the model stops

This system has one container process, described in [`../05-architecture/modular-monolith.md`](../05-architecture/modular-monolith.md).
C4 goes no deeper than component: internal functions are protected by `import-linter`
and covered by unit tests.

---

**Related:** [`./README.md`](./README.md) · [`../05-architecture/modular-monolith.md`](../05-architecture/modular-monolith.md)
