import json
from typing import Any

from redis.asyncio import Redis

from app.core.config import settings


class CacheService:
    def __init__(self, redis_client: Redis) -> None:
        self.redis = redis_client

    async def get(self, key: str) -> Any | None:
        try:
            value = await self.redis.get(key)
        except Exception:
            return None
        if value is None:
            return None
        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        try:
            await self.redis.set(
                key,
                json.dumps(value, default=str, separators=(",", ":")),
                ex=ttl if ttl is not None else settings.REDIS_CACHE_TTL,
            )
        except Exception:
            return

    async def delete(self, key: str) -> None:
        try:
            await self.redis.delete(key)
        except Exception:
            return

    async def exists(self, key: str) -> bool:
        try:
            return bool(await self.redis.exists(key))
        except Exception:
            return False

    async def delete_pattern(self, pattern: str) -> None:
        try:
            keys = [key async for key in self.redis.scan_iter(match=pattern)]
            if keys:
                await self.redis.delete(*keys)
        except Exception:
            return

    async def clear(self) -> None:
        try:
            await self.redis.flushdb()
        except Exception:
            return
