"""Performance monitoring middleware — request timing and slow query detection."""
from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Thresholds
SLOW_REQUEST_MS = 2000  # 2 seconds


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Log request timing and flag slow requests."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        # Add timing header
        response.headers["X-Response-Time"] = f"{duration_ms:.0f}ms"

        # Log slow requests
        if duration_ms > SLOW_REQUEST_MS:
            logger.warning(
                "SLOW REQUEST: %s %s took %.0fms (threshold: %dms)",
                request.method,
                request.url.path,
                duration_ms,
                SLOW_REQUEST_MS,
            )
        elif duration_ms > 500:
            logger.info(
                "Request: %s %s %.0fms",
                request.method,
                request.url.path,
                duration_ms,
            )

        return response
