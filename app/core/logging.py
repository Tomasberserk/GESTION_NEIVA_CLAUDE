import logging
import os

# Configuración del logger de auditoría de seguridad
LOG_FILE = "security_audit.log"

logger = logging.getLogger("security_audit")
logger.setLevel(logging.INFO)

# Evitar duplicar handlers al recargar la app
if not logger.handlers:
    formatter = logging.Formatter(
        "[%(asctime)s] [SECURITY-AUDIT] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler para persistencia local en archivo de auditoría
    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        # En caso de permisos restringidos en algún despliegue
        pass

    # Handler para logs del sistema estándar (consola)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def log_security_event(
    event: str,
    email: str,
    user_id: str = "anonymous",
    ip: str = "unknown",
    level: str = "INFO",
) -> None:
    """
    Registra un evento de seguridad de forma estructurada para auditorías.
    Alineado con A09:2025 – Security Logging & Alerting Failures.
    """
    msg = f"Event: {event} | Email: {email} | UserID: {user_id} | IP: {ip}"
    
    level_upper = level.upper()
    if level_upper == "WARNING":
        logger.warning(msg)
    elif level_upper == "ERROR":
        logger.error(msg)
    else:
        logger.info(msg)
