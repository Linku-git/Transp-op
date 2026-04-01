from __future__ import annotations

import logging

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> dict:
    db_ok = False
    redis_ok = False

    # Check database
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        logger.exception("Database health check failed")

    # Check Redis
    try:
        r = aioredis.from_url(settings.redis_url)
        pong = await r.ping()
        redis_ok = bool(pong)
        await r.aclose()
    except Exception:
        logger.exception("Redis health check failed")

    status = "healthy" if (db_ok and redis_ok) else "degraded"
    return {"status": status, "db": db_ok, "redis": redis_ok}
