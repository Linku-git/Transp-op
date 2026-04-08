from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.survey import Survey
from app.models.survey_response import SurveyResponse
from app.schemas.survey import (
    AnswerItem,
    QuestionAggregation,
    SurveyAggregationResponse,
)

logger = logging.getLogger(__name__)


async def create_survey(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    content_id: uuid.UUID,
    title: str,
    questions: list[dict],
    description: str | None = None,
    is_anonymous: bool = False,
) -> Survey:
    survey = Survey(
        tenant_id=tenant_id,
        content_id=content_id,
        title=title,
        description=description,
        questions=questions,
        is_anonymous=is_anonymous,
    )
    db.add(survey)
    await db.flush()
    await db.refresh(survey)
    return survey


async def get_survey(
    db: AsyncSession,
    survey_id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> Survey | None:
    result = await db.execute(
        select(Survey).where(
            Survey.id == survey_id,
            Survey.tenant_id == tenant_id,
        )
    )
    return result.scalar_one_or_none()


async def list_surveys(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    is_active: bool | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Survey], int]:
    conditions = [Survey.tenant_id == tenant_id]
    if is_active is not None:
        conditions.append(Survey.is_active == is_active)

    total_result = await db.execute(
        select(func.count()).select_from(Survey).where(*conditions)
    )
    total = total_result.scalar() or 0

    result = await db.execute(
        select(Survey)
        .where(*conditions)
        .order_by(Survey.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(result.scalars().all())
    return items, total


async def submit_response(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    survey: Survey,
    employee_id: uuid.UUID | None,
    responses: list[AnswerItem],
) -> SurveyResponse:
    """Submit a survey response with validation."""
    # Validate responses against questions
    question_map = {q["id"]: q for q in survey.questions}

    for answer in responses:
        question = question_map.get(answer.question_id)
        if not question:
            raise ValueError(f"Unknown question: {answer.question_id}")

        qtype = question.get("question_type", "text")

        if question.get("required", True) and answer.value is None:
            raise ValueError(
                f"Required question '{answer.question_id}' has no answer"
            )

        if answer.value is not None:
            _validate_answer(answer, question, qtype)

    # For non-anonymous surveys, check duplicate
    if not survey.is_anonymous and employee_id:
        existing = await db.execute(
            select(SurveyResponse).where(
                SurveyResponse.survey_id == survey.id,
                SurveyResponse.employee_id == employee_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Already submitted a response to this survey")

    # For anonymous surveys, clear employee_id
    if survey.is_anonymous:
        employee_id = None

    response = SurveyResponse(
        tenant_id=tenant_id,
        survey_id=survey.id,
        employee_id=employee_id,
        responses=[a.model_dump() for a in responses],
        submitted_at=datetime.now(timezone.utc),
    )
    db.add(response)

    # Increment response count
    survey.response_count = (survey.response_count or 0) + 1

    await db.flush()
    await db.refresh(response)
    return response


def _validate_answer(
    answer: AnswerItem, question: dict, qtype: str
) -> None:
    """Validate a single answer against its question schema."""
    options = question.get("options", [])
    option_values = [o.get("value") or o.get("text") for o in options]

    if qtype == "single_choice":
        if not isinstance(answer.value, str):
            raise ValueError(
                f"single_choice expects string, got {type(answer.value).__name__}"
            )
        if options and answer.value not in option_values:
            raise ValueError(
                f"Invalid choice '{answer.value}' for question '{answer.question_id}'"
            )

    elif qtype == "multiple_choice":
        if not isinstance(answer.value, list):
            raise ValueError(
                f"multiple_choice expects list, got {type(answer.value).__name__}"
            )
        for v in answer.value:
            if options and v not in option_values:
                raise ValueError(
                    f"Invalid choice '{v}' for question '{answer.question_id}'"
                )

    elif qtype == "rating":
        if not isinstance(answer.value, (int, float)):
            raise ValueError(
                f"rating expects number, got {type(answer.value).__name__}"
            )
        min_val = question.get("min_value", 1)
        max_val = question.get("max_value", 5)
        if answer.value < min_val or answer.value > max_val:
            raise ValueError(
                f"Rating must be between {min_val} and {max_val}"
            )

    elif qtype == "slider":
        if not isinstance(answer.value, (int, float)):
            raise ValueError(
                f"slider expects number, got {type(answer.value).__name__}"
            )
        min_val = question.get("min_value", 0)
        max_val = question.get("max_value", 100)
        if answer.value < min_val or answer.value > max_val:
            raise ValueError(
                f"Slider value must be between {min_val} and {max_val}"
            )

    elif qtype == "text":
        if not isinstance(answer.value, str):
            raise ValueError(
                f"text expects string, got {type(answer.value).__name__}"
            )


async def get_aggregation(
    db: AsyncSession,
    survey: Survey,
    tenant_id: uuid.UUID,
) -> SurveyAggregationResponse:
    """Aggregate responses for a survey."""
    result = await db.execute(
        select(SurveyResponse).where(
            SurveyResponse.survey_id == survey.id,
            SurveyResponse.tenant_id == tenant_id,
        )
    )
    all_responses = list(result.scalars().all())

    question_map = {q["id"]: q for q in survey.questions}
    question_aggregations: list[QuestionAggregation] = []

    for q in survey.questions:
        qid = q["id"]
        qtype = q.get("question_type", "text")
        answers = []

        for resp in all_responses:
            for a in resp.responses:
                if a.get("question_id") == qid and a.get("value") is not None:
                    answers.append(a["value"])

        agg = QuestionAggregation(
            question_id=qid,
            question_text=q["text"],
            question_type=qtype,
            total_responses=len(answers),
        )

        if qtype in ("single_choice", "multiple_choice"):
            dist: dict[str, int] = {}
            for val in answers:
                if isinstance(val, list):
                    for v in val:
                        dist[str(v)] = dist.get(str(v), 0) + 1
                else:
                    dist[str(val)] = dist.get(str(val), 0) + 1
            agg.distribution = dist

        elif qtype in ("rating", "slider"):
            numeric = [v for v in answers if isinstance(v, (int, float))]
            if numeric:
                agg.average = round(sum(numeric) / len(numeric), 2)
            agg.distribution = {}
            for v in answers:
                key = str(v)
                agg.distribution[key] = agg.distribution.get(key, 0) + 1

        elif qtype == "text":
            agg.text_responses = [str(v) for v in answers]

        question_aggregations.append(agg)

    return SurveyAggregationResponse(
        survey_id=survey.id,
        total_responses=len(all_responses),
        questions=question_aggregations,
    )
