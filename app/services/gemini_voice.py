"""
Servicio de procesamiento de voz/texto con Google Gemini.

Usa la API multimodal de Gemini para:
- Transcribir audio y extraer intención de inventario
- Parsear mensajes de texto con intención de inventario
- Hacer fuzzy matching de nombres de productos
- Ejecutar acciones de inventario (reabastecer, consultar stock)
"""

import json
import logging
import os
from decimal import Decimal
from difflib import SequenceMatcher
from uuid import UUID

from sqlalchemy.orm import Session

from app import models

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuración de Gemini (lazy — no falla al importar si falta la key)
# ---------------------------------------------------------------------------

_gemini_model = None


def _get_gemini_model():
    """Inicializa el modelo Gemini de forma lazy. Falla solo al llamar, no al importar."""
    global _gemini_model
    if _gemini_model is not None:
        return _gemini_model

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY no está configurada en las variables de entorno. "
            "Configúrala para usar el asistente de voz."
        )

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        _gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        logger.info("Modelo Gemini 2.0 Flash inicializado correctamente")
        return _gemini_model
    except Exception as exc:
        logger.error("Error al inicializar Gemini: %s", exc)
        raise RuntimeError(f"No se pudo inicializar Gemini: {exc}") from exc


# ---------------------------------------------------------------------------
# Prompt del sistema para extracción de intención
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """Eres un asistente de inventario para una tienda de barrio en Colombia.
Tu trabajo es interpretar mensajes de voz o texto del tendero y extraer la intención.

ACCIONES POSIBLES:
- "reabastecer": El tendero informa que recibió mercancía / reabastecimiento de stock.
- "consultar_stock": El tendero pregunta cuánto queda de un producto.
- "desconocido": No se entiende la intención o no es una acción de inventario.

LISTA DE PRODUCTOS DISPONIBLES EN ESTA TIENDA:
{product_list}

INSTRUCCIONES:
1. Identifica la acción que quiere realizar el tendero.
2. Identifica el producto mencionado. Usa el nombre más parecido de la lista de productos.
3. Si es reabastecimiento, extrae la cantidad. Si no se menciona cantidad, usa 1.
4. Determina la unidad (unidad, caja, bulto, kilo, libra, gramo, litro, metro).
5. Asigna un nivel de confianza entre 0.0 y 1.0.

RESPONDE ÚNICAMENTE con un JSON válido (sin markdown, sin explicación):
{{
    "action": "reabastecer",
    "product_name": "nombre del producto como aparece en la lista",
    "quantity": 10,
    "confidence": 0.95,
    "unit": "unidad",
    "raw_text": "texto original transcrito"
}}

Si no entiendes el mensaje o no es sobre inventario, responde:
{{
    "action": "desconocido",
    "product_name": null,
    "quantity": null,
    "confidence": 0.0,
    "unit": null,
    "raw_text": "texto original transcrito"
}}"""


def _build_prompt(product_names: list[str]) -> str:
    """Construye el prompt del sistema con la lista de productos de la tienda."""
    if product_names:
        product_list = "\n".join(f"- {name}" for name in product_names)
    else:
        product_list = "(No hay productos registrados en esta tienda)"
    return _SYSTEM_PROMPT.format(product_list=product_list)


def _parse_gemini_response(response_text: str) -> dict:
    """Parsea la respuesta JSON de Gemini. Maneja respuestas con markdown wrapping."""
    text = response_text.strip()

    # Remove markdown code block wrapping if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json or ```) and last line (```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.warning("Gemini devolvió respuesta no-JSON: %s", text[:200])
        return {
            "action": "desconocido",
            "product_name": None,
            "quantity": None,
            "confidence": 0.0,
            "unit": None,
            "raw_text": text,
        }


# ---------------------------------------------------------------------------
# Transcripción de audio + parsing de intención
# ---------------------------------------------------------------------------

def _extract_response_text(response) -> str:
    """
    Extrae el texto de la respuesta de Gemini de forma segura,
    manejando casos de safety filters o respuestas vacías.
    """
    try:
        # Intento directo
        return response.text
    except Exception as e:
        logger.warning("response.text falló: %s. Intentando extraer manualmente.", e)

    # Intento manual revisando candidatos
    if not hasattr(response, "candidates") or not response.candidates:
        raise RuntimeError("Gemini no devolvió candidatos (posible bloqueo por safety)")

    candidate = response.candidates[0]
    if hasattr(candidate, "finish_reason") and candidate.finish_reason.name == "SAFETY":
        raise RuntimeError("Respuesta bloqueada por filtros de seguridad de Gemini")

    try:
        parts = candidate.content.parts
        text_parts = [p.text for p in parts if hasattr(p, "text")]
        return "".join(text_parts)
    except Exception as e:
        raise RuntimeError(f"No se pudo extraer texto de la respuesta: {e}")


def transcribe_and_parse(audio_bytes: bytes, mime_type: str, product_names: list[str]) -> dict:
    """
    Envía audio directamente a Gemini (multimodal) con contexto de productos.
    Intenta convertir a MP3 usando pydub para máxima estabilidad, y si falla,
    envía el formato original usando Part.from_bytes.

    Args:
        audio_bytes: Bytes del archivo de audio (ogg/opus de WhatsApp).
        mime_type: Mime type del archivo de audio.
        product_names: Lista de nombres de productos de la tienda para contexto.

    Returns:
        dict con action, product_name, quantity, confidence, unit, raw_text.
    """
    model = _get_gemini_model()
    prompt = _build_prompt(product_names)

    processed_bytes = audio_bytes
    processed_mime = mime_type

    # 1️⃣ Intentar convertir a MP3 usando pydub + ffmpeg si están disponibles
    try:
        from pydub import AudioSegment
        import io

        fmt = "ogg" if "ogg" in mime_type else None
        if fmt:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format=fmt)
        else:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))

        audio = audio.set_channels(1).set_frame_rate(16000)
        output_buffer = io.BytesIO()
        audio.export(output_buffer, format="mp3", bitrate="64k")
        processed_bytes = output_buffer.getvalue()
        processed_mime = "audio/mp3"
        logger.info("Conversión de audio a MP3 exitosa (%d bytes)", len(processed_bytes))
    except Exception as exc:
        logger.warning(
            "No se pudo convertir el audio a MP3 (¿falta ffmpeg o pydub?): %s. "
            "Se enviará el audio original en formato %s.", exc, mime_type
        )

    # 2️⃣ Construir Part explícito (más robusto que dict)
    try:
        import google.generativeai as genai
        clean_mime = processed_mime.split(";")[0].strip()
        audio_part = genai.Part.from_bytes(data=processed_bytes, mime_type=clean_mime)
    except Exception as exc:
        logger.error("Error al construir Part de audio: %s", exc)
        return {
            "action": "desconocido",
            "product_name": None,
            "quantity": None,
            "confidence": 0.0,
            "unit": None,
            "raw_text": f"[Error de preparación de audio: {exc}]",
        }

    # 3️⃣ Llamar a Gemini
    try:
        logger.info("Enviando audio a Gemini (%d bytes, mime=%s)...", len(processed_bytes), clean_mime)
        response = model.generate_content([prompt, audio_part])
        response_text = _extract_response_text(response)
        return _parse_gemini_response(response_text)
    except Exception as exc:
        logger.error("Error al procesar audio con Gemini: %s", exc)
        return {
            "action": "desconocido",
            "product_name": None,
            "quantity": None,
            "confidence": 0.0,
            "unit": None,
            "raw_text": f"[Error de transcripción: {exc}]",
        }


# ---------------------------------------------------------------------------
# Parsing de intención desde texto
# ---------------------------------------------------------------------------

def parse_text_intent(text: str, product_names: list[str]) -> dict:
    """
    Parsea la intención de un mensaje de texto usando Gemini.

    Args:
        text: Mensaje de texto del tendero.
        product_names: Lista de nombres de productos de la tienda.

    Returns:
        dict con action, product_name, quantity, confidence, unit, raw_text.
    """
    model = _get_gemini_model()
    prompt = _build_prompt(product_names)

    full_prompt = f"{prompt}\n\nMENSAJE DEL TENDERO:\n{text}"

    try:
        response = model.generate_content(full_prompt)
        result = _parse_gemini_response(response.text)
        # Ensure raw_text reflects the original input
        result["raw_text"] = text
        return result

    except Exception as exc:
        logger.error("Error al procesar texto con Gemini: %s", exc)
        return {
            "action": "desconocido",
            "product_name": None,
            "quantity": None,
            "confidence": 0.0,
            "unit": None,
            "raw_text": text,
        }


# ---------------------------------------------------------------------------
# Fuzzy matching de productos
# ---------------------------------------------------------------------------

def find_best_product_match(
    intent_product: str, productos: list
) -> tuple[object | None, float]:
    """
    Busca el producto que mejor coincide con el nombre del intent usando
    fuzzy matching (difflib.SequenceMatcher).

    Args:
        intent_product: Nombre del producto extraído por Gemini.
        productos: Lista de objetos Producto del ORM.

    Returns:
        Tupla (producto_mejor_match, score). Si no hay match, (None, 0.0).
    """
    if not intent_product or not productos:
        return None, 0.0

    best_match = None
    best_score = 0.0
    intent_lower = intent_product.lower().strip()

    for producto in productos:
        nombre_lower = producto.nombre.lower().strip()

        # Direct SequenceMatcher comparison
        score = SequenceMatcher(None, intent_lower, nombre_lower).ratio()

        # Boost: if the intent is a substring of the product name or vice versa
        if intent_lower in nombre_lower or nombre_lower in intent_lower:
            score = max(score, 0.85)

        if score > best_score:
            best_score = score
            best_match = producto

    return best_match, best_score


# ---------------------------------------------------------------------------
# Ejecución de acciones de inventario
# ---------------------------------------------------------------------------

# Minimum fuzzy match score to accept a product match
_MIN_MATCH_SCORE = 0.5


def execute_inventory_action(
    intent: dict, empresa_id: UUID, db: Session
) -> str:
    """
    Ejecuta la acción de inventario indicada por el intent parseado.

    Args:
        intent: Dict con action, product_name, quantity, unit, confidence.
        empresa_id: UUID de la empresa (multi-tenant).
        db: Sesión de SQLAlchemy.

    Returns:
        Mensaje de respuesta en español para enviar al tendero por WhatsApp.
    """
    action = intent.get("action", "desconocido")

    if action == "desconocido":
        return (
            "🤔 No entendí tu mensaje. Puedes decirme cosas como:\n"
            "• \"Llegaron 20 papeles higiénicos\"\n"
            "• \"Cuántas gaseosas hay?\"\n"
            "• \"Reabastecí 5 cajas de leche\""
        )

    # Load active products for this empresa (multi-tenant)
    productos = (
        db.query(models.Producto)
        .filter(
            models.Producto.empresa_id == empresa_id,
            models.Producto.is_active.is_(True),
        )
        .all()
    )

    if not productos:
        return (
            "⚠️ No tienes productos registrados en el sistema. "
            "Primero agrega productos desde la aplicación web."
        )

    product_name = intent.get("product_name")
    if not product_name:
        return "⚠️ No pude identificar el producto. ¿Podrías repetir el nombre del producto?"

    # Fuzzy match the product
    producto, score = find_best_product_match(product_name, productos)

    if not producto or score < _MIN_MATCH_SCORE:
        return (
            f"❌ No encontré un producto parecido a \"{product_name}\" en tu inventario.\n"
            "Verifica el nombre e intenta de nuevo."
        )

    # -----------------------------------------------------------------------
    # Action: reabastecer
    # -----------------------------------------------------------------------
    if action == "reabastecer":
        quantity = intent.get("quantity")
        if not quantity or quantity <= 0:
            return "⚠️ No entendí la cantidad. ¿Cuántas unidades recibiste?"

        try:
            # Lock the row to prevent race conditions (with explicit multi-tenant filter)
            producto_locked = (
                db.query(models.Producto)
                .filter(
                    models.Producto.id == producto.id,
                    models.Producto.empresa_id == empresa_id,
                )
                .with_for_update()
                .first()
            )

            if producto_locked is None:
                db.rollback()
                return "❌ El producto no pertenece a tu tienda."

            stock_anterior = float(producto_locked.cantidad_actual)
            producto_locked.cantidad_actual += Decimal(str(quantity))
            db.commit()
            db.refresh(producto_locked)

            unit = intent.get("unit", "unidad")
            match_info = f" (coincidencia: {score:.0%})" if score < 0.95 else ""

            return (
                f"✅ *Reabastecimiento registrado*{match_info}\n"
                f"📦 Producto: {producto_locked.nombre}\n"
                f"➕ Cantidad agregada: {quantity} {unit}(s)\n"
                f"📊 Stock anterior: {stock_anterior}\n"
                f"📊 Stock actual: {float(producto_locked.cantidad_actual)}"
            )

        except Exception as exc:
            db.rollback()
            logger.error("Error al reabastecer %s: %s", producto.nombre, exc)
            return "❌ Error al actualizar el inventario. Intenta de nuevo."

    # -----------------------------------------------------------------------
    # Action: consultar_stock
    # -----------------------------------------------------------------------
    if action == "consultar_stock":
        match_info = f" (coincidencia: {score:.0%})" if score < 0.95 else ""
        stock = float(producto.cantidad_actual)
        unidad = producto.unidad_medida.value if producto.unidad_medida else "unidad"

        # Stock level indicator
        if stock <= 0:
            nivel = "🔴 SIN STOCK"
        elif stock <= 5:
            nivel = "🟡 Stock bajo"
        else:
            nivel = "🟢 Stock OK"

        return (
            f"📋 *Consulta de stock*{match_info}\n"
            f"📦 Producto: {producto.nombre}\n"
            f"📊 Cantidad: {stock} {unidad}(s)\n"
            f"💰 Precio venta: ${float(producto.precio_venta):,.0f}\n"
            f"📍 Estado: {nivel}"
        )

    # Fallback for unexpected action values
    return "🤔 Acción no reconocida. Intenta de nuevo."
