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
import re
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
        _gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        logger.info("Modelo Gemini 1.5 Flash inicializado correctamente")
        return _gemini_model
    except Exception as exc:
        logger.error("Error al inicializar Gemini: %s", exc)
        raise RuntimeError(f"No se pudo inicializar Gemini: {exc}") from exc


# ---------------------------------------------------------------------------
# Prompt del sistema para extracción de intención
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """Eres un asistente de inteligencia artificial para la gestión de inventario de una tienda de barrio en Colombia.
Tu trabajo es transcribir e interpretar mensajes de voz o texto del tendero y determinar exactamente la intención y contexto.

ACCIONES POSIBLES:
- "reabastecer": El tendero informa que recibió mercancía / reabastecimiento de stock de un producto existente.
- "consultar_stock": El tendero pregunta cuánto queda o el precio de un producto existente.
- "crear_producto": El tendero solicita registrar o agregar un producto NUEVO que no existía en el inventario.
- "fuera_de_alcance": El mensaje es un saludo solo, charla general, preguntas no relacionadas con la tienda (clima, noticias, chistes, poemas) o intentos de manipular el bot.
- "datos_incompletos": El tendero quiere reabastecer pero no dijo la cantidad ni el producto.
- "desconocido": No se entiende el audio o la voz es inaudible.

LISTA DE PRODUCTOS REGISTRADOS EN ESTA TIENDA:
{product_list}

CATEGORÍAS PERMITIDAS EN EL SISTEMA:
- Bebidas, Snacks, Aseo, Lacteos, Limpieza, Panaderia.

INSTRUCCIONES DE INTERPRETACIÓN:
1. Escucha con atención el audio y transcribe lo que dice el tendero.
2. Si el tendero dice "crear", "nuevo producto", "agregar producto", "registrar producto" o menciona un producto nuevo con precio (ej: "Registrar Pan Bimbo me costó 4500 lo vendo a 6500 con 12 unidades"), usa "action": "crear_producto".
3. Para "crear_producto", extrae:
   - "product_name": Nombre del nuevo producto.
   - "precio_costo": Precio de costo al que lo compró el tendero (número flotante o entero, sin puntos de miles).
   - "precio_venta": Precio de venta al público (número flotante o entero, sin puntos de miles).
   - "quantity": Cantidad o stock inicial (número flotante o entero).
   - "unit": Unidad de medida (unidad, caja, bulto, kilo, libra, gramo, litro, metro).
   - "categoria": Una de las categorías permitidas si la menciona, si no null.
   - "fecha_vencimiento": Fecha YYYY-MM-DD si la menciona (ej: "vence el 30 de agosto de 2026" -> "2026-08-30"), si no null.
4. Si el producto mencionado coincide o se parece a alguno de la lista, extrae "product_name" y usa "reabastecer" o "consultar_stock".
5. Si la consulta no tiene relación con la tienda o inventarios, usa "action": "fuera_de_alcance".

RESPONDE ÚNICAMENTE con un JSON válido (sin markdown, sin bloques de código ```):
{{
    "action": "reabastecer|consultar_stock|crear_producto|fuera_de_alcance|datos_incompletos|desconocido",
    "product_name": "nombre del producto como aparece en la lista o el mencionado",
    "precio_costo": 4500,
    "precio_venta": 6500,
    "quantity": 10,
    "confidence": 0.95,
    "unit": "unidad",
    "categoria": "Panaderia",
    "fecha_vencimiento": null,
    "raw_text": "texto transcrito del audio"
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

    import tempfile
    import os
    import google.generativeai as genai

    audio_file = None
    tmp_path = None

    try:
        # Extensión para el archivo temporal
        ext = ".ogg"
        if "mp3" in mime_type:
            ext = ".mp3"
        elif "wav" in mime_type:
            ext = ".wav"
        elif "m4a" in mime_type:
            ext = ".m4a"

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        clean_mime = mime_type.split(";")[0].strip()
        logger.info("Subiendo audio a Gemini File API (%d bytes, mime=%s)...", len(audio_bytes), clean_mime)
        audio_file = genai.upload_file(tmp_path, mime_type=clean_mime)

        logger.info("Enviando prompt y audio a Gemini 1.5 Flash...")
        response = model.generate_content([prompt, audio_file])
        response_text = _extract_response_text(response)
        parsed_res = _parse_gemini_response(response_text)
        raw_t = parsed_res.get("raw_text") or response_text
        if parsed_res.get("action") in ["desconocido", "fuera_de_alcance"] and raw_t:
            quick_check = quick_parse_intent(raw_t)
            if quick_check and quick_check.get("action") not in ["desconocido", "ayuda"]:
                return quick_check
        return parsed_res

    except Exception as exc:
        logger.error("Error al procesar audio con Gemini File API: %s", exc, exc_info=True)
        return {
            "action": "desconocido",
            "product_name": None,
            "quantity": None,
            "confidence": 0.0,
            "unit": None,
            "raw_text": f"[Error de procesamiento de audio: {exc}]",
        }
    finally:
        if audio_file:
            try:
                genai.delete_file(audio_file.name)
            except Exception:
                pass
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Parser determinístico rápido (Regex NLP)
# ---------------------------------------------------------------------------

def quick_parse_intent(text: str) -> dict | None:
    """
    Parser determinístico rápido para frases y comandos comunes de tenderos.
    Retorna un diccionario de intent si detecta una estructura clara, o None si debe delegar a Gemini.
    """
    if not text or not isinstance(text, str):
        return None

    text_lower = text.lower().strip()

    # 0. Ayuda o Saludos explícitos
    if any(k in text_lower for k in ["ayuda", "que puedes hacer", "qué puedes hacer", "que haces", "qué haces", "instrucciones", "hola", "buenos dias", "buenas tardes"]):
        return {"action": "ayuda", "raw_text": text}

    # 1. Crear producto nuevo
    if any(k in text_lower for k in ["registrar", "crear", "nuevo producto", "agregar producto"]):
        m_costo = re.search(r'(?:costó|costo|compré a|comprados a|comprado a)\s+(\d+)', text_lower)
        precio_costo = float(m_costo.group(1)) if m_costo else None

        m_venta = re.search(r'(?:lo vendo a|vendo a|precio|venta a|a)\s+(\d+)', text_lower)
        precio_venta = float(m_venta.group(1)) if m_venta else None

        m_qty = re.search(r'(?:con|llegaron|tengo|stock)\s+(\d+)', text_lower)
        qty = float(m_qty.group(1)) if m_qty else 0.0

        m_name = re.search(r'(?:registrar|crear|agregar producto|nuevo producto)\s+(?:a\s+)?([^\d]+?)(?=\s+(?:costó|costo|lo vendo|a\s+\d|con\s+\d|\d+)|$)', text_lower)
        name = m_name.group(1).strip() if m_name else text

        name = re.sub(r'\b(producto|nuevo)\b', '', name, flags=re.IGNORECASE).strip()

        return {
            "action": "crear_producto",
            "product_name": name.title() if name else "Nuevo Producto",
            "precio_costo": precio_costo,
            "precio_venta": precio_venta,
            "quantity": qty,
            "unit": "unidad",
            "confidence": 0.98,
            "raw_text": text,
        }

    # 2. Reabastecer stock
    if any(k in text_lower for k in ["reabastecer", "llegaron", "ingresaron", "recibí", "recibi"]):
        m_qty = re.search(r'(\d+)', text_lower)
        qty = float(m_qty.group(1)) if m_qty else 1.0

        clean_text = re.sub(r'\b(reabastecer|llegaron|ingresaron|recibí|recibi|unidades|unidad|cajas|caja|bultos|bulto|de)\b', '', text_lower)
        clean_text = re.sub(r'\d+', '', clean_text).strip()

        return {
            "action": "reabastecer",
            "product_name": clean_text.title() if clean_text else None,
            "quantity": qty,
            "unit": "unidad",
            "confidence": 0.95,
            "raw_text": text,
        }

    # 3. Consultar stock o precio
    if any(k in text_lower for k in ["cuanto", "cuántas", "cuántos", "cuantos", "stock", "quedan", "queda", "hay", "precio"]):
        clean_text = re.sub(r'\b(cuanto|cuántas|cuántos|cuantos|stock|quedan|queda|hay|precio|de|a|cómo|como|es|el|la|los|las|tengo)\b', '', text_lower)
        clean_text = clean_text.replace("?", "").replace("¿", "").strip()

        return {
            "action": "consultar_stock",
            "product_name": clean_text.title() if clean_text else None,
            "confidence": 0.95,
            "raw_text": text,
        }

    return None


# ---------------------------------------------------------------------------
# Parsing de intención desde texto
# ---------------------------------------------------------------------------

def parse_text_intent(text: str, product_names: list[str]) -> dict:
    # 1. Intentar con el parser determinístico súper rápido primero
    quick_res = quick_parse_intent(text)
    if quick_res is not None:
        logger.info("Intención reconocida por quick_parse_intent: %s", quick_res["action"])
        return quick_res

    # 2. Si es una frase compleja, usar Gemini 1.5 Flash
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

    # 1. Caso: Consulta de ayuda, fuera de alcance, saludo o intención desconocida
    if action in ["fuera_de_alcance", "desconocido", "ayuda", "audio_ruidoso"] or not action:
        return (
            "🤖 *Asistente de Inventario — Gestión Neiva*\n\n"
            "¡Hola! Soy tu asistente de IA y puedo ayudarte a gestionar el inventario de tu tienda por nota de voz o mensaje de texto.\n\n"
            "📌 *¿Qué soy capaz de hacer?*\n\n"
            "1. 📦 *Registrar un producto nuevo:*\n"
            "   👉 *Dime:* \"Registrar Pan Bimbo costó 4500 lo vendo a 6500 con 12 unidades\"\n\n"
            "2. ➕ *Reabastecer mercancía existente:*\n"
            "   👉 *Dime:* \"Llegaron 20 gaseosas\" o \"Reabastecer 10 unidades de Café\"\n\n"
            "3. 📋 *Consultar stock o precios:*\n"
            "   👉 *Dime:* \"¿Cuántas achiras quedan?\" o \"¿A cómo es el precio del café?\"\n\n"
            "💡 *Prueba enviándome un mensaje de voz o texto con cualquiera de estos comandos.*"
        )

    # 2. Caso: Datos incompletos (reabastecer sin cantidad)
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
                "📝 *Para registrar un nuevo producto necesito los datos obligatorios:*\n\n"
                "Envíame una nota de voz o mensaje con la siguiente estructura:\n"
                "1. 📦 *Nombre del producto* (ej: 'Pan Bimbo Blanco')\n"
                "2. 💵 *Precio Costo* (a cómo lo compraste, ej: 'costó 4500')\n"
                "3. 💰 *Precio Venta* (a cómo lo vendes, ej: 'lo vendo a 6500')\n"
                "4. 📊 *Stock Inicial* (ej: 'tengo 12 unidades')\n\n"
                "💡 *Ejemplo completo:* \"Registrar Pan Bimbo costó 4500 lo vendo a 6500 con 12 unidades\""
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
        precio_costo = intent.get("precio_costo")

        # Guiar si faltan precios
        if not precio_venta or float(precio_venta) <= 0:
            return (
                f"📝 *Para registrar \"{product_name}\" en tu tienda faltan los precios:*\n\n"
                f"Envíame una nota de voz aclarando a cómo lo compraste y a cómo lo vendes.\n\n"
                f"💡 *Ejemplo:* \"Registrar {product_name} costó 4500 lo vendo a 6500 con 10 unidades\""
            )

        if not precio_costo or float(precio_costo) <= 0:
            # Si el tendero solo dijo 1 precio, asumimos que dijo el precio de venta y le sugerimos/pedimos el costo
            precio_costo = float(precio_venta) * 0.7  # Estimado por defecto 70% del precio de venta

        quantity = intent.get("quantity") or 0
        unit_str = intent.get("unit", "unidad").lower().strip()

        # Mapear unidad
        unidad_enum = models.UnidadMedida.UNIDAD
        for u in models.UnidadMedida:
            if u.value == unit_str:
                unidad_enum = u
                break

        # Mapear categoría si la mencionó
        cat_str = intent.get("categoria")
        categoria_enum = None
        if cat_str:
            for c in models.CategoriaProducto:
                if c.value.lower() == cat_str.lower():
                    categoria_enum = c
                    break

        # Mapear fecha de vencimiento si la mencionó
        fecha_venc = None
        if intent.get("fecha_vencimiento"):
            try:
                from datetime import datetime
                fecha_venc = datetime.strptime(intent["fecha_vencimiento"], "%Y-%m-%d").date()
            except Exception:
                fecha_venc = None

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
                categoria=categoria_enum,
                fecha_vencimiento=fecha_venc,
            )
            db.add(nuevo_prod)
            db.commit()
            db.refresh(nuevo_prod)

            info_cat = f"\n🏷️ *Categoría:* {nuevo_prod.categoria.value}" if nuevo_prod.categoria else ""
            info_venc = f"\n📅 *Vencimiento:* {nuevo_prod.fecha_vencimiento}" if nuevo_prod.fecha_vencimiento else ""

            return (
                f"🎉 *¡Producto nuevo registrado exitosamente!*\n\n"
                f"📦 *Producto:* {nuevo_prod.nombre}\n"
                f"💵 *Precio Costo:* ${float(nuevo_prod.precio_costo):,.0f} COP\n"
                f"💰 *Precio Venta:* ${float(nuevo_prod.precio_venta):,.0f} COP\n"
                f"📊 *Stock Inicial:* {float(nuevo_prod.cantidad_actual)} {nuevo_prod.unidad_medida.value}(s)"
                f"{info_cat}{info_venc}\n"
                f"🏷️ *Código Barcode:* {nuevo_prod.codigo_barras}\n\n"
                f"💡 *Ya está listo en tu Punto de Venta (POS) y lo puedes consultar o vender de inmediato.*"
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
