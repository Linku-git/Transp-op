"""GZip compression middleware for API responses."""
from __future__ import annotations

import logging

from starlette.middleware.gzip import GZipMiddleware

logger = logging.getLogger(__name__)

# Minimum response size to compress (bytes)
MINIMUM_SIZE = 500


def add_compression_middleware(app) -> None:
    """Add GZip compression middleware to FastAPI app.

    Compresses responses > 500 bytes. Most JSON responses benefit.
    """
    app.add_middleware(GZipMiddleware, minimum_size=MINIMUM_SIZE)
    logger.info("GZip compression enabled (min size: %d bytes)", MINIMUM_SIZE)
