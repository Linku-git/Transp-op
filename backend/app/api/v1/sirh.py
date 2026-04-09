from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.auth import User
from app.models.sirh_connection import SIRHConnection
from app.models.sync_conflict import SyncConflict
from app.schemas.sirh import (
    SIRHConnectionCreate,
    SIRHConnectionUpdate,
    SIRHConnectionResponse,
    SIRHConnectionListResponse,
    SyncLogResponse,
    SyncLogListResponse,
    SyncConflictResponse,
    ConflictResolveRequest,
    SyncTriggerResponse,
)
from app.services.sirh.sync_engine import SyncEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sirh")


@router.post("/connections", response_model=SIRHConnectionResponse)
async def create_connection(
    body: SIRHConnectionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SIRHConnectionResponse:
    conn = SIRHConnection(
        tenant_id=current_user.tenant_id,
        provider=body.provider,
        name=body.name,
        config=body.config,
        sync_frequency=body.sync_frequency,
        conflict_strategy=body.conflict_strategy,
    )
    db.add(conn)
    await db.flush()
    await db.refresh(conn)
    return SIRHConnectionResponse.model_validate(conn)


@router.get("/connections", response_model=SIRHConnectionListResponse)
async def list_connections(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SIRHConnectionListResponse:
    conditions = [
        SIRHConnection.tenant_id == current_user.tenant_id,
        SIRHConnection.is_active.is_(True),
    ]
    total_result = await db.execute(
        select(func.count()).select_from(SIRHConnection).where(*conditions)
    )
    total = total_result.scalar() or 0

    result = await db.execute(
        select(SIRHConnection)
        .where(*conditions)
        .order_by(SIRHConnection.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(result.scalars().all())
    pages = max(1, (total + page_size - 1) // page_size)

    return SIRHConnectionListResponse(
        data=[SIRHConnectionResponse.model_validate(c) for c in items],
        total=total,
        page=page,
        pages=pages,
    )


@router.get("/connections/{connection_id}", response_model=SIRHConnectionResponse)
async def get_connection(
    connection_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SIRHConnectionResponse:
    result = await db.execute(
        select(SIRHConnection).where(
            SIRHConnection.id == connection_id,
            SIRHConnection.tenant_id == current_user.tenant_id,
        )
    )
    conn = result.scalar_one_or_none()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    return SIRHConnectionResponse.model_validate(conn)


@router.put("/connections/{connection_id}", response_model=SIRHConnectionResponse)
async def update_connection(
    connection_id: uuid.UUID,
    body: SIRHConnectionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SIRHConnectionResponse:
    result = await db.execute(
        select(SIRHConnection).where(
            SIRHConnection.id == connection_id,
            SIRHConnection.tenant_id == current_user.tenant_id,
        )
    )
    conn = result.scalar_one_or_none()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(conn, field, value)

    await db.flush()
    await db.refresh(conn)
    return SIRHConnectionResponse.model_validate(conn)


@router.delete("/connections/{connection_id}")
async def delete_connection(
    connection_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(
        select(SIRHConnection).where(
            SIRHConnection.id == connection_id,
            SIRHConnection.tenant_id == current_user.tenant_id,
        )
    )
    conn = result.scalar_one_or_none()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    conn.is_active = False
    conn.status = "deleted"
    await db.flush()
    return {"detail": "Connection deactivated"}


@router.post("/sync/{connection_id}", response_model=SyncTriggerResponse)
async def trigger_sync(
    connection_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SyncTriggerResponse:
    result = await db.execute(
        select(SIRHConnection).where(
            SIRHConnection.id == connection_id,
            SIRHConnection.tenant_id == current_user.tenant_id,
        )
    )
    conn = result.scalar_one_or_none()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    if conn.status != "active":
        raise HTTPException(status_code=400, detail="Connection is not active")

    engine = SyncEngine(db)

    # In production, the connector would fetch from the SIRH API.
    # Here we run with empty data to create the sync log.
    sync_log = await engine.run_sync(conn, employee_data=[])

    return SyncTriggerResponse(
        sync_log_id=sync_log.id,
        status=sync_log.status,
        message=f"Sync completed: {sync_log.records_created} created, {sync_log.records_updated} updated",
    )


@router.get(
    "/sync/{connection_id}/logs", response_model=SyncLogListResponse
)
async def get_sync_logs(
    connection_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SyncLogListResponse:
    engine = SyncEngine(db)
    items, total = await engine.get_sync_logs(
        connection_id, current_user.tenant_id, page, page_size
    )
    pages = max(1, (total + page_size - 1) // page_size)
    return SyncLogListResponse(
        data=[SyncLogResponse.model_validate(l) for l in items],
        total=total,
        page=page,
        pages=pages,
    )


@router.get(
    "/conflicts/{sync_log_id}", response_model=list[SyncConflictResponse]
)
async def get_conflicts(
    sync_log_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SyncConflictResponse]:
    engine = SyncEngine(db)
    conflicts = await engine.get_conflicts(sync_log_id, current_user.tenant_id)
    return [SyncConflictResponse.model_validate(c) for c in conflicts]


@router.put("/conflicts/{conflict_id}/resolve", response_model=SyncConflictResponse)
async def resolve_conflict(
    conflict_id: uuid.UUID,
    body: ConflictResolveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SyncConflictResponse:
    result = await db.execute(
        select(SyncConflict).where(
            SyncConflict.id == conflict_id,
            SyncConflict.tenant_id == current_user.tenant_id,
        )
    )
    conflict = result.scalar_one_or_none()
    if not conflict:
        raise HTTPException(status_code=404, detail="Conflict not found")

    from app.services.sirh.conflict_resolver import ConflictResolver
    resolver = ConflictResolver()
    updated = await resolver.resolve_conflict(
        db, conflict, body.resolution, body.manual_value
    )
    return SyncConflictResponse.model_validate(updated)
