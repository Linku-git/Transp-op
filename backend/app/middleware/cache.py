"""Redis caching middleware for frequently accessed data."""
from __future__ import annotations

import hashlib
import json
import logging
import os
from functools import wraps
from typing import Any, Callable

logger = logging.getLogger(__name__)

# Redis connection (optional — gracefully degrades if unavailable)
_redis_client = None

CACHE_TTL = {
    "site_config": 3600,       # 1 hour
    "vehicle_catalog": 1800,    # 30 minutes
    "settings": 86400,          # 24 hours
    "optimization_result": 600, # 10 minutes
    "kpi_dashboard": 300,       # 5 minutes
    "employee_list": 120,       # 2 minutes
}


def get_redis():
    """Get Redis client (lazy initialization)."""
    global _redis_client
    if _redis_client is None:
        try:
            import redis.asyncio as redis
            redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")
            _redis_client = redis.from_url(redis_url, decode_responses=True)
        except Exception as e:
            logger.warning("Redis not available: %s", e)
            _redis_client = None
    return _redis_client


def cache_key(prefix: str, *args: Any, **kwargs: Any) -> str:
    """Generate a deterministic cache key."""
    parts = [prefix] + [str(a) for a in args]
    if kwargs:
        sorted_kw = sorted(kwargs.items())
        parts.append(hashlib.md5(json.dumps(sorted_kw).encode()).hexdigest()[:8])
    return ":".join(parts)


async def cache_get(key: str) -> Any | None:
    """Get value from cache."""
    r = get_redis()
    if not r:
        return None
    try:
        data = await r.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        logger.debug("Cache get error: %s", e)
    return None


async def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    """Set value in cache with TTL."""
    r = get_redis()
    if not r:
        return
    try:
        await r.setex(key, ttl, json.dumps(value, default=str))
    except Exception as e:
        logger.debug("Cache set error: %s", e)


async def cache_delete(pattern: str) -> None:
    """Delete cache keys matching pattern."""
    r = get_redis()
    if not r:
        return
    try:
        keys = []
        async for key in r.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await r.delete(*keys)
    except Exception as e:
        logger.debug("Cache delete error: %s", e)


async def cache_invalidate_entity(entity: str, entity_id: str | None = None) -> None:
    """Invalidate cache for a specific entity type."""
    pattern = f"{entity}:*"
    if entity_id:
        pattern = f"{entity}:{entity_id}*"
    await cache_delete(pattern)
