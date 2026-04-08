from __future__ import annotations

import logging
import uuid

from sqlalchemy import func, select, case, cast, Float
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Content
from app.models.content_delivery import ContentDelivery

logger = logging.getLogger(__name__)


async def get_content_analytics(
    db: AsyncSession,
    tenant_id: uuid.UUID,
) -> dict:
    """Aggregate engagement analytics across all content."""
    base = [ContentDelivery.tenant_id == tenant_id]

    # Overview metrics
    total_deliveries = (await db.execute(
        select(func.count()).select_from(ContentDelivery).where(*base)
    )).scalar() or 0

    total_views = (await db.execute(
        select(func.count()).select_from(ContentDelivery).where(
            *base, ContentDelivery.viewed_at.isnot(None)
        )
    )).scalar() or 0

    total_completions = (await db.execute(
        select(func.count()).select_from(ContentDelivery).where(
            *base, ContentDelivery.completed_at.isnot(None)
        )
    )).scalar() or 0

    avg_quiz = (await db.execute(
        select(func.avg(ContentDelivery.quiz_score)).where(
            *base, ContentDelivery.quiz_score.isnot(None)
        )
    )).scalar()

    avg_time = (await db.execute(
        select(func.avg(ContentDelivery.time_spent_seconds)).where(
            *base, ContentDelivery.time_spent_seconds.isnot(None)
        )
    )).scalar()

    total_time = (await db.execute(
        select(func.sum(ContentDelivery.time_spent_seconds)).where(
            *base, ContentDelivery.time_spent_seconds.isnot(None)
        )
    )).scalar() or 0

    # Training hours recovered (total time spent / 3600)
    training_hours_recovered = round(total_time / 3600, 1) if total_time else 0.0

    # Per-content performance ranking
    content_stats_query = (
        select(
            Content.id,
            Content.title,
            Content.content_type,
            func.count(ContentDelivery.id).label("deliveries"),
            func.count(ContentDelivery.viewed_at).label("views"),
            func.count(ContentDelivery.completed_at).label("completions"),
            func.avg(ContentDelivery.quiz_score).label("avg_score"),
            func.avg(ContentDelivery.time_spent_seconds).label("avg_time"),
        )
        .join(ContentDelivery, ContentDelivery.content_id == Content.id)
        .where(Content.tenant_id == tenant_id)
        .group_by(Content.id, Content.title, Content.content_type)
        .order_by(func.count(ContentDelivery.completed_at).desc())
    )
    content_result = await db.execute(content_stats_query)
    content_ranking = [
        {
            "content_id": str(row.id),
            "title": row.title,
            "content_type": row.content_type,
            "deliveries": row.deliveries,
            "views": row.views,
            "completions": row.completions,
            "avg_quiz_score": round(row.avg_score, 1) if row.avg_score else None,
            "avg_time_seconds": round(row.avg_time, 0) if row.avg_time else None,
        }
        for row in content_result.all()
    ]

    # By content type
    type_stats_query = (
        select(
            Content.content_type,
            func.count(ContentDelivery.id).label("deliveries"),
            func.count(ContentDelivery.viewed_at).label("views"),
            func.count(ContentDelivery.completed_at).label("completions"),
        )
        .join(ContentDelivery, ContentDelivery.content_id == Content.id)
        .where(Content.tenant_id == tenant_id)
        .group_by(Content.content_type)
    )
    type_result = await db.execute(type_stats_query)
    by_type = {
        row.content_type: {
            "deliveries": row.deliveries,
            "views": row.views,
            "completions": row.completions,
        }
        for row in type_result.all()
    }

    return {
        "overview": {
            "total_deliveries": total_deliveries,
            "total_views": total_views,
            "total_completions": total_completions,
            "view_rate": round(total_views / total_deliveries * 100, 1) if total_deliveries > 0 else 0,
            "completion_rate": round(total_completions / total_deliveries * 100, 1) if total_deliveries > 0 else 0,
            "avg_quiz_score": round(avg_quiz, 1) if avg_quiz else None,
            "avg_time_spent_seconds": round(avg_time, 0) if avg_time else None,
            "training_hours_recovered": training_hours_recovered,
        },
        "content_ranking": content_ranking,
        "by_type": by_type,
    }
