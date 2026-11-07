# agente-ia — Runbook

## Symptoms this module can cause

| Symptom | Likely cause inside this module |
|---|---|
| Audio transcription returns empty text | Audio file size under 100 bytes or invalid WebM codec |
| 503 Service Unavailable on message | Groq / Gemini API key invalid, quota exceeded, or network outage |
| Voice turn repeats previous action | Frontend reusing stale `command_id` on new requests |

## Diagnosis

| Step | How |
|---|---|
| Isolate logs | Filter structured logs for `module: "agente_ia"` or `[VOICE-STT]` tags |
| Test STT provider | Run `pytest tests/test_llm_provider_smoke.py` |
| Check command history | Query `SELECT command_id, action, status, executed_at FROM agent_commands ORDER BY created_at DESC LIMIT 10` |

## Recovery

| Situation | Action |
|---|---|
| Groq outage | Switch provider to Gemini via server env `AI_PROVIDER=gemini` |
| Stuck command | SuperAdmin updates `status = 'INVALIDADO'` in `agent_commands` |

---

**Related:** [`./README.md`](./README.md) · [`../../13-operations/README.md`](../../13-operations/README.md)
