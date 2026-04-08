from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Content
from app.models.content_delivery import ContentDelivery
from app.models.employee import Employee
from app.schemas.content_delivery import EngagementMetrics

logger = logging.getLogger(__name__)


async def get_or_create_delivery(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    content_id: uuid.UUID,
    employee_id: uuid.UUID,
) -> ContentDelivery:
    """Get existing delivery record or create a new one."""
    result = await db.execute(
        select(ContentDelivery).where(
            ContentDelivery.content_id == content_id,
            ContentDelivery.employee_id == employee_id,
        )
    )
    delivery = result.scalar_one_or_none()

    if not delivery:
        delivery = ContentDelivery(
            tenant_id=tenant_id,
            content_id=content_id,
            employee_id=employee_id,
            delivered_at=datetime.now(timezone.utc),
        )
        db.add(delivery)
        await db.flush()
        await db.refresh(delivery)

    return delivery


async def record_delivery(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    content_id: uuid.UUID,
    employee_id: uuid.UUID,
) -> ContentDelivery:
    """Record that content was delivered to an employee."""
    return await get_or_create_delivery(db, tenant_id, content_id, employee_id)


async def record_view(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    content_id: uuid.UUID,
    employee_id: uuid.UUID,
) -> ContentDelivery:
    """Record that content was viewed by an employee."""
    delivery = await get_or_create_delivery(db, tenant_id, content_id, employee_id)
    if not delivery.viewed_at:
        delivery.viewed_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(delivery)
    return delivery


async def record_completion(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    content_id: uuid.UUID,
    employee_id: uuid.UUID,
    quiz_score: float | None = None,
    time_spent_seconds: int | None = None,
) -> ContentDelivery:
    """Record that content was fully consumed by an employee."""
    delivery = await get_or_create_delivery(db, tenant_id, content_id, employee_id)
    if not delivery.viewed_at:
        delivery.viewed_at = datetime.now(timezone.utc)
    delivery.completed_at = datetime.now(timezone.utc)
    if quiz_score is not None:
        delivery.quiz_score = quiz_score
    if time_spent_seconds is not None:
        delivery.time_spent_seconds = time_spent_seconds
    await db.flush()
    await db.refresh(delivery)
    return delivery


async def get_engagement_metrics(
    db: AsyncSession,
    content_id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> EngagementMetrics:
    """Compute aggregated engagement metrics for a content item."""
    base = select(ContentDelivery).where(
        ContentDelivery.content_id == content_id,
        ContentDelivery.tenant_id == tenant_id,
    )

    total_result = await db.execute(
        select(func.count()).select_from(ContentDelivery).where(
            ContentDelivery.content_id == content_id,
            ContentDelivery.tenant_id == tenant_id,
        )
    )
    total_deliveries = total_result.scalar() or 0

    views_result = await db.execute(
        select(func.count()).select_from(ContentDelivery).where(
            ContentDelivery.content_id == content_id,
            ContentDelivery.tenant_id == tenant_id,
            ContentDelivery.viewed_at.isnot(None),
        )
    )
    total_views = views_result.scalar() or 0

    completions_result = await db.execute(
        select(func.count()).select_from(ContentDelivery).where(
            ContentDelivery.content_id == content_id,
            ContentDelivery.tenant_id == tenant_id,
            ContentDelivery.completed_at.isnot(None),
        )
    )
    total_completions = completions_result.scalar() or 0

    avg_quiz_result = await db.execute(
        select(func.avg(ContentDelivery.quiz_score)).where(
            ContentDelivery.content_id == content_id,
            ContentDelivery.tenant_id == tenant_id,
            ContentDelivery.quiz_score.isnot(None),
        )
    )
    avg_quiz = avg_quiz_result.scalar()

    avg_time_result = await db.execute(
        select(func.avg(ContentDelivery.time_spent_seconds)).where(
            ContentDelivery.content_id == content_id,
            ContentDelivery.tenant_id == tenant_id,
            ContentDelivery.time_spent_seconds.isnot(None),
        )
    )
    avg_time = avg_time_result.scalar()

    view_rate = (total_views / total_deliveries * 100.0) if total_deliveries > 0 else 0.0
    completion_rate = (total_completions / total_deliveries * 100.0) if total_deliveries > 0 else 0.0

    return EngagementMetrics(
        content_id=content_id,
        total_deliveries=total_deliveries,
        total_views=total_views,
        total_completions=total_completions,
        view_rate=round(view_rate, 1),
        completion_rate=round(completion_rate, 1),
        avg_quiz_score=round(avg_quiz, 1) if avg_quiz is not None else None,
        avg_time_spent_seconds=round(avg_time, 1) if avg_time is not None else None,
    )


async def get_personalized_feed(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    employee_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict], int]:
    """Return content targeted at the employee's site, department, and shift."""
    # Get employee details
    employee_result = await db.execute(
        select(Employee).where(Employee.id == employee_id)
    )
    employee = employee_result.scalar_one_or_none()

    if not employee:
        return [], 0

    site_id = str(employee.site_id) if employee.site_id else None
    department = employee.department
    shift = employee.shift_time

    now = datetime.now(timezone.utc)

    # Get published, active, non-expired content for this tenant
    conditions = [
        Content.tenant_id == tenant_id,
        Content.is_active.is_(True),
        Content.published_at.isnot(None),
    ]

    result = await db.execute(
        select(Content)
        .where(*conditions)
        .order_by(Content.published_at.desc())
    )
    all_content = list(result.scalars().all())

    # Filter by audience targeting and expiry
    matched = []
    for c in all_content:
        # Skip expired
        if c.expires_at and c.expires_at < now:
            continue

        # Site match: None means all sites
        if c.target_sites and site_id and site_id not in c.target_sites:
            continue

        # Department match: None means all departments
        if c.target_departments and department and department not in c.target_departments:
            continue

        # Shift match: None means all shifts
        if c.target_shifts and shift and shift not in c.target_shifts:
            continue

        matched.append(c)

    total = len(matched)

    # Paginate
    start = (page - 1) * page_size
    page_items = matched[start : start + page_size]

    # Get delivery status for this employee
    if page_items:
        content_ids = [c.id for c in page_items]
        delivery_result = await db.execute(
            select(ContentDelivery).where(
                ContentDelivery.employee_id == employee_id,
                ContentDelivery.content_id.in_(content_ids),
            )
        )
        deliveries = {d.content_id: d for d in delivery_result.scalars().all()}
    else:
        deliveries = {}

    feed_items = []
    for c in page_items:
        d = deliveries.get(c.id)
        feed_items.append({
            "id": c.id,
            "title": c.title,
            "body": c.body,
            "content_type": c.content_type,
            "media_url": c.media_url,
            "published_at": c.published_at,
            "expires_at": c.expires_at,
            "delivered": d is not None,
            "viewed": d is not None and d.viewed_at is not None,
            "completed": d is not None and d.completed_at is not None,
        })

        # Auto-record delivery
        if d is None:
            await record_delivery(db, tenant_id, c.id, employee_id)

    return feed_items, total
