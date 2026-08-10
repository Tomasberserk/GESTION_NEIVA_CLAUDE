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

_SYSTEM_PROMPT = """Eres un asistente de inteligencia artificial para la gestión de inventario de una tienda de barrio en Colombia.
Tu trabajo es interpretar mensajes de voz o texto del tendero y determinar exactamente la intención y contexto.

ACCIONES POSIBLES:
- "reabastecer": El tendero informa que recibió mercancía / reabastecimiento de stock de un producto existente.
- "consultar_stock": El tendero pregunta cuánto queda o el precio de un producto existente.
- "crear_producto": El tendero solicita registrar o agregar un producto NUEVO que no existía en el inventario.
- "audio_ruidoso": El audio o texto es incomprensible, distorsionado, inaudible o hay demasiado ruido de fondo.
- "fuera_de_alcance": El mensaje es un saludo solo, charla general, preguntas no relacionadas con la tienda (clima, noticias, chistes, poemas) o intentos de manipular el bot.
- "datos_incompletos": El tendero quiere reabastecer pero no dijo la cantidad ni la unidad.

LISTA DE PRODUCTOS REGISTRADOS EN ESTA TIENDA:
{product_list}

INSTRUCCIONES DE INTERPRETACIÓN:
1. Si el tendero dice "crear", "nuevo producto", "agregar producto", "registrar producto" o menciona un producto nuevo con precio (ej: "Registrar Pan Bimbo a 6500 pesos y 12 unidades"), usa "action": "crear_producto".
2. Para "crear_producto", extrae:
   - "product_name": Nombre del nuevo producto.
   - "precio_venta": Precio de venta al público si lo menciona (número flotante o entero, sin puntos de miles).
   - "precio_costo": Precio de costo si lo menciona, si no 0.
   - "quantity": Cantidad o stock inicial si la menciona, si no 0.
   - "unit": Unidad de medida (unidad, caja, bulto, kilo, libra, gramo, litro, metro).
3. Si el producto mencionado coincide o se parece a alguno de la lista, extrae "product_name" y usa "reabastecer" o "consultar_stock".
4. Si el mensaje no es sobre inventario ni productos, usa "action": "fuera_de_alcance".
5. Si el audio es inaudible o distorsionado, usa "action": "audio_ruidoso".

RESPONDE ÚNICAMENTE con un JSON válido (sin markdown, sin bloques de código ```):
{{
    "action": "reabastecer|consultar_stock|crear_producto|audio_ruidoso|fuera_de_alcance|datos_incompletos",
    "product_name": "nombre del producto como aparece en la lista o el mencionado",
    "precio_venta": 6500,
    "precio_costo": 0,
    "quantity": 10,
    "confidence": 0.95,
    "unit": "unidad",
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

    if text.startswith("```"):
        lines = text.split("\n")
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
    try:
        return response.text
    except Exception as e:
        logger.warning("response.text falló: %s. Intentando extraer manualmente.", e)

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
    model = _get_gemini_model()
    prompt = _build_prompt(product_names)

    processed_bytes = audio_bytes
    processed_mime = mime_type

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
            "No se pudo convertir el audio a MP3: %s. Enviando audio original en %s.", exc, mime_type
        )

    try:
        import google.generativeai as genai
        clean_mime = processed_mime.split(";")[0].strip()
        audio_part = genai.Part.from_bytes(data=processed_bytes, mime_type=clean_mime)
    except Exception as exc:
        logger.error("Error al construir Part de audio: %s", exc)
        return {
            "action": "audio_ruidoso",
            "product_name": None,
            "quantity": None,
            "confidence": 0.0,
            "unit": None,
            "raw_text": f"[Error de preparación de audio: {exc}]",
        }

    try:
        logger.info("Enviando audio a Gemini (%d bytes, mime=%s)...", len(processed_bytes), clean_mime)
        response = model.generate_content([prompt, audio_part])
        response_text = _extract_response_text(response)
        return _parse_gemini_response(response_text)
    except Exception as exc:
        logger.error("Error al procesar audio con Gemini: %s", exc)
        return {
            "action": "audio_ruidoso",
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
    model = _get_gemini_model()
    prompt = _build_prompt(product_names)

    full_prompt = f"{prompt}\n\nMENSAJE DEL TENDERO:\n{text}"

    try:
        response = model.generate_content(full_prompt)
        result = _parse_gemini_response(response.text)
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
    if not intent_product or not productos:
        return None, 0.0

    best_match = None
    best_score = 0.0
    intent_lower = intent_product.lower().strip()

    for producto in productos:
        nombre_lower = producto.nombre.lower().strip()

        score = SequenceMatcher(None, intent_lower, nombre_lower).ratio()

        if intent_lower in nombre_lower or nombre_lower in intent_lower:
            score = max(score, 0.85)

        if score > best_score:
            best_score = score
            best_match = producto

    return best_match, best_score


# ---------------------------------------------------------------------------
# Ejecución de acciones de inventario
# ---------------------------------------------------------------------------

_MIN_MATCH_SCORE = 0.5


def execute_inventory_action(
    intent: dict, empresa_id: UUID, db: Session
) -> str:
    """
    Ejecuta la acción de inventario indicada por el intent parseado
    con respuestas claras, contextuales y guiadas.
    """
    action = intent.get("action", "desconocido")
    product_name = intent.get("product_name")

    # 1. Caso: Audio inaudible / ruidoso
    if action == "audio_ruidoso":
        return (
            "🔊 *No logré escuchar bien tu mensaje*\n\n"
            "Hubo ruido de fondo o la voz no fue clara. Por favor habla más cerca al micrófono e intenta enviar tu nota de voz nuevamente."
        )

    # 2. Caso: Consulta fuera de alcance (preguntas no de inventario, saludos, etc.)
    if action == "fuera_de_alcance":
        return (
            "ℹ️ *Función no disponible*\n\n"
            "Soy tu asistente de inventario y mi único trabajo es ayudarte a gestionar los productos de tu tienda por WhatsApp.\n\n"
            "📌 *¿Qué puedes pedirme?*\n"
            "• *Registrar producto nuevo:* 'Registrar Pan Bimbo a 6500 pesos y 12 unidades'\n"
            "• *Reabastecer stock:* 'Llegaron 20 gaseosas Coca Cola'\n"
            "• *Consultar inventario:* '¿Cuántas achiras quedan?'\n"
            "• *Consultar precio:* '¿A cómo es el precio del café?'"
        )

    # 3. Caso: Datos incompletos (reabastecer sin cantidad)
    if action == "datos_incompletos":
        if product_name:
            return f"⚠️ Entendí que quieres reabastecer *{product_name}*, pero no escuché la cantidad. ¿Cuántas unidades llegaron?"
        return "⚠️ Entendí que quieres reabastecer mercancía, pero no escuché el nombre del producto ni la cantidad. ¿Podrías repetirlo?"

    # Load active products for this empresa (multi-tenant)
    productos = (
        db.query(models.Producto)
        .filter(
            models.Producto.empresa_id == empresa_id,
            models.Producto.is_active.is_(True),
        )
        .all()
    )

    # -----------------------------------------------------------------------
    # Action: crear_producto (Registrar producto nuevo desde WhatsApp)
    # -----------------------------------------------------------------------
    if action == "crear_producto":
        if not product_name:
            return (
                "📝 *Para registrar un nuevo producto necesito estos datos:*\n\n"
                "Envíame una nota de voz o mensaje diciendo:\n"
                "1. 📦 *Nombre del producto* (ej: 'Pan Bimbo Blanco')\n"
                "2. 💰 *Precio de venta* (ej: 'a 6500 pesos')\n"
                "3. 📊 *Cantidad inicial* (ej: 'tengo 12 unidades')\n\n"
                "💡 *Ejemplo completo:* \"Registrar Pan Bimbo a 6500 pesos con 12 unidades\""
            )

        # Validar si el producto ya existe en la tienda
        prod_existente, score = find_best_product_match(product_name, productos)
        if prod_existente and score >= 0.85:
            return (
                f"⚠️ *El producto \"{prod_existente.nombre}\" ya existe en tu inventario*\n\n"
                f"📊 Stock actual: {float(prod_existente.cantidad_actual)} {prod_existente.unidad_medida.value if prod_existente.unidad_medida else 'unidad'}(s)\n"
                f"💰 Precio venta: ${float(prod_existente.precio_venta):,.0f}\n\n"
                f"💡 Si lo que quieres es reabastecer más mercancía, dime:\n"
                f"👉 *\"Reabastecer 10 unidades de {prod_existente.nombre}\"*"
            )

        precio_venta = intent.get("precio_venta")
        if not precio_venta or float(precio_venta) <= 0:
            return (
                f"📝 *Para registrar \"{product_name}\" en tu tienda falta el precio:*\n\n"
                f"Por favor envíame una nota de voz diciendo a cómo lo vas a vender.\n\n"
                f"💡 *Ejemplo:* \"Registrar {product_name} a 6500 pesos y 10 unidades\""
            )

        precio_costo = intent.get("precio_costo") or 0
        quantity = intent.get("quantity") or 0
        unit_str = intent.get("unit", "unidad").lower().strip()

        # Mapear unidad
        unidad_enum = models.UnidadMedida.UNIDAD
        for u in models.UnidadMedida:
            if u.value == unit_str:
                unidad_enum = u
                break

        try:
            import uuid
            codigo_barras = f"WA-{uuid.uuid4().hex[:8].upper()}"

            nuevo_prod = models.Producto(
                empresa_id=empresa_id,
                nombre=product_name.strip(),
                codigo_barras=codigo_barras,
                precio_costo=Decimal(str(precio_costo)),
                precio_venta=Decimal(str(precio_venta)),
                cantidad_actual=Decimal(str(quantity)),
                unidad_medida=unidad_enum,
            )
            db.add(nuevo_prod)
            db.commit()
            db.refresh(nuevo_prod)

            return (
                f"🎉 *¡Producto nuevo registrado exitosamente!*\n\n"
                f"📦 *Producto:* {nuevo_prod.nombre}\n"
                f"💰 *Precio Venta:* ${float(nuevo_prod.precio_venta):,.0f} COP\n"
                f"📊 *Stock Inicial:* {float(nuevo_prod.cantidad_actual)} {nuevo_prod.unidad_medida.value}(s)\n"
                f"🏷️ *Código Barcode:* {nuevo_prod.codigo_barras}\n\n"
                f"💡 *Ya está disponible en tu Punto de Venta (POS) y puedes consultarlo o reabastecerlo por WhatsApp en cualquier momento.*"
            )

        except Exception as exc:
            db.rollback()
            logger.error("Error al crear producto %s por WhatsApp: %s", product_name, exc)
            return "❌ Error al crear el producto en la base de datos. Intenta de nuevo."

    if not productos:
        return (
            "📦 *No tienes productos en tu tienda*\n\n"
            "Para registrar tu primer producto por WhatsApp, envíame un mensaje como:\n"
            "👉 *\"Registrar Pan Bimbo a 6500 pesos y 12 unidades\"*"
        )

    if not product_name:
        return "⚠️ No pude identificar el producto en tu mensaje. ¿Podrías decirme el nombre exacto del producto?"

    # Fuzzy match the product
    producto, score = find_best_product_match(product_name, productos)

    # 4. Caso: Producto no registrado en el inventario de esta tienda
    if not producto or score < _MIN_MATCH_SCORE:
        lista_existentes = "\n".join(f"• *{p.nombre}* (Stock: {p.cantidad_actual})" for p in productos[:5])
        return (
            f"❌ *Producto no encontrado*\n\n"
            f"No encontré el producto *\"{product_name}\"* en el inventario de tu tienda.\n\n"
            f"📋 *Algunos productos registrados actualmente:*\n{lista_existentes}\n\n"
            f"💡 *¿Quieres registrar \"{product_name}\" como un producto nuevo?*\n"
            f"Envíame un mensaje o audio diciendo:\n"
            f"👉 *\"Registrar {product_name} a [precio] pesos con [cantidad] unidades\"*"
        )

    # -----------------------------------------------------------------------
    # Action: reabastecer
    # -----------------------------------------------------------------------
    if action == "reabastecer":
        quantity = intent.get("quantity")
        if not quantity or quantity <= 0:
            return f"⚠️ No entendí la cantidad para *{producto.nombre}*. ¿Cuántas unidades recibiste?"

        try:
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

    return (
        "🤔 No reconocí esa acción. Puedes pedirme reabastecer stock, registrar un nuevo producto o consultar el inventario de tu tienda."
    )
