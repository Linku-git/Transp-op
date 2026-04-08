from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.auth import User
from app.schemas.content_delivery import (
    ContentDeliveryResponse,
    DeliveryEventCreate,
    ViewEventCreate,
    CompletionEventCreate,
    EngagementMetrics,
    FeedContentResponse,
    FeedResponse,
)
from app.services.engagement_service import (
    record_delivery,
    record_view,
    record_completion,
    get_engagement_metrics,
    get_personalized_feed,
)
from app.services.content_service import get_content_by_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/content")


@router.get("/feed", response_model=FeedResponse)
async def get_feed_endpoint(
    employee_id: uuid.UUID = Query(..., description="Employee ID for personalized feed"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FeedResponse:
    """Get personalized content feed for an employee."""
    items, total = await get_personalized_feed(
        db=db,
        tenant_id=current_user.tenant_id,
        employee_id=employee_id,
        page=page,
        page_size=page_size,
    )
    pages = max(1, (total + page_size - 1) // page_size)

    return FeedResponse(
        data=[FeedContentResponse(**item) for item in items],
        total=total,
        page=page,
        pages=pages,
    )


@router.get("/{content_id}/engagement", response_model=EngagementMetrics)
async def get_engagement_endpoint(
    content_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EngagementMetrics:
    """Get engagement metrics for a content item."""
    content = await get_content_by_id(db, content_id, current_user.tenant_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    return await get_engagement_metrics(db, content_id, current_user.tenant_id)


@router.post("/{content_id}/deliver", response_model=ContentDeliveryResponse)
async def deliver_content_endpoint(
    content_id: uuid.UUID,
    body: DeliveryEventCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ContentDeliveryResponse:
    """Record content delivery to an employee."""
    content = await get_content_by_id(db, content_id, current_user.tenant_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    delivery = await record_delivery(
        db, current_user.tenant_id, content_id, body.employee_id
    )
    return ContentDeliveryResponse.model_validate(delivery)


@router.post("/{content_id}/view", response_model=ContentDeliveryResponse)
async def view_content_endpoint(
    content_id: uuid.UUID,
    employee_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ContentDeliveryResponse:
    """Record that an employee viewed content."""
    content = await get_content_by_id(db, content_id, current_user.tenant_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    delivery = await record_view(
        db, current_user.tenant_id, content_id, employee_id
    )
    return ContentDeliveryResponse.model_validate(delivery)


@router.post("/{content_id}/complete", response_model=ContentDeliveryResponse)
async def complete_content_endpoint(
    content_id: uuid.UUID,
    body: CompletionEventCreate,
    employee_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ContentDeliveryResponse:
    """Record that an employee completed content consumption."""
    content = await get_content_by_id(db, content_id, current_user.tenant_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    delivery = await record_completion(
        db,
        current_user.tenant_id,
        content_id,
        employee_id,
        quiz_score=body.quiz_score,
        time_spent_seconds=body.time_spent_seconds,
    )
    return ContentDeliveryResponse.model_validate(delivery)
