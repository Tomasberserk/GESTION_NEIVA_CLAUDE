"""
Servicio para vinculación de números de WhatsApp a cuentas de usuario.

Maneja:
- Generación de códigos de 6 dígitos temporales (TTL 10 min)
- Verificación de códigos y guardado del teléfono en base de datos
- Búsqueda de usuarios por teléfono de WhatsApp
- Desvinculación de cuentas
"""

import logging
import random
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app import models

logger = logging.getLogger(__name__)

# Diccionario en memoria para códigos pendientes de verificación.
# Estructura: { "codigo": { "usuario_id": UUID, "expires_at": datetime } }
_pending_codes: dict[str, dict] = {}


def generar_codigo(usuario_id: UUID, db: Session) -> tuple[str, int]:
    """
    Genera un código aleatorio de 6 dígitos para la vinculación.
    Tiene una validez de 10 minutos (600 segundos).
    
    Args:
        usuario_id: ID del usuario que solicita la vinculación.
        db: Sesión de base de datos.
        
    Returns:
        Una tupla con (codigo, expira_en_segundos).
    """
    # Limpiar códigos expirados para evitar consumo de memoria
    ahora = datetime.now(timezone.utc)
    expirados = [k for k, v in _pending_codes.items() if v["expires_at"] < ahora]
    for k in expirados:
        _pending_codes.pop(k, None)

    # Generar código único que no esté colisionando
    while True:
        codigo = f"{random.randint(100000, 999999)}"
        if codigo not in _pending_codes:
            break

    expira_en = 600  # 10 minutos en segundos
    expires_at = ahora + timedelta(seconds=expira_en)
    
    _pending_codes[codigo] = {
        "usuario_id": usuario_id,
        "expires_at": expires_at,
    }
    
    logger.info("Código de vinculación generado para usuario %s: %s", usuario_id, codigo)
    return codigo, expira_en


def verificar_codigo(code: str, phone: str, db: Session) -> models.Usuario:
    """
    Verifica un código de vinculación. Si es válido y no ha expirado,
    vincula el número de teléfono al usuario correspondiente.
    
    Args:
        code: Código de 6 dígitos ingresado por el usuario.
        phone: Teléfono de WhatsApp que envía el código.
        db: Sesión de base de datos.
        
    Returns:
        El usuario vinculado.
        
    Raises:
        ValueError: Si el código es inválido, expiró, el usuario no existe,
                     o si el teléfono ya está en uso por otro usuario.
    """
    ahora = datetime.now(timezone.utc)
    
    # 1. Validar existencia del código en memoria
    if code not in _pending_codes:
        raise ValueError("El código ingresado es incorrecto o ya fue utilizado.")
        
    pending = _pending_codes[code]
    
    # 2. Validar expiración del código
    if pending["expires_at"] < ahora:
        _pending_codes.pop(code, None)
        raise ValueError("El código ha expirado. Genera uno nuevo desde el panel.")
        
    usuario_id = pending["usuario_id"]
    
    # 3. Validar si el teléfono ya está registrado por otro usuario activo
    usuario_existente = db.query(models.Usuario).filter(
        models.Usuario.telefono_whatsapp == phone,
        models.Usuario.is_active.is_(True)
    ).first()
    
    if usuario_existente:
        raise ValueError("Este número de WhatsApp ya se encuentra vinculado a otra cuenta.")
        
    # 4. Obtener el usuario de la DB y vincularlo
    usuario = db.query(models.Usuario).filter(
        models.Usuario.id == usuario_id,
        models.Usuario.is_active.is_(True)
    ).first()
    
    if not usuario:
        raise ValueError("El usuario asociado al código ya no está activo o no existe.")
        
    # 5. Guardar la vinculación
    usuario.telefono_whatsapp = phone
    db.commit()
    
    # Remover código usado
    _pending_codes.pop(code, None)
    
    logger.info("Usuario %s vinculado exitosamente al WhatsApp %s", usuario_id, phone)
    return usuario


def get_usuario_by_phone(phone: str, db: Session) -> models.Usuario | None:
    """
    Busca un usuario activo por su número de teléfono vinculado.
    
    Args:
        phone: Teléfono de WhatsApp.
        db: Sesión de base de datos.
        
    Returns:
        El objeto Usuario si existe, de lo contrario None.
    """
    return db.query(models.Usuario).filter(
        models.Usuario.telefono_whatsapp == phone,
        models.Usuario.is_active.is_(True)
    ).first()


def desvincular(usuario_id: UUID, db: Session) -> bool:
    """
    Desvincula el número de WhatsApp de un usuario.
    
    Args:
        usuario_id: ID del usuario a desvincular.
        db: Sesión de base de datos.
        
    Returns:
        True si se desvinculó exitosamente, False si el usuario no existe.
    """
    usuario = db.query(models.Usuario).filter(
        models.Usuario.id == usuario_id,
        models.Usuario.is_active.is_(True)
    ).first()
    
    if not usuario:
        return False
        
    usuario.telefono_whatsapp = None
    db.commit()
    logger.info("WhatsApp desvinculado para el usuario %s", usuario_id)
    return True
