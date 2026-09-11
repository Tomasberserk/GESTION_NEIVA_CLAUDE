"""Proveedor agnóstico de interpretación de intenciones y slots (IntentProvider).

Soporta parser determinístico ultrarrápido (regex) y adaptadores para Groq (Llama)
y Google Gemini. El agente consume este protocolo sin acoplarse a ningún modelo.
"""

import json
import logging
import math
import os
import re
from dataclasses import dataclass, field
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, field_validator

logger = logging.getLogger(__name__)

ALLOWED_INTENTS = {
    "registrar_venta",
    "reabastecer",
    "consultar_stock",
    "crear_producto",
    "consulta_financiera",
    "confirmar",
    "cancelar",
    "operacion_destructiva",
    "fuera_de_alcance",
    "proveer_slot",
    "unknown",
}

ALLOWED_METRICS = {
    "ventas_hoy",
    "ventas_semana",
    "ventas_mes",
    "recaudo_actual",
    "cantidad_ventas",
    "total_inventario",
    "resumen_actual",
    "recuperacion_inversion",
}

MAX_CANTIDAD = 10000.0
MIN_CANTIDAD = 0.001
MAX_PRECIO = 500_000_000.0


class AgentSlotsSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    product_query: str | None = None
    quantity: float | None = None
    metric: str | None = None
    unit: str | None = None
    precio_venta: float | None = None
    precio_costo: float | None = None

    @field_validator("quantity", mode="before")
    @classmethod
    def validate_quantity(cls, v):
        if v is None:
            return None
        try:
            val = float(v)
        except (ValueError, TypeError):
            return None
        if math.isnan(val) or math.isinf(val) or val < MIN_CANTIDAD or val > MAX_CANTIDAD:
            return None
        return round(val, 3)

    @field_validator("precio_venta", "precio_costo", mode="before")
    @classmethod
    def validate_precio(cls, v):
        if v is None:
            return None
        try:
            val = float(v)
        except (ValueError, TypeError):
            return None
        if math.isnan(val) or math.isinf(val) or val < 0.0 or val > MAX_PRECIO:
            return None
        return round(val, 2)

    @field_validator("metric", mode="before")
    @classmethod
    def validate_metric(cls, v):
        if v is None:
            return None
        v_str = str(v).strip().lower()
        return v_str if v_str in ALLOWED_METRICS else None

    @field_validator("product_query", mode="before")
    @classmethod
    def validate_product_query(cls, v):
        if v is None:
            return None
        v_str = str(v).strip()
        return v_str[:200] if v_str else None


class AgentLLMOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    intent: str = "unknown"
    slots: AgentSlotsSchema = Field(default_factory=AgentSlotsSchema)
    missing_slots: list[str] = Field(default_factory=list)
    confidence: float = 1.0

    @field_validator("intent", mode="before")
    @classmethod
    def validate_intent(cls, v):
        if not v or not isinstance(v, str):
            return "unknown"
        v_clean = v.strip().lower()
        return v_clean if v_clean in ALLOWED_INTENTS else "unknown"

    @field_validator("confidence", mode="before")
    @classmethod
    def validate_confidence(cls, v):
        try:
            val = float(v)
            if math.isnan(val) or math.isinf(val):
                return 0.0
            return max(0.0, min(1.0, val))
        except (ValueError, TypeError):
            return 0.0


def validate_agent_output(
    raw_intent: str,
    raw_slots: dict[str, Any] | None = None,
    raw_missing: list[str] | None = None,
    confidence: float = 1.0,
    raw_text: str = "",
) -> "AgentInterpretation":
    """Valida y sanitiza rigurosamente la salida del LLM antes de enviarla al dominio."""
    try:
        model = AgentLLMOutput(
            intent=raw_intent or "unknown",
            slots=raw_slots or {},
            missing_slots=raw_missing or [],
            confidence=confidence,
        )
        return AgentInterpretation(
            intent=model.intent,
            slots=model.slots.model_dump(exclude_none=True),
            missing_slots=model.missing_slots,
            confidence=model.confidence,
            raw_text=raw_text,
        )
    except Exception as exc:
        logger.warning("Fallo al validar output del LLM con Pydantic: %s", exc)
        return AgentInterpretation(
            intent="unknown",
            slots={},
            missing_slots=[],
            confidence=0.0,
            raw_text=raw_text,
        )


@dataclass
class AgentInterpretation:
    intent: str
    slots: dict[str, Any] = field(default_factory=dict)
    missing_slots: list[str] = field(default_factory=list)
    confidence: float = 1.0
    raw_text: str = ""


class IntentProvider(Protocol):
    def parse(self, text: str, context: dict[str, Any] | None = None) -> AgentInterpretation:
        ...


# ---------------------------------------------------------------------------
# Parser determinístico rápido (Regex)
# ---------------------------------------------------------------------------

def quick_parse_intent(text: str) -> AgentInterpretation | None:
    """Detecta intenciones obvias y comandos directos de forma determinística."""
    if not text or not isinstance(text, str):
        return None

    t = text.lower().strip()

    # 1. Confirmaciones directas
    if t in ["si", "sí", "confirmar", "confirmo", "dale", "de una", "ok", "correcto", "exacto", "hágale", "hagale", "yes"]:
        return AgentInterpretation(intent="confirmar", confidence=1.0, raw_text=text)

    # 2. Cancelaciones directas
    if any(k in t for k in ["cancelar", "cancela", "abortar", "olvidalo", "olvídalo", "ya no", "no gracias"]) or re.match(r"^no[\s,.]", t) or t == "no":
        return AgentInterpretation(intent="cancelar", confidence=1.0, raw_text=text)

    # 3. Operaciones destructivas bloqueadas (P1)
    if re.search(r"\b(elimina|eliminar|borra|borrar|destruir)\b", t) and any(w in t for w in ["producto", "arroz", "coca", "inventario"]):
        return AgentInterpretation(intent="operacion_destructiva", confidence=1.0, raw_text=text)

    # 4. Mensajes fuera de alcance evidentes
    if any(k in t for k in ["bitcoin", "cripto", "poema", "chiste", "cancion", "canción", "receta", "clima", "politica", "política"]):
        return AgentInterpretation(intent="fuera_de_alcance", confidence=1.0, raw_text=text)

    # 5. Consultas financieras directas
    if any(k in t for k in ["cuanto he vendido hoy", "cuánto he vendido hoy", "ventas de hoy", "ventas hoy"]):
        return AgentInterpretation(intent="consulta_financiera", slots={"metric": "ventas_hoy"}, confidence=0.99, raw_text=text)

    if any(k in t for k in ["esta semana", "esta semana vendi", "ventas de la semana"]):
        return AgentInterpretation(intent="consulta_financiera", slots={"metric": "ventas_semana"}, confidence=0.98, raw_text=text)

    if any(k in t for k in ["este mes", "ventas del mes", "ventas de este mes"]):
        return AgentInterpretation(intent="consulta_financiera", slots={"metric": "ventas_mes"}, confidence=0.98, raw_text=text)

    if any(k in t for k in ["cuanto he recaudado", "cuánto he recaudado", "recaudo", "dinero ingresado"]):
        return AgentInterpretation(intent="consulta_financiera", slots={"metric": "recaudo_actual"}, confidence=0.98, raw_text=text)

    if any(k in t for k in ["cuantas ventas", "cuántas ventas", "numero de ventas", "cantidad de ventas"]):
        return AgentInterpretation(intent="consulta_financiera", slots={"metric": "cantidad_ventas"}, confidence=0.98, raw_text=text)

    if any(k in t for k in ["cuanto inventario tengo", "cuánto inventario", "total inventario", "valor de mi inventario"]):
        return AgentInterpretation(intent="consulta_financiera", slots={"metric": "total_inventario"}, confidence=0.98, raw_text=text)

    if any(k in t for k in ["resumen actual", "cual es mi resumen", "cómo va el día", "resumen del dia"]):
        return AgentInterpretation(intent="consulta_financiera", slots={"metric": "resumen_actual"}, confidence=0.98, raw_text=text)

    if any(k in t for k in ["recuperar mi inversion", "recuperar mi inversión", "recuperacion de inversion"]):
        return AgentInterpretation(intent="consulta_financiera", slots={"metric": "recuperacion_inversion"}, confidence=0.98, raw_text=text)

    # 6. Consultas de stock simples
    m_stock = re.search(r"(?:cuanto|cuánto|cuantos|cuántos|stock|queda|quedan|hay)\s+(?:tengo\s+de\s+|de\s+)?([\w\s\.\-_]+?)(?:\?|$)", t)
    if m_stock and not any(v in t for v in ["vendi", "vendí", "llegaron", "compré"]):
        prod_q = m_stock.group(1).strip()
        prod_q = re.sub(r"\b(tengo|de|el|la|los|las)\b", "", prod_q).strip()
        if prod_q:
            return AgentInterpretation(intent="consultar_stock", slots={"product_query": prod_q}, confidence=0.90, raw_text=text)

    # Normalización de números escritos en palabras comunes (ej: "dos" -> "2")
    NUMEROS_TEXTO = {
        "un": "1", "uno": "1", "una": "1",
        "dos": "2", "tres": "3", "cuatro": "4", "cinco": "5",
        "seis": "6", "siete": "7", "ocho": "8", "nueve": "9", "diez": "10",
        "once": "11", "doce": "12", "quince": "15", "veinte": "20",
    }
    t_num = t
    for word_num, digit_val in NUMEROS_TEXTO.items():
        t_num = re.sub(rf"\b{word_num}\b", digit_val, t_num)

    # 7. Venta explícita sencilla (ej: "vendí 2 coca colas", "hoy vendi dos aceites")
    m_venta = re.search(r"(?:vendi|vendí|venta de|facturé|facture)\s+(\d+(?:\.\d+)?)\s+(?:de\s+)?([\w\s\.\-_]+)", t_num)
    if m_venta:
        qty = float(m_venta.group(1))
        prod_q = m_venta.group(2).strip()
        return validate_agent_output(
            raw_intent="registrar_venta",
            raw_slots={"product_query": prod_q, "quantity": qty},
            confidence=0.95,
            raw_text=text,
        )

    # 8. Reabastecimiento explícito sencillo (ej: "llegaron 5 aceites diana", "compré 10 cervezas")
    m_reab = re.search(r"(?:llegaron|llegó|llego|compre|compré|recibí|recibi|entran|entraron)\s+(\d+(?:\.\d+)?)\s+(?:de\s+)?([\w\s\.\-_]+)", t_num)
    if m_reab:
        qty = float(m_reab.group(1))
        prod_q = m_reab.group(2).strip()
        return validate_agent_output(
            raw_intent="reabastecer",
            raw_slots={"product_query": prod_q, "quantity": qty},
            confidence=0.95,
            raw_text=text,
        )

    return None


# ---------------------------------------------------------------------------
# Implementación LLM (Groq / Gemini)
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """Eres el clasificador de intenciones del sistema POS Gestión Neiva.
Tu función es extraer la intención y los slots del mensaje del tendero.
RESPONDE EXCLUSIVAMENTE CON UN JSON VÁLIDO sin markdown ni explicaciones.

INTENCIONES PERMITIDAS:
- "registrar_venta": El usuario informa que vendió uno o más productos.
- "reabastecer": Llegó mercancía / aumentó el stock de un producto.
- "consultar_stock": Pregunta cuánto queda o precio de un producto.
- "crear_producto": Quiere registrar un producto completamente nuevo.
- "consulta_financiera": Pregunta por métricas (ventas_hoy, ventas_semana, ventas_mes, recaudo_actual, cantidad_ventas, total_inventario, resumen_actual, recuperacion_inversion).
- "confirmar": El usuario acepta o confirma ("sí", "dale", "correcto").
- "cancelar": El usuario cancela o rechaza ("no", "cancela").
- "fuera_de_alcance": Conversación general, chistes, temas no relacionados con la tienda.
- "unknown": El mensaje es confuso o incomprensible.

ESTRUCTURA DE RESPUESTA JSON:
{
  "intent": "...",
  "slots": {
    "product_query": "nombre del producto mencionado o null",
    "quantity": 2.0,
    "metric": "ventas_hoy o null",
    "unit": "unidad o kilo o libra o null",
    "precio_venta": 5000,
    "precio_costo": 3500
  },
  "missing_slots": [],
  "confidence": 0.95
}"""


class LLMIntentProvider:
    """Proveedor que delega la interpretación al LLM si el parser determinístico no coincide."""

    def __init__(self, provider: str = "groq", model: str | None = None):
        default_gemini = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
        self.model = model or ("llama-3.3-70b-versatile" if self.provider == "groq" else default_gemini)

    def parse(self, text: str, context: dict[str, Any] | None = None) -> AgentInterpretation:
        # 1. Intentar el parser rápido determinístico primero
        quick = quick_parse_intent(text)
        if quick:
            return quick

        # 2. Si hay contexto de aclaración pendiente y el usuario envía un número o palabra corta
        if context and context.get("estado") == "NEEDS_CLARIFICATION":
            missing = context.get("missing_slots", [])
            if "cantidad" in missing:
                m_num = re.search(r"^(\d+(?:\.\d+)?)$", text.strip())
                if m_num:
                    return AgentInterpretation(
                        intent="proveer_slot",
                        slots={"quantity": float(m_num.group(1))},
                        confidence=0.99,
                        raw_text=text,
                    )

        # 3. Invocar API de IA según proveedor
        try:
            if self.provider == "groq":
                return self._parse_groq(text)
            elif self.provider == "gemini":
                return self._parse_gemini(text)
            else:
                return self._parse_gemini(text)
        except Exception as exc:
            logger.error("Error al invocar LLM IntentProvider (%s): %s", self.provider, exc)
            return AgentInterpretation(intent="unknown", raw_text=text, confidence=0.0)

    def _parse_groq(self, text: str) -> AgentInterpretation:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            # Fallback a Gemini si falta la key de Groq
            return self._parse_gemini(text)

        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        return validate_agent_output(
            raw_intent=data.get("intent", "unknown"),
            raw_slots=data.get("slots", {}),
            raw_missing=data.get("missing_slots", []),
            confidence=float(data.get("confidence", 0.8)),
            raw_text=text,
        )

    def _parse_gemini(self, text: str) -> AgentInterpretation:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return AgentInterpretation(intent="unknown", raw_text=text, confidence=0.0)

        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(self.model)
        full_prompt = f"{_SYSTEM_PROMPT}\n\nMENSAJE DEL TENDERO:\n{text}"
        response = model.generate_content(full_prompt)
        content = response.text.strip()
        if content.startswith("```"):
            lines = [l for l in content.split("\n") if not l.strip().startswith("```")]
            content = "\n".join(lines).strip()
        data = json.loads(content)
        return validate_agent_output(
            raw_intent=data.get("intent", "unknown"),
            raw_slots=data.get("slots", {}),
            raw_missing=data.get("missing_slots", []),
            confidence=float(data.get("confidence", 0.8)),
            raw_text=text,
        )


def get_intent_provider() -> IntentProvider:
    """Factory para instanciar el proveedor configurado."""
    prov = os.getenv("AI_PROVIDER", "groq")
    mod = os.getenv("AI_MODEL")
    return LLMIntentProvider(provider=prov, model=mod)
