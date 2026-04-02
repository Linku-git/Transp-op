from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.settings import OptimizationSettings
from app.schemas.settings import SettingsResponse, SettingsUpdateRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings")


# ---------------------------------------------------------------------------
# GET /settings — get or create default settings for current tenant
# ---------------------------------------------------------------------------


@router.get("", response_model=SettingsResponse)
async def get_settings(
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> SettingsResponse:
    """Get optimization settings for the current tenant.

    If no settings exist yet, create a row with default values and return it.
    """
    stmt = select(OptimizationSettings).where(
        OptimizationSettings.tenant_id == current_user.tenant_id
    )
    result = await db.execute(stmt)
    settings = result.scalar_one_or_none()

    if settings is None:
        logger.info("Creating default optimization settings for tenant %s", current_user.tenant_id)
        settings = OptimizationSettings(tenant_id=current_user.tenant_id)
        db.add(settings)
        await db.flush()
        await db.refresh(settings)

    return SettingsResponse.model_validate(settings)


# ---------------------------------------------------------------------------
# PUT /settings — update settings (partial)
# ---------------------------------------------------------------------------


@router.put("", response_model=SettingsResponse)
async def update_settings(
    body: SettingsUpdateRequest,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> SettingsResponse:
    """Update optimization settings for the current tenant.

    Only provided fields are updated (partial update semantics).
    """
    stmt = select(OptimizationSettings).where(
        OptimizationSettings.tenant_id == current_user.tenant_id
    )
    result = await db.execute(stmt)
    settings = result.scalar_one_or_none()

    if settings is None:
        settings = OptimizationSettings(tenant_id=current_user.tenant_id)
        db.add(settings)
        await db.flush()
        await db.refresh(settings)

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)

    await db.flush()
    await db.refresh(settings)

    logger.info(
        "Updated optimization settings for tenant %s: %s",
        current_user.tenant_id,
        list(update_data.keys()),
    )
    return SettingsResponse.model_validate(settings)
