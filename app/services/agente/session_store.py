"""Abstracción de almacenamiento de sesión para el Agente (SessionStore).

Soporta InMemory (para desarrollo y tests) y Redis (para producción multi-worker).
TTL por defecto: 5 minutos (300 segundos).
"""

import json
import logging
import os
import time
from typing import Any, Protocol

logger = logging.getLogger(__name__)


class SessionStoreUnavailableError(RuntimeError):
    """Lanzada cuando el almacén de sesiones de producción no está disponible (fail-closed)."""
    pass


class SessionStore(Protocol):
    async def get(self, session_id: str) -> dict[str, Any] | None:
        ...

    async def save(self, session_id: str, data: dict[str, Any], ttl: int = 300) -> None:
        ...

    async def delete(self, session_id: str) -> None:
        ...


class InMemorySessionStore:
    """Almacén en memoria con expiración por timestamp (para dev y testing)."""

    def __init__(self):
        self._store: dict[str, tuple[dict[str, Any], float]] = {}

    async def get(self, session_id: str) -> dict[str, Any] | None:
        item = self._store.get(session_id)
        if not item:
            return None
        data, expires_at = item
        if time.time() > expires_at:
            del self._store[session_id]
            return None
        return data

    async def save(self, session_id: str, data: dict[str, Any], ttl: int = 300) -> None:
        expires_at = time.time() + ttl
        self._store[session_id] = (data, expires_at)

    async def delete(self, session_id: str) -> None:
        self._store.pop(session_id, None)

    def clear(self) -> None:
        self._store.clear()


class RedisSessionStore:
    """Almacén en Redis para producción con TTL automático nativo."""

    def __init__(self, redis_url: str):
        import redis.asyncio as aioredis
        self.redis_url = redis_url
        self.redis = aioredis.from_url(redis_url, decode_responses=True)

    async def get(self, session_id: str) -> dict[str, Any] | None:
        try:
            raw = await self.redis.get(f"agente:session:{session_id}")
            if raw:
                return json.loads(raw)
            return None
        except Exception as exc:
            env = os.getenv("ENVIRONMENT", "development").lower()
            logger.error("Error al leer sesión de Redis: %s", exc)
            if env == "production":
                raise SessionStoreUnavailableError(f"Error de comunicación con Redis en producción: {exc}") from exc
            return None

    async def save(self, session_id: str, data: dict[str, Any], ttl: int = 300) -> None:
        try:
            payload = json.dumps(data, ensure_ascii=False)
            await self.redis.set(f"agente:session:{session_id}", payload, ex=ttl)
        except Exception as exc:
            env = os.getenv("ENVIRONMENT", "development").lower()
            logger.error("Error al guardar sesión en Redis: %s", exc)
            if env == "production":
                raise SessionStoreUnavailableError(f"Error al guardar sesión en Redis en producción: {exc}") from exc

    async def delete(self, session_id: str) -> None:
        try:
            await self.redis.delete(f"agente:session:{session_id}")
        except Exception as exc:
            env = os.getenv("ENVIRONMENT", "development").lower()
            logger.error("Error al eliminar sesión de Redis: %s", exc)
            if env == "production":
                raise SessionStoreUnavailableError(f"Error al eliminar sesión de Redis en producción: {exc}") from exc

    async def ping(self) -> bool:
        return await self.redis.ping()


# Instancia singleton para InMemory / Factory
_default_store: SessionStore | None = None


def get_session_store() -> SessionStore:
    """Devuelve la instancia configurada según variables de entorno.

    En producción (ENVIRONMENT=production), Redis es ESTRICTAMENTE OBLIGATORIO (fail-closed).
    Si Redis no está configurado o falla, NO se realiza fallback a InMemory para evitar
    inconsistencias o pérdida de estado entre workers concurrentes.
    """
    global _default_store
    if _default_store is not None:
        return _default_store

    redis_url = os.getenv("REDIS_URL")
    env = os.getenv("ENVIRONMENT", "development").lower()

    if env == "production":
        if not redis_url:
            raise SessionStoreUnavailableError(
                "Configuración inválida: en producción (ENVIRONMENT=production) REDIS_URL es obligatoria "
                "para garantizar el aislamiento e integridad de sesiones multi-worker."
            )
        try:
            _default_store = RedisSessionStore(redis_url)
            logger.info("SessionStore inicializado con Redis (%s) en producción", redis_url)
            return _default_store
        except Exception as exc:
            logger.critical("Fallo crítico al conectar con Redis en producción: %s", exc)
            raise SessionStoreUnavailableError(
                f"No se pudo conectar a Redis en producción. El agente no puede operar con almacén volátil: {exc}"
            ) from exc

    # En desarrollo / pruebas: intentar Redis si existe, con fallback permisivo a InMemory
    if redis_url:
        try:
            _default_store = RedisSessionStore(redis_url)
            logger.info("SessionStore inicializado con Redis (%s)", redis_url)
            return _default_store
        except Exception as exc:
            logger.warning("Fallo al conectar con Redis en dev, usando InMemory: %s", exc)

    _default_store = InMemorySessionStore()
    logger.info("SessionStore inicializado en InMemory")
    return _default_store


def set_session_store_instance(store: SessionStore | None) -> None:
    """Permite inyectar o limpiar un store específico (útil para tests unitarios)."""
    global _default_store
    _default_store = store
