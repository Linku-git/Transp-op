from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.auth import User
from app.schemas.training_module import (
    CompletionListResponse,
    CompletionRecord,
    SyncRequest,
    SyncResult,
    WebhookPayload,
)
from app.services.lms.sync_service import (
    full_sync,
    get_completions,
    handle_webhook_event,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/training")


@router.post("/sync-lms", response_model=SyncResult)
async def sync_lms_endpoint(
    body: SyncRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SyncResult:
    """Trigger bidirectional LMS sync."""
    result = await full_sync(
        db=db,
        tenant_id=current_user.tenant_id,
        provider=body.provider,
    )
    return SyncResult(**result)


@router.get("/completions", response_model=CompletionListResponse)
async def get_completions_endpoint(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CompletionListResponse:
    """Get training completion records."""
    records, total = await get_completions(
        db=db,
        tenant_id=current_user.tenant_id,
        page=page,
        page_size=page_size,
    )
    pages = max(1, (total + page_size - 1) // page_size)
    return CompletionListResponse(
        data=[CompletionRecord(**r) for r in records],
        total=total,
        page=page,
        pages=pages,
    )


@router.post("/webhook/{provider}")
async def webhook_endpoint(
    provider: str,
    body: WebhookPayload,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Handle real-time webhook from LMS provider.

    Note: Webhooks bypass auth — validated by provider-specific signatures.
    """
    # Use a default tenant for webhook processing
    # In production, resolve tenant from webhook signature or API key
    from app.models.auth import Tenant
    from sqlalchemy import select

    result = await db.execute(select(Tenant).limit(1))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=500, detail="No tenant configured")

    success = await handle_webhook_event(
        db=db,
        tenant_id=tenant.id,
        provider=provider,
        payload=body.model_dump(),
    )
    return {"processed": success}
