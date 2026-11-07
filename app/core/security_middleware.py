"""HTTP security headers and request correlation ID middleware."""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import set_correlation_id


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Propagate or generate an X-Correlation-ID header for every HTTP request."""

    async def dispatch(self, request: Request, call_next) -> Response:
        incoming_cid = request.headers.get("X-Correlation-ID") or request.headers.get("x-correlation-id")
        cid = set_correlation_id(incoming_cid)
        request.state.correlation_id = cid
        response: Response = await call_next(request)
        response.headers["X-Correlation-ID"] = cid
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Inject HTTP security headers recommended by OWASP Top 10 (A02/A05)."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        return response
