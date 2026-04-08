from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SurveyQuestionOption(BaseModel):
    text: str
    value: str | None = None


class SurveyQuestion(BaseModel):
    id: str
    text: str
    question_type: str = Field(
        ..., pattern=r"^(single_choice|multiple_choice|text|rating|slider)$"
    )
    options: list[SurveyQuestionOption] | None = None
    required: bool = True
    min_value: int | None = None
    max_value: int | None = None


class SurveyCreate(BaseModel):
    content_id: uuid.UUID
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=2000)
    questions: list[SurveyQuestion] = Field(..., min_length=1)
    is_anonymous: bool = False


class SurveyUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    questions: list[SurveyQuestion] | None = None
    is_anonymous: bool | None = None
    is_active: bool | None = None


class SurveyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    content_id: uuid.UUID
    title: str
    description: str | None = None
    questions: list[dict]
    response_count: int = 0
    is_anonymous: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class SurveyListResponse(BaseModel):
    data: list[SurveyResponse]
    total: int
    page: int = 1
    pages: int = 1


class AnswerItem(BaseModel):
    question_id: str
    value: str | int | float | list[str] | None = None


class SurveySubmitRequest(BaseModel):
    employee_id: uuid.UUID | None = None
    responses: list[AnswerItem] = Field(..., min_length=1)


class SurveySubmitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    survey_id: uuid.UUID
    employee_id: uuid.UUID | None = None
    responses: list[dict]
    submitted_at: datetime


class QuestionAggregation(BaseModel):
    question_id: str
    question_text: str
    question_type: str
    total_responses: int = 0
    distribution: dict[str, int] | None = None
    average: float | None = None
    text_responses: list[str] | None = None


class SurveyAggregationResponse(BaseModel):
    survey_id: uuid.UUID
    total_responses: int = 0
    questions: list[QuestionAggregation] = []
