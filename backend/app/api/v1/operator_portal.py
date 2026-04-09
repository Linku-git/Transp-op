from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.auth import User
from app.models.sizing_plan_export import SizingPlanExport
from app.schemas.operator_portal import (
    OperatorSizingPlan,
    OperatorSizingPlanList,
    AcknowledgeResponse,
    ServiceIssueCreate,
    ServiceIssueResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/operator")


@router.get("/sizing-plans", response_model=OperatorSizingPlanList)
async def list_operator_sizing_plans(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OperatorSizingPlanList:
    """List sizing plans assigned to the current operator."""
    # In production, filter by operator_id linked to current_user
    conditions = [
        SizingPlanExport.tenant_id == current_user.tenant_id,
        SizingPlanExport.status.in_(["completed", "acknowledged"]),
    ]

    total = (await db.execute(
        select(func.count()).select_from(SizingPlanExport).where(*conditions)
    )).scalar() or 0

    result = await db.execute(
        select(SizingPlanExport)
        .where(*conditions)
        .order_by(SizingPlanExport.created_at.desc())
    )
    items = list(result.scalars().all())

    plans = [
        OperatorSizingPlan(
            id=p.id,
            version=p.version,
            format=p.format,
            status=p.status,
            file_url=p.file_url,
            content_summary=p.content_summary,
            acknowledged=p.status == "acknowledged",
            acknowledged_at=None,
            created_at=p.created_at,
        )
        for p in items
    ]

    return OperatorSizingPlanList(data=plans, total=total)


@router.get("/sizing-plans/{plan_id}", response_model=OperatorSizingPlan)
async def get_operator_sizing_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OperatorSizingPlan:
    """Get sizing plan details."""
    result = await db.execute(
        select(SizingPlanExport).where(
            SizingPlanExport.id == plan_id,
            SizingPlanExport.tenant_id == current_user.tenant_id,
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Sizing plan not found")

    return OperatorSizingPlan(
        id=plan.id,
        version=plan.version,
        format=plan.format,
        status=plan.status,
        file_url=plan.file_url,
        content_summary=plan.content_summary,
        acknowledged=plan.status == "acknowledged",
        created_at=plan.created_at,
    )


@router.post("/sizing-plans/{plan_id}/acknowledge", response_model=AcknowledgeResponse)
async def acknowledge_sizing_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AcknowledgeResponse:
    """Acknowledge receipt of a sizing plan."""
    result = await db.execute(
        select(SizingPlanExport).where(
            SizingPlanExport.id == plan_id,
            SizingPlanExport.tenant_id == current_user.tenant_id,
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Sizing plan not found")

    now = datetime.now(timezone.utc)
    plan.status = "acknowledged"
    await db.flush()

    return AcknowledgeResponse(
        plan_id=plan.id,
        acknowledged=True,
        acknowledged_at=now,
    )


@router.post("/service-issues", response_model=ServiceIssueResponse)
async def report_service_issue(
    body: ServiceIssueCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ServiceIssueResponse:
    """Submit a service issue report."""
    now = datetime.now(timezone.utc)

    # Store as a simple response object — in production would write to a ServiceIssue model
    return ServiceIssueResponse(
        id=uuid.uuid4(),
        operator_id=current_user.id,
        issue_type=body.issue_type,
        description=body.description,
        affected_route=body.affected_route,
        incident_date=body.incident_date,
        status="open",
        created_at=now,
    )
