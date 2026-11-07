"""Structured JSON logging and correlation ID propagation for security and operational events."""
from contextvars import ContextVar
from datetime import datetime, timezone
import json
import logging
import uuid

LOG_FILE = "security_audit.log"

correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")


def get_correlation_id() -> str:
    """Return the active request correlation ID or generate a fallback UUID."""
    current = correlation_id_ctx.get()
    if not current:
        current = str(uuid.uuid4())
        correlation_id_ctx.set(current)
    return current


def set_correlation_id(value: str | None = None) -> str:
    """Set and return the correlation ID for the current execution context."""
    cid = (value or "").strip() or str(uuid.uuid4())
    correlation_id_ctx.set(cid)
    return cid


class StructuredJSONFormatter(logging.Formatter):
    """Format log records as single-line JSON objects compliant with NFR-09."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "correlationId": getattr(record, "correlationId", None) or get_correlation_id(),
            "module": getattr(record, "domain_module", None) or record.name,
            "message": record.getMessage(),
        }
        for extra_key in ("event", "email", "user_id", "ip"):
            val = getattr(record, extra_key, None)
            if val is not None:
                payload[extra_key] = val
        return json.dumps(payload, ensure_ascii=False)


logger = logging.getLogger("security_audit")
logger.setLevel(logging.INFO)
logger.propagate = True

if not logger.handlers:
    _json_formatter = StructuredJSONFormatter()
    _console_handler = logging.StreamHandler()
    _console_handler.setFormatter(_json_formatter)
    logger.addHandler(_console_handler)


def log_security_event(
    event: str,
    email: str,
    user_id: str = "anonymous",
    ip: str = "unknown",
    level: str = "INFO",
    module: str = "auth_tenancy",
) -> None:
    """Record a structured security audit event to both console and local audit file."""
    cid = get_correlation_id()
    msg = f"Event: {event} | Email: {email} | UserID: {user_id} | IP: {ip}"
    extra = {
        "correlationId": cid,
        "domain_module": module,
        "event": event,
        "email": email,
        "user_id": user_id,
        "ip": ip,
    }

    level_upper = level.upper()
    if level_upper == "WARNING":
        logger.warning(msg, extra=extra)
    elif level_upper == "ERROR":
        logger.error(msg, extra=extra)
    else:
        logger.info(msg, extra=extra)

    # Guarantee persistence to LOG_FILE even if a test unlinked the file descriptor on POSIX
    record_json = json.dumps(
        {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "level": level_upper,
            "correlationId": cid,
            "module": module,
            "event": event,
            "email": email,
            "user_id": user_id,
            "ip": ip,
            "message": msg,
        },
        ensure_ascii=False,
    )
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as audit_fp:
            audit_fp.write(record_json + "\n")
    except OSError:
        pass
