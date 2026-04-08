from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.auth import User
from app.schemas.survey import (
    SurveyCreate,
    SurveyUpdate,
    SurveyResponse as SurveyResponseSchema,
    SurveyListResponse,
    SurveySubmitRequest,
    SurveySubmitResponse,
    SurveyAggregationResponse,
)
from app.services.survey_service import (
    create_survey,
    get_survey,
    list_surveys,
    submit_response,
    get_aggregation,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/surveys")


@router.post("", response_model=SurveyResponseSchema)
async def create_survey_endpoint(
    body: SurveyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SurveyResponseSchema:
    questions_data = [q.model_dump() for q in body.questions]
    survey = await create_survey(
        db=db,
        tenant_id=current_user.tenant_id,
        content_id=body.content_id,
        title=body.title,
        description=body.description,
        questions=questions_data,
        is_anonymous=body.is_anonymous,
    )
    return SurveyResponseSchema.model_validate(survey)


@router.get("", response_model=SurveyListResponse)
async def list_surveys_endpoint(
    is_active: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SurveyListResponse:
    items, total = await list_surveys(
        db=db,
        tenant_id=current_user.tenant_id,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )
    pages = max(1, (total + page_size - 1) // page_size)
    return SurveyListResponse(
        data=[SurveyResponseSchema.model_validate(s) for s in items],
        total=total,
        page=page,
        pages=pages,
    )


@router.get("/{survey_id}", response_model=SurveyResponseSchema)
async def get_survey_endpoint(
    survey_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SurveyResponseSchema:
    survey = await get_survey(db, survey_id, current_user.tenant_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    return SurveyResponseSchema.model_validate(survey)


@router.put("/{survey_id}", response_model=SurveyResponseSchema)
async def update_survey_endpoint(
    survey_id: uuid.UUID,
    body: SurveyUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SurveyResponseSchema:
    survey = await get_survey(db, survey_id, current_user.tenant_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    update_data = body.model_dump(exclude_unset=True)
    if "questions" in update_data and update_data["questions"] is not None:
        update_data["questions"] = [
            q.model_dump() if hasattr(q, "model_dump") else q
            for q in update_data["questions"]
        ]
    for field, value in update_data.items():
        setattr(survey, field, value)

    await db.flush()
    await db.refresh(survey)
    return SurveyResponseSchema.model_validate(survey)


@router.post("/{survey_id}/respond", response_model=SurveySubmitResponse)
async def submit_response_endpoint(
    survey_id: uuid.UUID,
    body: SurveySubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SurveySubmitResponse:
    survey = await get_survey(db, survey_id, current_user.tenant_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    if not survey.is_active:
        raise HTTPException(status_code=400, detail="Survey is closed")

    try:
        response = await submit_response(
            db=db,
            tenant_id=current_user.tenant_id,
            survey=survey,
            employee_id=body.employee_id,
            responses=body.responses,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return SurveySubmitResponse.model_validate(response)


@router.get("/{survey_id}/aggregation", response_model=SurveyAggregationResponse)
async def get_aggregation_endpoint(
    survey_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SurveyAggregationResponse:
    survey = await get_survey(db, survey_id, current_user.tenant_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    return await get_aggregation(db, survey, current_user.tenant_id)
