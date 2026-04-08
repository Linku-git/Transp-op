from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Content

logger = logging.getLogger(__name__)


async def create_content(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    created_by: uuid.UUID,
    **kwargs,
) -> Content:
    content = Content(
        tenant_id=tenant_id,
        created_by=created_by,
        **kwargs,
    )
    db.add(content)
    await db.flush()
    await db.refresh(content)
    return content


async def list_content(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    content_type: str | None = None,
    is_active: bool | None = None,
    site_id: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Content], int]:
    conditions = [Content.tenant_id == tenant_id]

    if content_type:
        conditions.append(Content.content_type == content_type)
    if is_active is not None:
        conditions.append(Content.is_active == is_active)

    # Total count
    total_result = await db.execute(
        select(func.count()).select_from(Content).where(*conditions)
    )
    total = total_result.scalar() or 0

    # Paginated query
    result = await db.execute(
        select(Content)
        .where(*conditions)
        .order_by(Content.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(result.scalars().all())

    # Audience filter (post-query for JSONB contains)
    if site_id:
        items = [
            c for c in items
            if c.target_sites is None or site_id in c.target_sites
        ]

    return items, total


async def get_content_by_id(
    db: AsyncSession,
    content_id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> Content | None:
    result = await db.execute(
        select(Content).where(
            Content.id == content_id,
            Content.tenant_id == tenant_id,
        )
    )
    return result.scalar_one_or_none()


async def publish_content(
    db: AsyncSession,
    content: Content,
    publish: bool = True,
) -> Content:
    if publish:
        content.published_at = datetime.now(timezone.utc)
        content.is_active = True
    else:
        content.published_at = None
        content.is_active = False

    await db.flush()
    await db.refresh(content)
    return content
