from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.fleet_context import FleetContext
from app.schemas.fleet_context import FleetContextResponse
from app.services.sotreg.context_service import compute_fleet_diagnostics

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sotreg/context")


@router.get("/snapshot", response_model=FleetContextResponse)
async def get_fleet_context_snapshot(
    current_user: User = Depends(require_role("admin", "drh", "responsable_exploitation")),
    db: AsyncSession = Depends(get_db),
) -> FleetContext:
    """Compute and persist a fleet diagnostics snapshot."""
    diagnostics = await compute_fleet_diagnostics(db, current_user.tenant_id)

    snapshot = FleetContext(
        tenant_id=current_user.tenant_id,
        **diagnostics,
    )
    db.add(snapshot)
    await db.flush()
    await db.refresh(snapshot)

    logger.info(
        "Fleet context snapshot %s created for tenant %s",
        snapshot.id,
        current_user.tenant_id,
    )
    return snapshot
