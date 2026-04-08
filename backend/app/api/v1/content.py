from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.auth import User
from app.schemas.content import (
    ContentCreate,
    ContentUpdate,
    ContentResponse,
    ContentListResponse,
)
from app.services.content_service import (
    create_content,
    list_content,
    get_content_by_id,
    publish_content,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/content")


@router.post("", response_model=ContentResponse)
async def create_content_endpoint(
    body: ContentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ContentResponse:
    content = await create_content(
        db=db,
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        title=body.title,
        body=body.body,
        content_type=body.content_type,
        media_url=body.media_url,
        target_sites=body.target_sites,
        target_departments=body.target_departments,
        target_shifts=body.target_shifts,
        expires_at=body.expires_at,
    )
    return ContentResponse.model_validate(content)


@router.get("", response_model=ContentListResponse)
async def list_content_endpoint(
    content_type: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    site_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ContentListResponse:
    items, total = await list_content(
        db=db,
        tenant_id=current_user.tenant_id,
        content_type=content_type,
        is_active=is_active,
        site_id=site_id,
        page=page,
        page_size=page_size,
    )
    pages = max(1, (total + page_size - 1) // page_size)

    return ContentListResponse(
        data=[ContentResponse.model_validate(c) for c in items],
        total=total,
        page=page,
        pages=pages,
    )


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content_endpoint(
    content_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ContentResponse:
    content = await get_content_by_id(db, content_id, current_user.tenant_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return ContentResponse.model_validate(content)


@router.put("/{content_id}", response_model=ContentResponse)
async def update_content_endpoint(
    content_id: uuid.UUID,
    body: ContentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ContentResponse:
    content = await get_content_by_id(db, content_id, current_user.tenant_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(content, field, value)

    await db.flush()
    await db.refresh(content)
    return ContentResponse.model_validate(content)


@router.delete("/{content_id}")
async def delete_content_endpoint(
    content_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    content = await get_content_by_id(db, content_id, current_user.tenant_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    content.is_active = False
    await db.flush()
    return {"detail": "Content deactivated"}


@router.post("/{content_id}/publish", response_model=ContentResponse)
async def publish_content_endpoint(
    content_id: uuid.UUID,
    publish: bool = Query(default=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ContentResponse:
    content = await get_content_by_id(db, content_id, current_user.tenant_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    content = await publish_content(db, content, publish)
    return ContentResponse.model_validate(content)
