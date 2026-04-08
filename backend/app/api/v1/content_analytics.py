from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.auth import User
from app.services.analytics_service import get_content_analytics

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/content")


@router.get("/analytics")
async def content_analytics_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get aggregate engagement analytics for all content."""
    return await get_content_analytics(db, current_user.tenant_id)
