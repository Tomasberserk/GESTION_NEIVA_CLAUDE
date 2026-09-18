"""Proveedor agnóstico de interpretación de intenciones y slots (IntentProvider).

Soporta parser determinístico semántico rápido enriquecido con modismos de mostrador colombiano
y adaptadores para Groq (Llama) y Google Gemini con memoria de contexto de negocio.
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
    "consulta_productos",
    "consulta_inventario_critico",
    "consulta_top_ventas",
    "comparacion",
    "ambiguo",
    "confirmar",
    "cancelar",
    "operacion_destructiva",
    "fuera_de_alcance",
    "proveer_slot",
    "unknown",
}

ALLOWED_METRICS = {
    "ventas_hoy",
    "ventas_ayer",
    "ventas_semana",
    "ventas_mes",
    "recaudo_actual",
    "cantidad_ventas",
    "total_inventario",
    "resumen_actual",
    "recuperacion_inversion",
    "ventas_vendedor",
}

MAX_CANTIDAD = 10000.0
MIN_CANTIDAD = 0.001
MAX_PRECIO = 500_000_000.0


class AgentSlotsSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    product_query: str | None = None
    quantity: float | None = None
    metric: str | None = None
    period: str | None = None
    seller_name: str | None = None
    action: str | None = None
    comparison_type: str | None = None
    target_a: str | None = None
    target_b: str | None = None
    ambiguity_type: str | None = None
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

    @field_validator("product_query", "seller_name", "period", "action", "comparison_type", mode="before")
    @classmethod
    def validate_strings(cls, v):
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
    """Valida y sanitiza rigurosamente la salida del LLM o del parser antes de enviarla al orquestador."""
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
        logger.warning("Fallo al validar output con Pydantic: %s", exc)
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


class LLMProviderUnavailableError(Exception):
    """Excepción lanzada cuando el proveedor LLM sufre una falla técnica de infraestructura."""

    def __init__(self, provider: str, reason: str, status_code: int = 503):
        self.provider = provider
        self.reason = reason
        self.status_code = status_code
        super().__init__(f"LLM Provider '{provider}' unavailable: {reason}")


AGENT_TELEMETRY: dict[str, int] = {
    "llm_provider_success": 0,
    "llm_provider_failure": 0,
    "intent_parse_success": 0,
    "intent_parse_failure": 0,
    "business_service_success": 0,
    "business_service_failure": 0,
}


def get_agent_telemetry() -> dict[str, int]:
    return dict(AGENT_TELEMETRY)


def reset_agent_telemetry() -> None:
    for k in AGENT_TELEMETRY:
        AGENT_TELEMETRY[k] = 0


# ---------------------------------------------------------------------------
# Normalización de texto y diccionarios coloquiales de Colombia
# ---------------------------------------------------------------------------

NUMEROS_TEXTO = {
    "un": "1", "uno": "1", "una": "1",
    "dos": "2", "tres": "3", "cuatro": "4", "cinco": "5",
    "seis": "6", "siete": "7", "ocho": "8", "nueve": "9", "diez": "10",
    "once": "11", "doce": "12", "quince": "15", "veinte": "20",
}

SINONIMOS_PRODUCTOS_COL = {
    "pola": "cerveza", "polas": "cerveza",
    "birra": "cerveza", "birras": "cerveza",
    "chela": "cerveza", "chelas": "cerveza",
    "librita de arroz": "arroz",
    "libra de arroz": "arroz",
    "arroces": "arroz",
    "aceites": "aceite",
    "cubeta de huevos": "huevos",
}


def _normalizar_frase(texto: str) -> str:
    """Limpia signos de puntuación inicial/final, tildes comunes y minúsculas."""
    t = texto.strip().lower()
    t = re.sub(r"^[¿\?¡\!]+|[¿\?¡\!]+$", "", t).strip()
    return t


# ---------------------------------------------------------------------------
# Parser determinístico semántico (rápido, determinístico y robusto)
# ---------------------------------------------------------------------------

def quick_parse_intent(text: str, context: dict[str, Any] | None = None) -> AgentInterpretation | None:
    """Detecta intenciones de negocio, contexto multi-turno, ambigüedad y modismos colombianos."""
    if not text or not isinstance(text, str):
        return None

    t = _normalizar_frase(text)
    b_ctx = (context or {}).get("business_context", {})

    # 1. Confirmaciones determinísticas inequívocas
    if t in ["si", "sí", "confirmar", "confirmo", "dale", "de una", "ok", "correcto", "exacto", "hágale", "hagale", "yes", "listo"]:
        return AgentInterpretation(intent="confirmar", confidence=1.0, raw_text=text)

    # 2. Cancelaciones determinísticas inequívocas
    if any(k in t for k in ["cancelar", "cancela", "abortar", "olvidalo", "olvídalo", "ya no", "no gracias", "descartar"]) or re.match(r"^no[\s,.]", t) or t == "no":
        return AgentInterpretation(intent="cancelar", confidence=1.0, raw_text=text)

    # 3. Operaciones destructivas bloqueadas
    if re.search(r"\b(elimina|eliminar|borra|borrar|destruir)\b", t) and any(w in t for w in ["producto", "arroz", "coca", "inventario", "tienda", "ventas"]):
        return AgentInterpretation(intent="operacion_destructiva", confidence=1.0, raw_text=text)

    # 4. Out-of-Domain (temas generales que no corresponden a un POS de mostrador)
    OUT_OF_DOMAIN_PATTERNS = [
        r"\b(capital de|francia|italia|españa|bogota)\b",
        r"\b(chiste|pepito|broma|cuentame un chiste)\b",
        r"\b(partido de fútbol|fútbol|futbol|mundial|messi|ronaldo)\b",
        r"\b(poema|amor y la luna|poesía|verso)\b",
        r"\b(receta|arroz con pollo|preparo|cocinar)\b",
        r"\b(presidente|política|politica|alcalde|senado)\b",
        r"\b(bitcoin|cripto|criptomoneda|ethereum)\b",
        r"\b(tarea|matemáticas|matematicas|integrales|derivadas|química)\b",
        r"\b(clima|va a llover|temperatura)\b",
        r"\b(descubrió américa|colon|1492|historia)\b",
        r"\b(película|pelicula|netflix|cine|serie)\b",
        r"\b(hackear|contraseña del wifi|wifi de mi vecino)\b",
        r"\b(tradúceme|traducir|mandarín|ingles|idioma)\b",
        r"\b(mejor carro|automóvil|ferrari|toyota)\b",
        r"\b(canción|cancion|salsa|reggaeton|bailar)\b",
        r"\b(correo de renuncia|carta de renuncia|jefe)\b",
        r"\b(dolor de cabeza|remedios caseros|medicina|ibuprofeno)\b",
        r"\b(tierra y marte|planeta|espacio|nasa)\b",
        r"\b(río magdalena|rio magdalena|geografia|geografía)\b",
    ]
    for pattern in OUT_OF_DOMAIN_PATTERNS:
        if re.search(pattern, t):
            return AgentInterpretation(intent="fuera_de_alcance", confidence=1.0, raw_text=text)

    # 5. Ambigüedad evidente (frases hiper-vagas de mostrador que requieren aclaración guiada)
    AMBIGUOUS_EXACTS = {
        "cuanto tenemos", "cuánto tenemos",
        "como vamos", "cómo vamos",
        "cuanto salio", "cuánto salió",
        "cuanto hay", "cuánto hay",
        "que se movio", "qué se movió",
        "ventas", "stock",
        "cuanto fue", "cuánto fue",
        "como estamos", "cómo estamos",
        "cuanto queda", "cuánto queda",
        "reporte", "que tenemos", "qué tenemos",
        "cuanto dio", "cuánto dio",
        "total",
        "cuanto se hizo", "cuánto se hizo",
        "a como", "a cómo",
        "hay o no hay",
        "inventario",
        "que falta", "qué falta",
        "cuanto entro", "cuánto entró",
    }
    if t in AMBIGUOUS_EXACTS:
        return AgentInterpretation(
            intent="ambiguo",
            slots={"ambiguity_type": t},
            confidence=0.98,
            raw_text=text,
        )

    # 6. Contexto Multi-Turno (Anáforas y Elipsis de Mostrador)
    # Ej: "¿Y ayer?", "¿Y esta semana?", "¿Y este mes?", "¿Y de aceite?", "¿Y a cómo está?", "¿Y Don Pedro?"
    if re.match(r"^y\s+", t) or t.startswith("¿y ") or t.startswith("y "):
        t_sub = re.sub(r"^[¿\?]?y\s+", "", t).strip()

        # 6.1 "¿Y ayer?"
        if "ayer" in t_sub:
            last_dom = b_ctx.get("last_domain", "VENTAS")
            if last_dom == "REPORTES" and b_ctx.get("last_action") == "top_ventas":
                return AgentInterpretation(
                    intent="consulta_top_ventas",
                    slots={"period": "ayer"},
                    confidence=0.95,
                    raw_text=text,
                )
            seller = b_ctx.get("last_seller")
            return AgentInterpretation(
                intent="consulta_financiera",
                slots={"metric": "ventas_ayer", "period": "ayer", "seller_name": seller},
                confidence=0.95,
                raw_text=text,
            )

        # 6.2 "¿Y esta semana?"
        if "semana" in t_sub:
            return AgentInterpretation(
                intent="consulta_financiera",
                slots={"metric": "ventas_semana", "period": "semana"},
                confidence=0.95,
                raw_text=text,
            )

        # 6.3 "¿Y este mes?"
        if "mes" in t_sub:
            return AgentInterpretation(
                intent="consulta_financiera",
                slots={"metric": "ventas_mes", "period": "mes"},
                confidence=0.95,
                raw_text=text,
            )

        # 6.4 "¿Y con stock bajo?"
        if "stock bajo" in t_sub or "bajo" in t_sub or "escaso" in t_sub:
            return AgentInterpretation(
                intent="consulta_inventario_critico",
                slots={"action": "stock_bajo"},
                confidence=0.95,
                raw_text=text,
            )

        # 6.5 "¿Y a cómo está?" / "¿Y cuánto vale?" (hereda producto)
        if any(w in t_sub for w in ["a como", "a cómo", "precio", "cuanto vale", "cuánto vale"]):
            last_p = b_ctx.get("last_product", "arroz")
            return AgentInterpretation(
                intent="consulta_productos",
                slots={"product_query": last_p, "action": "precio"},
                confidence=0.95,
                raw_text=text,
            )

        # 6.6 "¿Y cuánto queda?" (hereda producto para stock)
        if any(w in t_sub for w in ["cuanto queda", "cuánto queda", "stock", "hay"]):
            last_p = b_ctx.get("last_product", "leche")
            return AgentInterpretation(
                intent="consultar_stock",
                slots={"product_query": last_p},
                confidence=0.95,
                raw_text=text,
            )

        # 6.7 "¿Y Don Pedro?" (hereda ventas por vendedor)
        if any(n in t_sub for n in ["don pedro", "pedro", "paula", "cajero"]):
            seller = "Don Pedro" if "pedro" in t_sub else "Paula"
            return AgentInterpretation(
                intent="consulta_financiera",
                slots={"metric": "ventas_vendedor", "seller_name": seller, "period": b_ctx.get("last_period", "hoy")},
                confidence=0.95,
                raw_text=text,
            )

        # 6.8 "¿Y de aceite?" / "¿Y cuántas cervezas?" (cambio de entidad en mismo dominio)
        for kw in ["aceite", "arroz", "cerveza", "pola", "polas", "pan", "leche", "jabón", "jabon", "gaseosa", "huevos"]:
            if kw in t_sub:
                clean_kw = SINONIMOS_PRODUCTOS_COL.get(kw, kw)
                last_dom = b_ctx.get("last_domain", "INVENTARIO")
                if "a cómo" in t_sub or "cuánto vale" in t_sub or "precio" in t_sub:
                    return AgentInterpretation(
                        intent="consulta_productos",
                        slots={"product_query": clean_kw, "action": "precio"},
                        confidence=0.95,
                        raw_text=text,
                    )
                return AgentInterpretation(
                    intent="consultar_stock",
                    slots={"product_query": clean_kw},
                    confidence=0.95,
                    raw_text=text,
                )

    # 6.9 Turnos consecutivos específicos sin 'y'
    if t in ["cuantas transacciones fueron", "cuántas transacciones fueron", "cuantas transacciones van"]:
        return AgentInterpretation(
            intent="consulta_financiera",
            slots={"metric": "cantidad_ventas", "period": b_ctx.get("last_period", "hoy")},
            confidence=0.95,
            raw_text=text,
        )
    if t in ["cuanto vale", "cuánto vale", "precio"]:
        last_p = b_ctx.get("last_product", "pan")
        return AgentInterpretation(
            intent="consulta_productos",
            slots={"product_query": last_p, "action": "precio"},
            confidence=0.95,
            raw_text=text,
        )

    # 7. Comparaciones de negocio determinísticas
    # 7.1 Hoy vs Ayer
    if any(k in t for k in [
        "vendimos más hoy que ayer", "vendimos mas hoy que ayer",
        "comparado con ayer", "más hoy o ayer", "mas hoy o ayer",
        "frente a ayer", "mejor o peor que ayer", "hoy vs ayer",
        "comparar ventas hoy", "hoy comparado con ayer", "hoy superó a ayer",
        "hoy supero a ayer", "subieron las ventas hoy", "mayores a las de ayer",
        "mejor ayer o hoy", "ayer o hoy mi socio"
    ]):
        return AgentInterpretation(
            intent="comparacion",
            slots={"comparison_type": "hoy_vs_ayer", "target_a": "hoy", "target_b": "ayer"},
            confidence=0.98,
            raw_text=text,
        )

    # 7.2 Comparación de vendedores
    if any(k in t for k in [
        "quién vendió más hoy", "quien vendio mas hoy", "paula vendió más que don pedro",
        "paula vendio mas que don pedro", "quién lleva más ventas hoy", "quien lleva mas ventas",
        "lidera las ventas entre los cajeros", "hizo más ventas que", "quién ha facturado más hoy",
        "quien ha facturado mas", "cajero que más ha vendido", "cajero que mas ha vendido"
    ]):
        return AgentInterpretation(
            intent="comparacion",
            slots={"comparison_type": "vendedores", "period": "hoy"},
            confidence=0.98,
            raw_text=text,
        )

    # 7.3 Comparación de productos
    if any(k in t for k in [
        "se vende más arroz o aceite", "qué salió más", "que salio mas", "quién vendió más unidades",
        "se ha vendido más hoy, arroz", "cuál tiene más stock", "mayor precio", "más existencias",
        "más rotación", "mas rotacion"
    ]):
        comp_t = "stock" if any(w in t for w in ["stock", "existencias"]) else ("precios" if "precio" in t else "productos")
        return AgentInterpretation(
            intent="comparacion",
            slots={"comparison_type": comp_t, "target_a": "producto_a", "target_b": "producto_b"},
            confidence=0.95,
            raw_text=text,
        )

    # 8. Reportes y Análisis
    # 8.1 Producto más vendido / Top ventas
    if any(k in t for k in [
        "producto más vendido", "producto mas vendido", "lo que más se ha vendido",
        "lo que mas se ha vendido", "el que más sale", "el que mas sale", "rey de ventas",
        "se vendió más hoy", "se vendio mas hoy", "top 1 de ventas", "producto estrella",
        "lidera las ventas", "más compra la gente", "mas compra la gente", "pide la gallada",
        "más vendido de la semana", "lideró ventas ayer", "top de ventas", "más salida", "mas salida",
        "el más vendido", "el mas vendido", "lo que más vendimos", "lo que mas vendimos",
        "que más vendimos", "que mas vendimos", "más vendido", "mas vendido"
    ]):
        per = "ayer" if "ayer" in t else ("semana" if "semana" in t else "hoy")
        return AgentInterpretation(
            intent="consulta_top_ventas",
            slots={"period": per, "action": "top_ventas"},
            confidence=0.98,
            raw_text=text,
        )

    # 8.2 Menor rotación
    if any(k in t for k in ["menos se mueve", "menor rotación", "menor rotacion"]):
        return AgentInterpretation(
            intent="consulta_top_ventas",
            slots={"action": "menor_rotacion"},
            confidence=0.95,
            raw_text=text,
        )

    # 8.3 Resumen rápido del día
    if any(k in t for k in [
        "cómo va el día", "como va el dia", "resumen de hoy", "resumen del día", "resumen del dia",
        "reporte rápido de hoy", "reporte rapido de hoy", "resumen actual", "cómo está el negocio hoy",
        "como esta el negocio", "cómo pinta el día hoy", "balance rápido", "reporte del día",
        "cómo cerramos hoy", "como cerramos hoy"
    ]):
        return AgentInterpretation(
            intent="consulta_financiera",
            slots={"metric": "resumen_actual", "period": "hoy"},
            confidence=0.98,
            raw_text=text,
        )

    # 8.4 Recaudo actual / caja
    if any(k in t for k in [
        "dinero ha ingresado", "cuánto es el recaudo", "cuanto es el recaudo",
        "dinero hay en caja", "efectivo o recaudo", "recaudo de hoy", "billete entró hoy a la caja",
        "recaudo actual"
    ]):
        return AgentInterpretation(
            intent="consulta_financiera",
            slots={"metric": "recaudo_actual", "period": "hoy"},
            confidence=0.98,
            raw_text=text,
        )

    # 8.5 Recuperación de inversión / balance general
    if any(k in t for k in [
        "recuperación de mi inversión", "recuperacion de mi inversion", "recupero la inversión",
        "balance de inversión", "falta para recuperar lo invertido", "recuperación de inversión",
        "recuperacion de inversion", "recuperar mi inversión", "recuperar mi inversion",
        "recuperar la inversión", "recuperar la inversion", "recuperar lo invertido"
    ]):
        return AgentInterpretation(
            intent="consulta_financiera",
            slots={"metric": "recuperacion_inversion"},
            confidence=0.98,
            raw_text=text,
        )

    # 9. Ventas (por período, vendedor o métrica)
    # 9.1 Ventas por vendedor específico ("Paula", "Don Pedro", "yo")
    if any(k in t for k in ["vendió paula", "vendio paula", "ha vendido paula", "ventas de paula", "coronó paula", "corono paula"]):
        return AgentInterpretation(
            intent="consulta_financiera",
            slots={"metric": "ventas_vendedor", "seller_name": "Paula", "period": "hoy"},
            confidence=0.98,
            raw_text=text,
        )
    if any(k in t for k in ["don pedro", "hizo don pedro", "coronó don pedro", "corono don pedro"]):
        return AgentInterpretation(
            intent="consulta_financiera",
            slots={"metric": "ventas_vendedor", "seller_name": "Don Pedro", "period": "hoy"},
            confidence=0.98,
            raw_text=text,
        )
    if any(k in t for k in ["cuánto vendí yo", "cuanto vendi yo", "mis ventas"]):
        return AgentInterpretation(
            intent="consulta_financiera",
            slots={"metric": "ventas_vendedor", "seller_name": "yo", "period": "hoy"},
            confidence=0.98,
            raw_text=text,
        )

    # 9.2 Cantidad de ventas / transacciones
    if any(k in t for k in [
        "cuántas ventas", "cuantas ventas", "cuántas transacciones", "cuantas transacciones",
        "número de ventas", "clientes han comprado", "cuántas facturas", "cuantas facturas",
        "clientes cayeron hoy a comprar"
    ]):
        return AgentInterpretation(
            intent="consulta_financiera",
            slots={"metric": "cantidad_ventas", "period": "hoy"},
            confidence=0.98,
            raw_text=text,
        )

    # 9.3 Ventas de ayer
    if any(k in t for k in [
        "vendimos ayer", "se vendió ayer", "se vendio ayer", "ventas de ayer", "saldo de ayer",
        "ventas de ayer", "salió ayer", "salio ayer", "recaudamos ayer", "cerró ayer", "cerro ayer",
        "se echó al bolsillo el negocio ayer", "se echo al bolsillo el negocio ayer",
        "cómo nos fue ayer", "como nos fue ayer"
    ]):
        return AgentInterpretation(
            intent="consulta_financiera",
            slots={"metric": "ventas_ayer", "period": "ayer"},
            confidence=0.98,
            raw_text=text,
        )

    # 9.4 Ventas de la semana
    if any(k in t for k in [
        "en la semana", "esta semana", "ha estado la semana", "total semanal",
        "últimos 7 días", "ultimos 7 dias", "llevamos esta semana", "saldo de la semana",
        "vendimos esta semana", "pintó la semana", "pinto la semana"
    ]):
        return AgentInterpretation(
            intent="consulta_financiera",
            slots={"metric": "ventas_semana", "period": "semana"},
            confidence=0.98,
            raw_text=text,
        )

    # 9.5 Ventas del mes
    if any(k in t for k in [
        "en el mes", "este mes", "va el mes", "total mensual", "llevamos este mes", "saldo del mes", "vendimos este mes"
    ]):
        return AgentInterpretation(
            intent="consulta_financiera",
            slots={"metric": "ventas_mes", "period": "mes"},
            confidence=0.98,
            raw_text=text,
        )

    # 9.6 Ventas de hoy (incluye modismos colombianos)
    if any(k in t for k in [
        "he vendido hoy", "hemos vendido", "cuánto llevamos", "cuanto llevamos",
        "qué tanto hemos vendido", "que tanto hemos vendido", "cuánto salió hoy", "cuanto salio hoy",
        "van las ventas de hoy", "ventas de hoy", "plata que ha entrado hoy", "va facturado hoy",
        "cuánto vendí hoy", "cuanto vendi hoy", "total vendido hoy", "llevamos vendido",
        "saldo de ventas de hoy", "qué tanto se vendió hoy", "se movió hoy la tienda",
        "se movio hoy la tienda", "cuánto coronamos hoy", "cuanto coronamos hoy",
        "se vendió harto hoy", "se vendio harto hoy", "cuánto vendimos hoy", "cuanto vendimos hoy",
        "cuánto vendimos", "cuanto vendimos", "cuánto hemos vendido", "cuanto hemos vendido",
        "cómo vamos hoy", "como vamos hoy"
    ]):
        return AgentInterpretation(
            intent="consulta_financiera",
            slots={"metric": "ventas_hoy", "period": "hoy"},
            confidence=0.98,
            raw_text=text,
        )

    # 10. Inventario Crítico
    # 10.1 Productos Agotados
    if any(k in t for k in [
        "productos están agotados", "productos estan agotados", "qué se agotó", "que se agoto",
        "qué no hay", "que no hay", "no tienen stock", "tenemos en cero", "existencia cero",
        "productos agotados", "sin existencias", "se acabó en la tienda", "se acabo en la tienda",
        "productos agotados", "productos sin stock", "mercancía está agotada", "mercancia esta agotada",
        "seco en la bodega"
    ]):
        return AgentInterpretation(
            intent="consulta_inventario_critico",
            slots={"action": "agotados"},
            confidence=0.98,
            raw_text=text,
        )

    # 10.2 Productos con Stock Bajo / Crítico
    if any(k in t for k in [
        "stock bajo", "se está acabando", "se esta acabando", "pocas existencias", "toca pedir",
        "qué está escaso", "que esta escaso", "menos de 5 unidades", "por acabarse",
        "existencias bajas", "está escaso mi viejo", "esta escaso mi viejo", "acaban ya mismito"
    ]):
        return AgentInterpretation(
            intent="consulta_inventario_critico",
            slots={"action": "stock_bajo"},
            confidence=0.98,
            raw_text=text,
        )

    # 10.3 Valor Total del Inventario / Total Inventario
    KNOWN_CATALOG_KEYWORDS = ["arroz", "aceite", "cerveza", "pola", "polas", "birra", "birras", "leche", "pan", "gaseosa", "huevos", "jabón", "jabon"]
    if any(k in t for k in [
        "vale mi inventario", "invertido en mercancía", "invertido en mercancia",
        "valor del inventario", "inventario a costo", "dinero hay metido en la tienda",
        "le metimos a la mercancía", "le metimos a la mercancia", "total inventario",
        "cuánto inventario", "cuanto inventario", "cuánto de inventario", "cuanto de inventario",
        "cuánto hay en inventario", "cuanto hay en inventario"
    ]) and not any(kw in t for kw in KNOWN_CATALOG_KEYWORDS):
        return AgentInterpretation(
            intent="consulta_financiera",
            slots={"metric": "total_inventario"},
            confidence=0.98,
            raw_text=text,
        )

    # 11. Productos: Conteo Activo, Precios y Existencia
    # 11.1 Conteo total de productos
    if any(k in t for k in [
        "cuántos productos tenemos", "cuantos productos tenemos", "productos activos hay",
        "total de productos en la tienda", "ítems manejamos", "items manejamos",
        "referencias tenemos", "total de productos", "conteo de productos",
        "productos registrados hay", "cuántos productos vendemos", "cuantos productos vendemos",
        "artículos hay en catálogo", "articulos hay en catalogo"
    ]):
        return AgentInterpretation(
            intent="consulta_productos",
            slots={"action": "conteo"},
            confidence=0.98,
            raw_text=text,
        )

    # 11.2 Búsqueda por código de barras o referencia numérica (ej: 7701234567890)
    m_barcode = re.search(r"\b(770\d{10}|\d{8,14})\b", t)
    if m_barcode:
        bar = m_barcode.group(1)
        return AgentInterpretation(
            intent="consulta_productos",
            slots={"product_query": bar, "action": "precio"},
            confidence=0.98,
            raw_text=text,
        )

    # 11.3 Precios y Consulta de Catálogo
    PRECIOS_TRIGGERS = [
        "a cómo está", "a como esta", "precio de", "precio del", "en cuánto está", "en cuanto esta",
        "cuánto cuesta", "cuanto cuesta", "cuánto vale", "cuanto vale", "a cómo tengo", "a como tengo",
        "en cuánto doy", "en cuanto doy", "a cuánto se vende", "a cuanto se vende", "a cómo me sale",
        "a como me sale", "tengo que dar"
    ]
    for trig in PRECIOS_TRIGGERS:
        if trig in t:
            prod_part = t.split(trig, 1)[1].strip()
            prod_part = re.sub(r"^(el|la|los|las|de|del|un|una)\s+", "", prod_part).strip()
            prod_part = prod_part.replace("?", "").strip()
            # Mapear sinónimos coloquiales
            for col_term, clean_term in SINONIMOS_PRODUCTOS_COL.items():
                if col_term in prod_part:
                    prod_part = prod_part.replace(col_term, clean_term)
            if prod_part:
                return AgentInterpretation(
                    intent="consulta_productos",
                    slots={"product_query": prod_part, "action": "precio"},
                    confidence=0.95,
                    raw_text=text,
                )

    # 11.4 Existencia / Disponibilidad ("¿Tenemos arroz?", "¿Hay leche?", "¿Manejamos pan?")
    m_exist = re.search(r"(?:tenemos|hay|manejamos|se vende|existe el producto)\s+([\w\s\.\-_]+)", t)
    if m_exist and not any(v in t for v in ["vendi", "vendí", "llegaron", "compré", "stock"]):
        prod_q = m_exist.group(1).strip()
        prod_q = re.sub(r"^(el|la|los|las|un|una|acá|aca)\s*", "", prod_q).strip()
        if prod_q and len(prod_q) > 2:
            return AgentInterpretation(
                intent="consulta_productos",
                slots={"product_query": prod_q, "action": "existencia"},
                confidence=0.95,
                raw_text=text,
            )

    # 12. Consultas de Stock Específico
    if any(k in t for k in ["stock", "queda", "quedan", "cuántas", "cuantas", "cuántos", "cuantos", "hay de", "tenemos de", "cuánto inventario", "cuanto inventario"]):
        for kw in KNOWN_CATALOG_KEYWORDS:
            if kw in t and not any(v in t for v in ["vendi", "vendí", "llegaron", "compré", "ayer", "semana"]):
                clean_prod = SINONIMOS_PRODUCTOS_COL.get(kw, kw)
                return AgentInterpretation(intent="consultar_stock", slots={"product_query": clean_prod}, confidence=0.95, raw_text=text)

    m_stock = re.search(r"(?:cuanto|cuánto|cuantos|cuántos|stock|queda|quedan)\s+(?:de\s+|hay\s+de\s+|tenemos\s+de\s+|tengo\s+de\s+|bolsas\s+de\s+|botellas\s+de\s+|paquetes\s+de\s+|unidades\s+hay\s+de\s+|unidades\s+de\s+)?([\w\s\.\-_]+?)(?:\?|$)", t)
    if m_stock and not any(v in t for v in ["vendi", "vendí", "llegaron", "compré", "ayer", "semana"]):
        prod_q = m_stock.group(1).strip()
        prod_q = re.sub(r"\b(tengo|de|el|la|los|las|en nevera|nos queda|disponibles)\b", "", prod_q).strip()
        # Normalizar coloquialismos
        if "cerveza" in prod_q or "cervezas" in prod_q or "pola" in prod_q or "polas" in prod_q or "birra" in prod_q:
            prod_q = "cerveza"
        if prod_q and len(prod_q) > 2 and not any(k in prod_q for k in ["ayer", "semana", "mes", "hoy", "inventario", "tienda", "bodega", "falta", "inversión", "inversion", "ganancia", "ganamos", "recaudo"]):
            return AgentInterpretation(intent="consultar_stock", slots={"product_query": prod_q}, confidence=0.92, raw_text=text)

    # Normalización de números para mutaciones
    t_num = t
    for word_num, digit_val in NUMEROS_TEXTO.items():
        t_num = re.sub(rf"\b{word_num}\b", digit_val, t_num)

    # 13. Venta explícita
    m_venta = re.search(r"(?:vendi|vendí|venta de|facturé|facture)\s+([-\w\.\+]+)\s+(?:de\s+)?([\w\s\.\-_]+)", t_num)
    if m_venta:
        raw_q = m_venta.group(1)
        try:
            qty = float(raw_q)
        except (ValueError, TypeError):
            qty = None
        prod_q = m_venta.group(2).strip()
        for col_term, clean_term in SINONIMOS_PRODUCTOS_COL.items():
            if col_term in prod_q:
                prod_q = prod_q.replace(col_term, clean_term)
        return validate_agent_output(
            raw_intent="registrar_venta",
            raw_slots={"product_query": prod_q, "quantity": qty},
            confidence=0.98,
            raw_text=text,
        )

    # 14. Reabastecimiento explícito
    m_reab = re.search(r"(?:llegaron|llegó|llego|compre|compré|recibí|recibi|entran|entraron)\s+([-\w\.\+]+)\s+(?:de\s+)?([\w\s\.\-_]+)", t_num)
    if m_reab:
        raw_q = m_reab.group(1)
        try:
            qty = float(raw_q)
        except (ValueError, TypeError):
            qty = None
        prod_q = m_reab.group(2).strip()
        for col_term, clean_term in SINONIMOS_PRODUCTOS_COL.items():
            if col_term in prod_q:
                prod_q = prod_q.replace(col_term, clean_term)
        return validate_agent_output(
            raw_intent="reabastecer",
            raw_slots={"product_query": prod_q, "quantity": qty},
            confidence=0.98,
            raw_text=text,
        )

    return None


# ---------------------------------------------------------------------------
# Implementación LLM (Groq / Gemini) con Contexto y Fallback
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """Eres el clasificador de intenciones del sistema POS Gestión Neiva para tiendas de barrio en Colombia.
Tu función es extraer la intención y los slots del mensaje del tendero.
RESPONDE EXCLUSIVAMENTE CON UN JSON VÁLIDO sin markdown ni explicaciones.

INTENCIONES PERMITIDAS:
- "registrar_venta": Vendió uno o más productos.
- "reabastecer": Llegó mercancía / aumentó el stock.
- "consultar_stock": Pregunta cuánto stock queda de un producto específico.
- "consulta_productos": Pregunta precio, catálogo, existencia o conteo total de productos.
- "consulta_inventario_critico": Pregunta por productos agotados (stock 0) o productos con stock bajo.
- "consulta_top_ventas": Pregunta por el producto más vendido o de menor rotación.
- "consulta_financiera": Ventas por período (hoy, ayer, semana, mes), recaudo, transacciones o ventas de un cajero/vendedor.
- "comparacion": Compara ventas entre períodos (hoy vs ayer), productos o vendedores.
- "ambiguo": Frase vaga que no tiene suficiente información ("¿cuánto tenemos?", "¿cómo vamos?", "ventas", "stock").
- "confirmar": El usuario acepta ("sí", "dale", "correcto", "hágale").
- "cancelar": El usuario cancela ("no", "cancela", "descartar").
- "operacion_destructiva": Quiere borrar productos o vaciar inventario.
- "fuera_de_alcance": Conversación general ajena al POS (fútbol, chistes, capitales, recetas, tareas escolares).
- "unknown": Incomprensible.

ESTRUCTURA DE RESPUESTA JSON:
{
  "intent": "...",
  "slots": {
    "product_query": "arroz o null",
    "quantity": 2.0,
    "metric": "ventas_hoy o ventas_ayer o recaudo_actual o null",
    "period": "hoy o ayer o semana o mes o null",
    "seller_name": "Paula o Don Pedro o null",
    "action": "agotados o stock_bajo o conteo o top_ventas o null",
    "comparison_type": "hoy_vs_ayer o productos o vendedores o null"
  },
  "confidence": 0.95
}"""


def _build_context_prompt(context: dict[str, Any] | None) -> str:
    if not context:
        return ""
    b_ctx = context.get("business_context", {})
    if not b_ctx:
        return ""
    return (
        f"\nCONTEXTO PREVIO DEL DIÁLOGO:\n"
        f"- Último dominio: {b_ctx.get('last_domain')}\n"
        f"- Último período: {b_ctx.get('last_period')}\n"
        f"- Último producto: {b_ctx.get('last_product')}\n"
        f"- Último vendedor: {b_ctx.get('last_seller')}\n"
    )


class GroqIntentProvider:
    """Proveedor oficial para Groq Cloud utilizando API compatible con OpenAI."""

    def __init__(self, model: str | None = None):
        self.provider = "groq"
        # Prioridad: LLM_MODEL -> AI_MODEL -> 'openai/gpt-oss-120b'
        self.model = model or os.getenv("LLM_MODEL") or os.getenv("AI_MODEL") or "openai/gpt-oss-120b"

    def parse(self, text: str, context: dict[str, Any] | None = None) -> AgentInterpretation:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            AGENT_TELEMETRY["llm_provider_failure"] += 1
            logger.error("Error al invocar LLM IntentProvider (groq): GROQ_API_KEY no está configurada")
            raise LLMProviderUnavailableError(
                provider="groq",
                reason="GROQ_API_KEY no está configurada en las variables de entorno.",
            )

        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            ctx_prompt = _build_context_prompt(context)
            prompt = f"{ctx_prompt}\nMENSAJE DEL TENDERO:\n{text}"
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or "{}"
            AGENT_TELEMETRY["llm_provider_success"] += 1
        except Exception as exc:
            AGENT_TELEMETRY["llm_provider_failure"] += 1
            logger.error("Error al invocar LLM IntentProvider (groq): %s", exc)
            raise LLMProviderUnavailableError(
                provider="groq",
                reason=f"Falla de comunicación con Groq ({type(exc).__name__}): {exc}",
            ) from exc

        try:
            data = json.loads(content)
        except Exception as json_err:
            AGENT_TELEMETRY["intent_parse_failure"] += 1
            logger.warning("Groq retornó JSON inválido: %s", content)
            return AgentInterpretation(intent="unknown", raw_text=text, confidence=0.0)

        interp = validate_agent_output(
            raw_intent=data.get("intent", "unknown"),
            raw_slots=data.get("slots", {}),
            raw_missing=data.get("missing_slots", []),
            confidence=float(data.get("confidence", 0.8)),
            raw_text=text,
        )
        if interp.intent == "unknown":
            AGENT_TELEMETRY["intent_parse_failure"] += 1
        else:
            AGENT_TELEMETRY["intent_parse_success"] += 1

        return interp


class GeminiIntentProvider:
    """Proveedor aislado para Google Gemini (sin mezclar modelos ni fallback cruzado)."""

    def __init__(self, model: str | None = None):
        self.provider = "gemini"
        # Prioridad: LLM_MODEL -> AI_MODEL -> GEMINI_MODEL -> 'gemini-2.5-flash'
        self.model = model or os.getenv("LLM_MODEL") or os.getenv("AI_MODEL") or os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"

    def parse(self, text: str, context: dict[str, Any] | None = None) -> AgentInterpretation:
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            AGENT_TELEMETRY["llm_provider_failure"] += 1
            logger.error("Error al invocar LLM IntentProvider (gemini): GOOGLE_API_KEY/GEMINI_API_KEY no configurada")
            raise LLMProviderUnavailableError(
                provider="gemini",
                reason="GOOGLE_API_KEY o GEMINI_API_KEY no está configurada en las variables de entorno.",
            )

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model_inst = genai.GenerativeModel(self.model)
            ctx_prompt = _build_context_prompt(context)
            full_prompt = f"{_SYSTEM_PROMPT}\n{ctx_prompt}\nMENSAJE DEL TENDERO:\n{text}"
            response = model_inst.generate_content(full_prompt)
            content = response.text.strip()
            if content.startswith("```"):
                lines = [l for l in content.split("\n") if not l.strip().startswith("```")]
                content = "\n".join(lines).strip()
            AGENT_TELEMETRY["llm_provider_success"] += 1
        except Exception as exc:
            AGENT_TELEMETRY["llm_provider_failure"] += 1
            logger.error("Error al invocar LLM IntentProvider (gemini): %s", exc)
            raise LLMProviderUnavailableError(
                provider="gemini",
                reason=f"Falla de comunicación con Gemini ({type(exc).__name__}): {exc}",
            ) from exc

        try:
            data = json.loads(content)
        except Exception as json_err:
            AGENT_TELEMETRY["intent_parse_failure"] += 1
            logger.warning("Gemini retornó JSON inválido: %s", content)
            return AgentInterpretation(intent="unknown", raw_text=text, confidence=0.0)

        interp = validate_agent_output(
            raw_intent=data.get("intent", "unknown"),
            raw_slots=data.get("slots", {}),
            raw_missing=data.get("missing_slots", []),
            confidence=float(data.get("confidence", 0.8)),
            raw_text=text,
        )
        if interp.intent == "unknown":
            AGENT_TELEMETRY["intent_parse_failure"] += 1
        else:
            AGENT_TELEMETRY["intent_parse_success"] += 1

        return interp


class LLMIntentProvider:
    """Proveedor orquestador de intenciones: determinístico rápido + LLM aislado."""

    def __init__(self, provider: str = "groq", model: str | None = None):
        self.provider = (provider or "groq").lower().strip()
        self.model = model
        if self.provider == "gemini":
            self._llm: Any = GeminiIntentProvider(model=model)
        else:
            self._llm = GroqIntentProvider(model=model)

    def parse(self, text: str, context: dict[str, Any] | None = None) -> AgentInterpretation:
        # 1. Intentar el parser semántico determinístico primero
        quick = quick_parse_intent(text, context=context)
        if quick:
            return quick

        # 2. Si hay contexto de aclaración pendiente
        if context and context.get("estado") == "NEEDS_CLARIFICATION":
            missing = context.get("missing_slots", [])
            clar_opts = context.get("clarification_options", {})

            # A. Si falta cantidad y el usuario envía un número
            if "cantidad" in missing:
                m_num = re.search(r"^(\d+(?:\.\d+)?)$", text.strip())
                if m_num:
                    return AgentInterpretation(
                        intent="proveer_slot",
                        slots={"quantity": float(m_num.group(1))},
                        confidence=0.99,
                        raw_text=text,
                    )

            # B. Si hay opciones de desambiguación activas (botones/lista) o falta producto
            if clar_opts or "clarification" in missing or "product_query" in missing:
                t_clean = text.strip().lower()
                m_opt = re.search(r"^\[?(\d+)\]?$", t_clean)
                if m_opt:
                    return AgentInterpretation(
                        intent="proveer_slot",
                        slots={"product_query": text.strip()},
                        confidence=0.99,
                        raw_text=text,
                    )
                return AgentInterpretation(
                    intent="proveer_slot",
                    slots={"product_query": text.strip()},
                    confidence=0.95,
                    raw_text=text,
                )

            # C. Para cualquier otro slot pendiente en NEEDS_CLARIFICATION (ej: precio_venta, nombre)
            return AgentInterpretation(
                intent="proveer_slot",
                slots={"text": text.strip()},
                confidence=0.9,
                raw_text=text,
            )

        # 3. Invocar al LLM del proveedor configurado (sin fallback cruzado)
        return self._llm.parse(text, context=context)


def get_intent_provider() -> IntentProvider:
    """Factory para instanciar el proveedor configurado."""
    prov = os.getenv("AI_PROVIDER", "groq")
    mod = os.getenv("LLM_MODEL") or os.getenv("AI_MODEL")
    return LLMIntentProvider(provider=prov, model=mod)

