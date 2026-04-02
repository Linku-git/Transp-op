from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.services.hr_analytics import compute_hr_kpis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/kpis")


@router.get("/hr", response_model=dict)
async def get_hr_kpis(
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return all HR dashboard KPIs: mobility coverage, absenteeism, retention, shadow zones."""
    result = await compute_hr_kpis(current_user.tenant_id, db)
    logger.info("HR KPIs computed for tenant %s by user %s", current_user.tenant_id, current_user.id)
    return result
