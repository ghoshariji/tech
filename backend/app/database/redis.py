import json
from typing import Any, Optional
import redis.asyncio as aioredis
from app.config.settings import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return redis_client


async def close_redis() -> None:
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


class CacheService:
    def __init__(self, redis: aioredis.Redis):
        self._redis = redis

    async def get(self, key: str) -> Optional[Any]:
        try:
            value = await self._redis.get(key)
            return json.loads(value) if value else None
        except Exception as exc:
            logger.warning(f"Cache GET error for key '{key}': {exc}")
            return None

    async def set(self, key: str, value: Any, ttl: int = settings.REDIS_CACHE_TTL) -> bool:
        try:
            await self._redis.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception as exc:
            logger.warning(f"Cache SET error for key '{key}': {exc}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            await self._redis.delete(key)
            return True
        except Exception as exc:
            logger.warning(f"Cache DELETE error for key '{key}': {exc}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        try:
            keys = await self._redis.keys(pattern)
            if keys:
                return await self._redis.delete(*keys)
            return 0
        except Exception as exc:
            logger.warning(f"Cache DELETE_PATTERN error for pattern '{pattern}': {exc}")
            return 0


async def get_cache() -> CacheService:
    redis = await get_redis()
    return CacheService(redis)
