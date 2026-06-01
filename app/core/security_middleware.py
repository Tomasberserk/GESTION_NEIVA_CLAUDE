from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware de seguridad para inyectar cabeceras HTTP recomendadas por OWASP Top 10 2025.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response: Response = await call_next(request)
        # Previene que el navegador adivine el tipo MIME del recurso
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Evita ataques de clickjacking denegando el enmarcado de la página (iframes)
        response.headers["X-Frame-Options"] = "DENY"
        # Habilita el filtro de XSS reflejado activo en navegadores heredados
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Fuerza todas las conexiones futuras del navegador a usar HTTPS
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        # Evita almacenamiento en caché de información sensible de transacciones del POS
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        return response
