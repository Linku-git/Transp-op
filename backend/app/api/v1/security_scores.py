from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.auth import User
from app.models.security_score import SecurityScore
from app.schemas.security_score import (
    SecurityScoreResponse,
    SecurityScoreListResponse,
    SecurityScoreDetail,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/security")


@router.get("/scores", response_model=SecurityScoreListResponse)
async def list_security_scores(
    risk_level: str | None = Query(default=None, pattern="^(low|medium|high|critical)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SecurityScoreListResponse:
    conditions = [SecurityScore.tenant_id == current_user.tenant_id]
    if risk_level:
        conditions.append(SecurityScore.risk_level == risk_level)

    result = await db.execute(
        select(SecurityScore)
        .where(*conditions)
        .order_by(SecurityScore.score.asc())
    )
    scores = list(result.scalars().all())

    return SecurityScoreListResponse(
        data=[SecurityScoreResponse.model_validate(s) for s in scores],
        total=len(scores),
    )


@router.get("/scores/{employee_id}", response_model=SecurityScoreDetail)
async def get_security_score(
    employee_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SecurityScoreDetail:
    result = await db.execute(
        select(SecurityScore)
        .where(
            SecurityScore.tenant_id == current_user.tenant_id,
            SecurityScore.employee_id == employee_id,
        )
        .order_by(SecurityScore.computed_at.desc())
        .limit(1)
    )
    score = result.scalar_one_or_none()
    if not score:
        raise HTTPException(status_code=404, detail="Security score not found")

    factors = score.contributing_factors or {}

    return SecurityScoreDetail(
        score=score.score,
        risk_level=score.risk_level,
        contributing_factors=factors,
        computed_at=score.computed_at,
        employee_id=score.employee_id,
        questionnaire_rating=factors.get("questionnaire_rating"),
        vulnerable_stop_count=factors.get("vulnerable_stop_count", 0),
        night_commute_exposure=factors.get("night_commute_exposure", 0),
        avg_stop_isolation=factors.get("avg_stop_isolation", 0),
    )
