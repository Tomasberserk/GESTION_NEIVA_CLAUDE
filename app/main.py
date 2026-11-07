"""Main FastAPI application entry point for Gestion Neiva POS SaaS."""
import os

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.logging import get_correlation_id
from app.core.security_middleware import CorrelationIdMiddleware, SecurityHeadersMiddleware
from app.database import get_db
from app.routers import (
    agente,
    auth,
    dashboard,
    empresas,
    productos,
    reportes,
    soporte,
    superadmin,
    usuarios,
    ventas,
)

app = FastAPI(
    title="Tiendapp API",
    description="POS SaaS System — Gestion Inteligente Neiva",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

_CORS_DEFAULT = ",".join([
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "https://gestion-neiva-claude.vercel.app",
])
_origins_raw = os.getenv("CORS_ORIGINS", _CORS_DEFAULT)
_origins = [o.strip() for o in _origins_raw.split(",") if o.strip()]

_frontend_url = os.getenv("FRONTEND_URL", "").strip()
if _frontend_url and _frontend_url not in _origins:
    _origins.append(_frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CorrelationIdMiddleware)

_media_dir = os.getenv("UPLOAD_DIR", "media")
os.makedirs(_media_dir, exist_ok=True)
app.mount("/media", StaticFiles(directory=_media_dir), name="media")

for router_instance in (
    auth.router,
    dashboard.router,
    empresas.router,
    productos.router,
    ventas.router,
    reportes.router,
    superadmin.router,
    soporte.router,
    usuarios.router,
    agente.router,
):
    app.include_router(router_instance, prefix="/api/v1")
    app.include_router(router_instance, prefix="/api", include_in_schema=False)
    app.include_router(router_instance, include_in_schema=False)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Emit standardized error structure while preserving FastAPI 'detail' compatibility."""
    if isinstance(exc.detail, dict):
        error_code = exc.detail.get("code", f"HTTP_{exc.status_code}")
        message = exc.detail.get("message", str(exc.detail))
    else:
        error_code = f"HTTP_{exc.status_code}"
        message = str(exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error": error_code,
            "message": message,
            "details": [],
            "correlationId": get_correlation_id(),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Emit standardized validation error payload for HTTP 422 responses."""
    encoded_errors = jsonable_encoder(exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": encoded_errors,
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": encoded_errors,
            "correlationId": get_correlation_id(),
        },
    )


def _check_redis_health() -> str:
    """Ping Redis if configured and return connection state."""
    redis_url = os.getenv("REDIS_URL", "")
    if not redis_url:
        return "not_configured"
    try:
        import redis
        client = redis.from_url(redis_url, socket_connect_timeout=1, socket_timeout=1)
        return "connected" if client.ping() else "disconnected"
    except Exception:
        return "disconnected"


@app.get("/health", tags=["System"])
@app.get("/api/health", tags=["System"], include_in_schema=False)
@app.get("/api/v1/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """Execute deep health check verifying database and cache connectivity."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    redis_status = _check_redis_health()
    require_redis = os.getenv("HEALTH_REQUIRE_REDIS", "false").lower() == "true"

    if db_status != "connected" or (require_redis and redis_status != "connected"):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "degraded",
                "version": "2.0.0",
                "db": db_status,
                "redis": redis_status,
            },
        )

    return {
        "status": "ok",
        "version": "2.0.0",
        "db": db_status,
        "redis": redis_status,
    }


@app.get("/", tags=["System"])
def root():
    """Return service metadata for root endpoint."""
    return {"status": "ok", "message": "Tiendapp API — Gestion Neiva", "version": "2.0.0"}
