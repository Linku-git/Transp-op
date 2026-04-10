from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class MCDAAlternative(BaseModel):
    name: str
    capex: float = Field(..., ge=0)
    opex: float = Field(..., ge=0)
    co2: float = Field(..., ge=0)
    risk: float = Field(..., ge=0, le=10)
    comfort: float = Field(..., ge=0, le=10)
    maturity: float = Field(..., ge=0, le=10)

class MCDARequest(BaseModel):
    alternatives: list[MCDAAlternative] = Field(..., min_length=1)
    weights: dict[str, float] | None = None
    scenario_name: str = Field(default="Analyse MCDA")

class NormalizedAlternative(BaseModel):
    name: str
    score: float
    rank: int
    normalized_values: dict[str, float]

class MCDAResponse(BaseModel):
    ranked_alternatives: list[NormalizedAlternative]
    weights_used: dict[str, float]
    criteria_ranges: dict[str, dict[str, float]]
    best_alternative: str
    worst_alternative: str

class SensitivityRequest(BaseModel):
    alternatives: list[MCDAAlternative] = Field(..., min_length=2)
    weights: dict[str, float] | None = None
    delta_pct: float = Field(default=20.0, gt=0, le=50)

class SensitivityCriterionResult(BaseModel):
    criterion: str
    weight_original: float
    weight_plus: float
    weight_minus: float
    ranking_changed: bool
    is_critical: bool

class SensitivityResponse(BaseModel):
    base_ranking: list[str]
    sensitivity_results: list[SensitivityCriterionResult]
    critical_criteria: list[str]
    stability_score: float

class ModalChoiceAlternative(BaseModel):
    name: str
    cost: float = Field(..., ge=0)
    time_minutes: float = Field(..., ge=0)
    comfort: float = Field(default=5.0, ge=0, le=10)

class ModalChoiceRequest(BaseModel):
    alternatives: list[ModalChoiceAlternative] = Field(..., min_length=2)
    beta_cost: float = Field(default=-0.001)
    beta_time: float = Field(default=-0.05)
    beta_comfort: float = Field(default=0.5)

class ModalChoiceProbability(BaseModel):
    name: str
    utility: float
    probability: float

class ModalChoiceResponse(BaseModel):
    probabilities: list[ModalChoiceProbability]
    probabilities_sum: float
    dominant_mode: str

class MCDAScenarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    alternatives: dict | None
    weights: dict | None
    results: dict | None
    created_at: datetime
    updated_at: datetime
