# agente-ia — Module Overview

## Purpose

The `agente_ia` module provides an in-app multi-modal conversational assistant.
It processes voice audio via Groq Whisper STT, resolves business intents through LLMs,
orchestrates conversational Finite State Machines (FSM), and records idempotent commands.

## Public API

| Method | Input | Output | Called by |
|---|---|---|---|
| `AgenteIaFacade.procesar_mensaje` | `conversation_id: str, mensaje: str, user: UsuarioDTO` | `AgenteRespuestaDTO` | Presentation router |
| `AgenteIaFacade.transcribir_audio` | `audio_bytes: bytes, content_type: str` | `str` | Presentation router |

## Dependencies

| Depends on | Through | Why |
|---|---|---|
| `inventario` | `InventarioFacade.reabastecer_stock()` | Executes restock commands from natural language |
| `pos_ventas` | `VentasFacade.obtener_resumen_diario()` | Answers questions about today's revenue and sales |
| `auth_tenancy` | `AuthTenancyFacade.verificar_acceso_pro()` | Verifies tenant has Pro/Premium plan enabled per **BR-09** |

---

**Related:** [`./data-model.md`](./data-model.md) · [`./runbook.md`](./runbook.md) · [`../module-catalog.md`](../module-catalog.md)
