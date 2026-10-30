# Viabilidad del Modo Voz en producción (análisis 28-10)

> Documento de decisión. Autor: Gemini/Antigravity. Estado: **propuesta**, pendiente de validación por Claude y el dueño.

## Veredicto

**Sí es viable y sostenible**, siempre que se cumplan cuatro condiciones operativas (ver más abajo). El costo de IA por tienda es marginal. El riesgo real está en la operación: cuotas compartidas, límites de concurrencia y la fiabilidad de la UI en navegadores reales.

## Cómo está construido hoy (verificado en el código)

| Pieza | Dónde corre | Costo | Evidencia |
|---|---|---|---|
| Voz → texto en escritorio | Navegador (Web Speech API) | 0 | `VoiceTurnManager.js:64-71` |
| Voz → texto en móvil | Backend: Groq Whisper `whisper-large-v3`; si falla, Gemini | Por minuto de audio | `app/routers/agente.py:106-143` |
| Entender la intención | **Primero un parser determinístico (sin IA)**. Solo si no entiende, LLM (Groq `gpt-oss-120b` o Gemini), con fallback cruzado | Solo las frases que el parser no resuelve | `intent_provider.py:1131-1199` |
| Ejecutar venta o stock | Backend, por reglas: "el LLM no ejecuta, no calcula, no decide el tenant" | 0 | `agent_orchestrator.py:4-6` |
| Redactar la respuesta | Plantillas fijas, sin LLM | 0 | `response_formatter.py:3` |
| Texto → voz | Navegador (speechSynthesis) | 0 | `services/voice/tts/` |
| Credenciales | Solo en el backend (`.env` del servidor), nunca en el frontend | — | `os.getenv` en el backend |
| Acceso | Solo con plan Pro o trial (`require_pro_entitlement`) | — | `agente.py:52,86` |

Credenciales locales (verificado el 28-10): `GOOGLE_API_KEY` = `GEMINI_API_KEY` (la misma key). **Es válida** y `gemini-3.6-flash` responde. Un primer intento devolvió **503** (sobrecarga transitoria), lo que muestra que el fallback es necesario. `GROQ_API_KEY` **no está** en el `.env` local, así que localmente todo pasa por Gemini (`get_intent_provider`, línea 1209).

## Costo estimado (orden de magnitud; verificar precios vigentes)

Supuesto pesimista por tienda: 100 comandos de voz al día, unos 4 s de audio cada uno, y un 30 % de frases que necesitan LLM (unos 1.500 tokens por llamada).

| Concepto | Por tienda al mes |
|---|---|
| STT móvil (unas 3,3 h de audio) | ≈ USD 0,15–0,40 |
| LLM (≈ 1,3 M tokens) | ≈ USD 0,15–0,50 |
| **Total** | **< USD 1** |

Con 1.000 tiendas Pro serían unos USD 300–1.000 al mes frente a sus suscripciones. El costo no es el problema.

## Riesgos reales y condiciones para seguir

1. **No usar el free tier en producción.** Los límites son por cuenta o proyecto, no por tienda: 1.000 tiendas comparten la misma cuota de RPM y tokens diarios. Además, en el free tier de Gemini los datos pueden usarse para mejorar los modelos. → Activar facturación (pay-as-you-go) en Gemini y/o Groq y poner un tope de gasto mensual en cada consola.
2. **Llamadas síncronas dentro de endpoints `async`.** El SDK de Groq y `genai` corren de forma bloqueante dentro de `async def` (`agente.py:84-143` y `parse()` en el orquestador). Con muchos usuarios simultáneos, eso bloquea el event loop. → Usar `run_in_threadpool` o los clientes async.
3. **No hay cuota por tienda.** No existe rate-limit en `app/` (grep de `limiter`/`quota` vacío). Una tienda o un bug en bucle puede consumir la cuota de todas. → Límite simple por `empresa_id` en Redis (p. ej. N comandos por minuto y por día).
4. **Modelos que caducan.** Los nombres de modelo vienen de env vars (bien), pero los defaults `gemini-3.6-flash` y `openai/gpt-oss-120b` están en el código. → Mantenerlos en env, revisar los avisos de deprecación de cada proveedor cada trimestre y, en producción, tener configurados los **dos** proveedores para que el fallback cruzado funcione.

Ya cumplido: sesiones en Redis obligatorias en producción (`session_store.py:118-128`), keys solo en el servidor y feature restringida a planes de pago.

## Lo que más costará mantener (no es la IA)

La fiabilidad del frontend en navegadores reales: diferencias entre Chrome, Safari y Android en Web Speech, permisos de micrófono, BFCache y extensiones, además de bugs como el del overlay (`AUDITORIA_MODO_VOZ_RESULTADO.md`). Esto se mitiga con E2E realistas, no con otro proveedor.
