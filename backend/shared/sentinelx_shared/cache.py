"""
Async Redis client — shared across all services.
"""
from collections.abc import AsyncGenerator
from typing import Annotated

import redis.asyncio as aioredis
from fastapi import Depends

from sentinelx_shared.config import get_settings

settings = get_settings()

_pool: aioredis.ConnectionPool | None = None


def get_redis_pool() -> aioredis.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = aioredis.ConnectionPool.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=50,
        )
    return _pool


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    """FastAPI dependency — yields an async Redis connection."""
    pool = get_redis_pool()
    redis = aioredis.Redis(connection_pool=pool)
    try:
        yield redis
    finally:
        await redis.aclose()


RedisClient = Annotated[aioredis.Redis, Depends(get_redis)]
