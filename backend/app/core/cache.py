"""Redis async cache client."""

import json
from typing import Any

import redis.asyncio as redis

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RedisCache:
    def __init__(self) -> None:
        self._client: redis.Redis | None = None

    async def connect(self) -> None:
        if not settings.redis_enabled:
            return
        self._client = redis.from_url(settings.redis_url, decode_responses=True)
        await self._client.ping()
        logger.info("redis_connected")

    async def disconnect(self) -> None:
        if self._client:
            await self._client.close()

    async def ping(self) -> bool:
        if not self._client:
            return False
        await self._client.ping()
        return True

    async def get(self, key: str) -> Any | None:
        if not self._client:
            return None
        raw = await self._client.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> None:
        if not self._client:
            return
        payload = json.dumps(value) if not isinstance(value, str) else value
        await self._client.set(key, payload, ex=ttl or settings.redis_cache_ttl_seconds)

    async def delete(self, key: str) -> None:
        if self._client:
            await self._client.delete(key)

    async def delete_pattern(self, pattern: str) -> None:
        if not self._client:
            return
        async for key in self._client.scan_iter(match=pattern):
            await self._client.delete(key)


cache = RedisCache()
