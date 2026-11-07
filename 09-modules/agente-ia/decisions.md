# agente-ia — Decisions

## [DEC-01] Whisper Cloud for Low-Latency STT

| Field | Value |
|---|---|
| Date | 2026-10-18 |
| Status | Active |

**Context:** Mobile phone web browsers have poor local speech-to-text accuracy with Colombian accents.

**Decision:** Audio is sent to Groq Cloud Whisper Large v3 (latency ~150ms) with Gemini Flash fallback.

**Global ADR:** none — internal to `agente_ia`

## [DEC-02] State Machine with Redis Session Store

| Field | Value |
|---|---|
| Date | 2026-10-20 |
| Status | Active |

**Context:** Multi-turn interactions (e.g. asking for missing product price) require transient context.

**Decision:** The conversational Finite State Machine (FSM) stores session turns in Redis with a 15-minute TTL.

**Global ADR:** none — internal to `agente_ia`

---

**Related:** [`./README.md`](./README.md) · [`../../05-architecture/decisions/README.md`](../../05-architecture/decisions/README.md)
