import hashlib
import hmac
import json
import logging
import os
import re

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, status
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy.orm import Session

from app import models
import app.database
from app.database import get_db
from app.dependencies import get_current_user
from app.services import gemini_voice, whatsapp_service, whatsapp_vinculacion

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp IA"])

# Pattern to match "VINCULAR XXXXXX" (6-digit code)
_VINCULAR_RE = re.compile(r"^VINCULAR\s+(\d{6})$", re.IGNORECASE)


def _verificar_firma_hmac(body_bytes: bytes, signature_header: str | None, app_secret: str) -> bool:
    """Verifica la firma HMAC SHA-256 enviada por Meta en los webhooks."""
    if not signature_header:
        return False
    if not app_secret:
        logger.warning("WHATSAPP_APP_SECRET no configurada. Omitiendo validación estricta de firma HMAC.")
        return True
    try:
        expected = "sha256=" + hmac.new(app_secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature_header, expected)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Webhook verification (GET) — Meta sends this during setup
# ---------------------------------------------------------------------------

@router.get("/webhook")
def verificar_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """Webhook verification endpoint for Meta WhatsApp Business API."""
    if whatsapp_service.verify_webhook(hub_mode, hub_verify_token, hub_challenge):
        return PlainTextResponse(content=hub_challenge, status_code=200)

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Token de verificación inválido",
    )


# ---------------------------------------------------------------------------
# Incoming messages (POST) — Meta pushes messages here
# ---------------------------------------------------------------------------

def _process_whatsapp_message(phone: str, msg: dict) -> None:
    """
    Background task: processes a single incoming WhatsApp message.

    Uses short-lived DB sessions to prevent holding DB pool connections
    during external network I/O calls (Gemini AI / Media Download).
    """
    db: Session = app.database.SessionLocal()
    try:
        # Step 1 — look up user by phone number
        usuario = whatsapp_vinculacion.get_usuario_by_phone(phone, db)

        if usuario is None:
            # User not linked — check for VINCULAR command
            match = _VINCULAR_RE.match((msg.get("text", {}).get("body", "") or "").strip())
            if match:
                code = match.group(1)
                try:
                    whatsapp_vinculacion.verificar_codigo(code, phone, db)
                    whatsapp_service.send_text_message(
                        phone,
                        "✅ ¡Tu cuenta ha sido vinculada exitosamente! "
                        "Ahora puedes enviar comandos de inventario por texto o audio.",
                    )
                except Exception as exc:
                    whatsapp_service.send_text_message(
                        phone,
                        f"❌ No se pudo vincular: {exc}",
                    )
            else:
                whatsapp_service.send_text_message(
                    phone,
                    "👋 Hola! Tu número no está vinculado a Gestión Neiva.\n\n"
                    "Para vincular tu cuenta:\n"
                    "1. Abre la app y ve a Configuración → WhatsApp\n"
                    "2. Genera un código de vinculación\n"
                    "3. Envía aquí: VINCULAR XXXXXX\n\n"
                    "Ejemplo: VINCULAR 847291",
                )
            return

        # Step 2 — user is linked: fetch product names, empresa_id & context_info
        empresa_id = usuario.empresa_id
        empresa = usuario.empresa
        nombre_tienda = empresa.nombre_comercial if empresa else "tu tienda"
        nombre_usuario = usuario.email.split("@")[0].capitalize() if usuario.email else "tendero"
        context_info = {
            "nombre_tienda": nombre_tienda,
            "nombre_usuario": nombre_usuario,
        }

        productos = db.query(models.Producto).filter(
            models.Producto.empresa_id == empresa_id,
            models.Producto.is_active.is_(True),
        ).all()
        product_names = [p.nombre for p in productos]
    finally:
        try:
            db.close()
        except Exception:
            pass

    # Step 3 — parse intent outside DB session (Release connection during I/O)
    msg_type = msg.get("type", "text")
    try:
        if msg_type == "audio":
            audio_id = msg.get("audio", {}).get("id")
            if not audio_id:
                whatsapp_service.send_text_message(phone, "⚠️ No se pudo procesar el audio.")
                return
            audio_bytes, mime_type = whatsapp_service.download_media(audio_id)
            intent = gemini_voice.transcribe_and_parse(audio_bytes, mime_type, product_names)
        else:
            text_body = msg.get("text", {}).get("body", "")
            intent = gemini_voice.parse_text_intent(text_body, product_names)

        # Step 4 — execute the parsed intent in a fresh, isolated DB session
        with app.database.SessionLocal() as db2:
            result = gemini_voice.execute_inventory_action(intent, empresa_id, db2, context_info=context_info)

        # Step 5 — respond to user
        whatsapp_service.send_text_message(phone, result)

    except Exception as exc:
        import traceback
        tb = traceback.format_exc()
        logger.exception("Error processing WhatsApp message from %s", phone)
        error_msg = f"⚠️ Error procesando tu mensaje:\n\n{str(exc)}\n\nDetalle:\n{tb[-400:]}"
        try:
            whatsapp_service.send_text_message(phone, error_msg)
        except Exception:
            logger.exception("Failed to send error message to %s", phone)


@router.post("/webhook")
async def recibir_mensaje(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """
    Receive incoming messages from WhatsApp Business API.

    Always returns 200 OK immediately (Meta retries on non-2xx).
    Actual message processing is dispatched to a BackgroundTask so
    the response returns within Meta's 5-second window.
    """
    raw_body = await request.body()
    signature = request.headers.get("x-hub-signature-256")

    app_secret = os.getenv("WHATSAPP_APP_SECRET", "")
    if not app_secret:
        logger.warning("WHATSAPP_APP_SECRET no configurada. Omitiendo validación estricta de firma HMAC.")
    elif not _verificar_firma_hmac(raw_body, signature, app_secret):
        logger.warning("Firma HMAC inválida recibida en webhook de WhatsApp.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firma HMAC inválida",
        )

    try:
        body = json.loads(raw_body.decode("utf-8")) if raw_body else {}
    except Exception:
        return Response(status_code=200)

    # Validate payload structure
    if body.get("object") != "whatsapp_business_account":
        return Response(status_code=200)

    # Extract messages from Meta's nested payload
    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages", [])
            for msg in messages:
                phone = msg.get("from")
                if not phone:
                    continue
                # Dispatch to background — don't block the webhook response
                background_tasks.add_task(_process_whatsapp_message, phone, msg)

    # Always 200 to prevent Meta retries
    return Response(status_code=200)


# ---------------------------------------------------------------------------
# Vinculación endpoints (protected — require JWT)
# ---------------------------------------------------------------------------

@router.get("/vinculacion/codigo")
def generar_codigo_vinculacion(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """Generate a 6-digit linking code, or show already-linked phone."""
    if current_user.telefono_whatsapp:
        return {
            "codigo": None,
            "expira_en": None,
            "telefono_vinculado": current_user.telefono_whatsapp,
        }

    codigo, expira_en = whatsapp_vinculacion.generar_codigo(current_user.id, db)
    return {
        "codigo": codigo,
        "expira_en": expira_en,
        "telefono_vinculado": None,
    }


@router.delete("/vinculacion")
def desvincular_whatsapp(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """Unlink the current user's WhatsApp number."""
    whatsapp_vinculacion.desvincular(current_user.id, db)
    return {"detail": "WhatsApp desvinculado exitosamente"}


@router.get("/estado")
def estado_whatsapp(
    current_user: models.Usuario = Depends(get_current_user),
):
    """Return WhatsApp integration status for the current user."""
    return {
        "vinculado": current_user.telefono_whatsapp is not None,
        "telefono": current_user.telefono_whatsapp,
    }
