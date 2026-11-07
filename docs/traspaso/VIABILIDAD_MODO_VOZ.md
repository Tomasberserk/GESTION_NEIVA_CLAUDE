# Viabilidad del Modo Voz en producción (análisis 28-10)

> Documento de decisión. Autor: Gemini/Antigravity. Estado: **propuesta**, pendiente de validación por Claude y el dueño.

## Veredicto

**Sí es viable y sostenible**, siempre que se cumplan cuatro condiciones operativas (ver más abajo). El costo de IA por tienda es marginal. El riesgo real está en la operación: cuotas compartidas, límites de concurrencia y la fiabilidad de la UI en navegadores reales.

## Cómo está construido hoy (verificado en el código)

**Tabla 1**  
*Registro estructurado de especificaciones técnicas ( Sección 1 )*

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

*Nota.* Especificación técnica sincronizada con la arquitectura vigente del proyecto. Fuente: Elaboración propia (2026).

Credenciales locales (verificado el 28-10): `GOOGLE_API_KEY` = `GEMINI_API_KEY` (la misma key). **Es válida** y `gemini-3.6-flash` responde. Un primer intento devolvió **503** (sobrecarga transitoria), lo que muestra que el fallback es necesario. `GROQ_API_KEY` **no está** en el `.env` local, así que localmente todo pasa por Gemini (`get_intent_provider`, línea 1209).

## Costo estimado (orden de magnitud; verificar precios vigentes)

Supuesto pesimista por tienda: 100 comandos de voz al día, unos 4 s de audio cada uno, y un 30 % de frases que necesitan LLM (unos 1.500 tokens por llamada).

**Tabla 2**  
*Registro estructurado de especificaciones técnicas ( Sección 2 )*

| Concepto | Por tienda al mes |
|---|---|
| STT móvil (unas 3,3 h de audio) | ≈ USD 0,15–0,40 |
| LLM (≈ 1,3 M tokens) | ≈ USD 0,15–0,50 |
| **Total** | **< USD 1** |

*Nota.* Especificación técnica sincronizada con la arquitectura vigente del proyecto. Fuente: Elaboración propia (2026).

Con 1.000 tiendas Pro serían unos USD 300–1.000 al mes frente a sus suscripciones. El costo no es el problema.

## Riesgos reales y condiciones para seguir

1. **No usar el free tier en producción.** Los límites son por cuenta o proyecto, no por tienda: 1.000 tiendas comparten la misma cuota de RPM y tokens diarios. Además, en el free tier de Gemini los datos pueden usarse para mejorar los modelos. → Activar facturación (pay-as-you-go) en Gemini y/o Groq y poner un tope de gasto mensual en cada consola.
2. **Llamadas síncronas dentro de endpoints `async`.** El SDK de Groq y `genai` corren de forma bloqueante dentro de `async def` (`agente.py:84-143` y `parse()` en el orquestador). Con muchos usuarios simultáneos, eso bloquea el event loop. → Usar `run_in_threadpool` o los clientes async.
3. **No hay cuota por tienda.** No existe rate-limit en `app/` (grep de `limiter`/`quota` vacío). Una tienda o un bug en bucle puede consumir la cuota de todas. → Límite simple por `empresa_id` en Redis (p. ej. N comandos por minuto y por día).
4. **Modelos que caducan.** Los nombres de modelo vienen de env vars (bien), pero los defaults `gemini-3.6-flash` y `openai/gpt-oss-120b` están en el código. → Mantenerlos en env, revisar los avisos de deprecación de cada proveedor cada trimestre y, en producción, tener configurados los **dos** proveedores para que el fallback cruzado funcione.

Ya cumplido: sesiones en Redis obligatorias en producción (`session_store.py:118-128`), keys solo en el servidor y feature restringida a planes de pago.

## Lo que más costará mantener (no es la IA)

La fiabilidad del frontend en navegadores reales: diferencias entre Chrome, Safari y Android en Web Speech, permisos de micrófono, BFCache y extensiones, además de bugs como el del overlay (`AUDITORIA_MODO_VOZ_RESULTADO.md`). Esto se mitiga con E2E realistas, no con otro proveedor.

---

## Declaración de Uso de Inteligencia Artificial Generativa y Derechos de Autor (Norma APA 7.ª Edición)

En cumplimiento de las políticas de integridad académica y propiedad intelectual del Servicio Nacional de Aprendizaje (SENA — Programa ADSO) y los estándares de citación de la American Psychological Association (APA, 7.ª ed., 2020), el equipo de desarrollo integrado por Tomás Barrera Ortiz (`@Tomasberserk`), Santiago Javela Ospino (`@SantiagoJavelaOspino`) y Juan Pablo Doria Caviedes (`@Doritotes444`) declara de manera explícita y transparente el uso ético y supervisado de herramientas de Inteligencia Artificial Generativa (IAG):

1. **Alcance del apoyo con IA:** Los modelos de lenguaje fueron utilizados como asistentes de programación en pareja (*pair programming*), generación de código repetitivo (*boilerplate* de esquemas Pydantic y migraciones Alembic), estructuración inicial de plantillas documentales bajo el marco SDD (*Specification-Driven Development*), auditoría estática de seguridad OWASP y pruebas automatizadas. Toda la arquitectura de negocio, reglas de dominio del comercio minorista en Neiva (`BR-01` a `BR-12`), validación funcional y decisiones técnicas fueron diseñadas, verificadas y aprobadas íntegramente por los aprendices autores.
2. **Modelos utilizados y atribución técnica:**
   - *Anthropic Claude Sonnet 4.6 y Claude Haiku 4.5* (Anthropic, 2026): Asistencia en refactorización modular, generación de esquemas, contratos de fachada y coautoría declarada en metadatos de commits (`Co-Authored-By`).
   - *Google Gemini 2.5 Flash / 3.6 Flash* (Google DeepMind, 2026): Procesamiento de lenguaje natural en el módulo `agente_ia`, análisis de contexto de repositorio y revisión de calidad documental.
   - *Groq Cloud Whisper Large v3* (Groq Inc., 2026): Transcripción automática de voz a texto (STT) en tiempo real para el Modo Mostrador del punto de venta.
   - *OpenAI ChatGPT (GPT-4o)* (OpenAI, 2026) y *Google Veo*: Consultoría de optimización de rendimiento frontend (`code-splitting`) y apoyo en guionización visual de la página de aterrizaje.
3. **Derechos de autor y licencias de terceros:** El código fuente original de **Gestión Neiva (TiendApp POS SaaS)** es propiedad intelectual de sus autores humanos (Barrera Ortiz, Javela Ospino y Doria Caviedes, 2026). Las librerías de terceros (FastAPI, SQLAlchemy, React 19, TailwindCSS, Radix UI, Lucide Icons, ZXing) se utilizan bajo sus respectivas licencias de código abierto (MIT / Apache 2.0 / BSD), y los recursos fotográficos de demostración provienen de bancos libres de regalías (Pexels / Picsum Photos) conforme a sus términos de atribución.

**Referencias de modelos IA (Formato APA 7):**
- Anthropic. (2026). *Claude (Versiones Sonnet 4.6 y Haiku 4.5)* [Modelo de lenguaje grande]. https://www.anthropic.com
- Google. (2026). *Gemini (Versión 2.5 Flash)* [Modelo multimodal de inteligencia artificial]. https://deepmind.google/technologies/gemini/
- OpenAI. (2026). *ChatGPT (Versión GPT-4o)* [Modelo de lenguaje grande]. https://chat.openai.com
