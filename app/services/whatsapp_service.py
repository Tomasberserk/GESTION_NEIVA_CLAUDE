"""
Servicio de comunicación con la API de WhatsApp Business Cloud.

Maneja:
- Envío de mensajes de texto vía WhatsApp Cloud API
- Descarga de archivos multimedia (audio) desde WhatsApp
- Verificación del webhook de suscripción de Meta
"""

import logging
import os

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuración (lazy — no falla al importar si faltan las variables)
# ---------------------------------------------------------------------------

_WHATSAPP_API_BASE = "https://graph.facebook.com/v21.0"


def _get_config() -> dict:
    """Lee la configuración de WhatsApp desde variables de entorno."""
    access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")

    if not access_token or not phone_number_id:
        raise RuntimeError(
            "WHATSAPP_ACCESS_TOKEN y WHATSAPP_PHONE_NUMBER_ID deben estar "
            "configurados en las variables de entorno."
        )

    return {
        "access_token": access_token,
        "phone_number_id": phone_number_id,
        "verify_token": verify_token or "",
    }


# ---------------------------------------------------------------------------
# Envío de mensajes
# ---------------------------------------------------------------------------

def send_text_message(phone_number: str, text: str) -> bool:
    """
    Envía un mensaje de texto vía WhatsApp Cloud API.

    Args:
        phone_number: Número del destinatario en formato internacional (ej: "573001234567").
        text: Texto del mensaje a enviar.

    Returns:
        True si el mensaje se envió exitosamente, False en caso de error.
    """
    config = _get_config()
    url = f"{_WHATSAPP_API_BASE}/{config['phone_number_id']}/messages"

    headers = {
        "Authorization": f"Bearer {config['access_token']}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": text},
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            logger.info(
                "Mensaje enviado exitosamente a %s", phone_number
            )
            return True

        logger.error(
            "Error al enviar mensaje a %s: HTTP %d — %s",
            phone_number,
            response.status_code,
            response.text[:500],
        )
        return False

    except httpx.TimeoutException:
        logger.error("Timeout al enviar mensaje a %s", phone_number)
        return False
    except Exception as exc:
        logger.error("Error inesperado al enviar mensaje a %s: %s", phone_number, exc)
        return False


# ---------------------------------------------------------------------------
# Descarga de multimedia
# ---------------------------------------------------------------------------

def download_media(media_id: str) -> tuple[bytes, str]:
    """
    Descarga un archivo multimedia desde WhatsApp usando el media_id.

    Proceso en dos pasos:
    1. Obtener la URL del archivo desde la API de Meta.
    2. Descargar el contenido binario del archivo.

    Args:
        media_id: ID del media recibido en el webhook de WhatsApp.

    Returns:
        tuple[bytes, str]: (bytes_del_archivo, mime_type)

    Raises:
        RuntimeError: Si no se puede obtener la URL o descargar el archivo.
    """
    config = _get_config()

    headers = {
        "Authorization": f"Bearer {config['access_token']}",
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            # Paso 1: Obtener la metadata de la URL firmada desde Meta
            meta_url = f"{_WHATSAPP_API_BASE}/{media_id}"
            meta_response = client.get(meta_url, headers=headers)

            if meta_response.status_code != 200:
                logger.error(
                    "Error al obtener URL del media %s: HTTP %d — %s",
                    media_id,
                    meta_response.status_code,
                    meta_response.text[:500],
                )
                raise RuntimeError(
                    f"No se pudo obtener la URL del archivo multimedia "
                    f"(HTTP {meta_response.status_code})"
                )

            media_data = meta_response.json()
            media_url = media_data.get("url")
            mime_type = media_data.get("mime_type", "audio/ogg")

            if not media_url:
                logger.error(
                    "Respuesta del media %s no contiene 'url': %s",
                    media_id,
                    media_data,
                )
                raise RuntimeError(
                    "La respuesta de WhatsApp no contiene la URL del archivo"
                )

            # Paso 2: Descargar el contenido binario real
            download_response = client.get(media_url, headers=headers)

            if download_response.status_code != 200:
                logger.error(
                    "Error al descargar media desde %s: HTTP %d",
                    media_url[:100],
                    download_response.status_code,
                )
                raise RuntimeError(
                    f"No se pudo descargar el archivo multimedia "
                    f"(HTTP {download_response.status_code})"
                )

            logger.info(
                "Media %s descargado exitosamente (%d bytes, mime_type=%s)",
                media_id,
                len(download_response.content),
                mime_type,
            )
            return download_response.content, mime_type

    except RuntimeError:
        raise
    except httpx.TimeoutException:
        logger.error("Timeout al descargar media %s", media_id)
        raise RuntimeError(f"Timeout al descargar el archivo multimedia {media_id}")
    except Exception as exc:
        logger.error("Error inesperado al descargar media %s: %s", media_id, exc)
        raise RuntimeError(f"Error inesperado al descargar multimedia: {exc}") from exc


# ---------------------------------------------------------------------------
# Verificación del webhook
# ---------------------------------------------------------------------------

def verify_webhook(mode: str, token: str, challenge: str) -> str | None:
    """
    Verifica la suscripción del webhook de Meta.

    Meta envía una solicitud GET con hub.mode, hub.verify_token y hub.challenge.
    Si el token coincide, se debe devolver el challenge para confirmar la suscripción.
    """
    expected_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "tiendapp_secret_token")

    if mode == "subscribe" and token == expected_token:
        logger.info("Webhook verificado exitosamente con token: %s", token)
        return challenge

    logger.warning(
        "Verificación de webhook fallida: mode=%s, token_recibido=%s, token_esperado=%s",
        mode,
        token,
        expected_token,
    )
    return None
