from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SecurityScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    employee_id: uuid.UUID
    score: int
    risk_level: str
    contributing_factors: dict | None = None
    computed_at: datetime
    created_at: datetime


class SecurityScoreListResponse(BaseModel):
    data: list[SecurityScoreResponse]
    total: int


class SecurityScoreDetail(BaseModel):
    score: int
    risk_level: str
    contributing_factors: dict
    computed_at: datetime
    employee_id: uuid.UUID
    questionnaire_rating: int | None = None
    vulnerable_stop_count: int = 0
    night_commute_exposure: float = 0.0
    avg_stop_isolation: float = 0.0


class GroupAggregation(BaseModel):
    group_key: str
    group_value: str
    avg_score: float
    employee_count: int
    risk_distribution: dict[str, int]


class TimeSlotHeatmap(BaseModel):
    time_slot: str
    risk_score: float
    employee_count: int
    is_night: bool
