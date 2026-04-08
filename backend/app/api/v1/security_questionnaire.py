from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.auth import User
from app.models.security_questionnaire import SecurityQuestionnaire
from app.schemas.security_questionnaire import (
    SecurityQuestionnaireSubmit,
    SecurityQuestionnaireResponse,
    SecurityQuestionnaireHistory,
    SecurityQuestionnaireSummary,
)
from app.services.reassessment_scheduler import get_next_version

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/security")


@router.post("/questionnaire", response_model=SecurityQuestionnaireResponse)
async def submit_questionnaire(
    body: SecurityQuestionnaireSubmit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SecurityQuestionnaireResponse:
    """Submit a new security questionnaire response."""
    employee_id = current_user.employee_id
    if not employee_id:
        raise HTTPException(status_code=400, detail="User has no linked employee")

    version = await get_next_version(db, current_user.tenant_id, employee_id)

    questionnaire = SecurityQuestionnaire(
        tenant_id=current_user.tenant_id,
        employee_id=employee_id,
        version=version,
        overall_safety_rating=body.overall_safety_rating,
        responses=body.responses,
        vulnerable_stops=body.vulnerable_stops,
        night_concerns=body.night_concerns,
        submitted_at=datetime.now(timezone.utc),
        trigger_type=body.trigger_type,
    )
    db.add(questionnaire)
    await db.flush()
    await db.refresh(questionnaire)
    return SecurityQuestionnaireResponse.model_validate(questionnaire)


@router.get("/questionnaire/{employee_id}", response_model=SecurityQuestionnaireHistory)
async def get_questionnaire(
    employee_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SecurityQuestionnaireHistory:
    """Get latest questionnaire and submission history for an employee."""
    result = await db.execute(
        select(SecurityQuestionnaire)
        .where(
            SecurityQuestionnaire.tenant_id == current_user.tenant_id,
            SecurityQuestionnaire.employee_id == employee_id,
        )
        .order_by(SecurityQuestionnaire.version.desc())
    )
    all_submissions = list(result.scalars().all())

    if not all_submissions:
        return SecurityQuestionnaireHistory(
            latest=None,
            history=[],
            total_submissions=0,
        )

    latest = SecurityQuestionnaireResponse.model_validate(all_submissions[0])
    history = [
        SecurityQuestionnaireSummary.model_validate(s)
        for s in all_submissions
    ]

    return SecurityQuestionnaireHistory(
        latest=latest,
        history=history,
        total_submissions=len(all_submissions),
    )


@router.post("/questionnaire/trigger-reassessment")
async def trigger_reassessment(
    employee_ids: list[uuid.UUID],
    reason: str = Query(default="incident"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Trigger reassessment for specific employees after an incident."""
    # In production, this would send push notifications to affected employees
    logger.info(
        f"Reassessment triggered for {len(employee_ids)} employees, reason: {reason}"
    )
    return {
        "triggered": len(employee_ids),
        "employee_ids": [str(eid) for eid in employee_ids],
        "reason": reason,
        "message": f"Reassessment triggered for {len(employee_ids)} employees",
    }
