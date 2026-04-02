from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Canonical condition types (English)
SCENARIO_CONDITION_TYPES = [
    "normal",
    "rain",
    "strike",
    "peak",
    "night",
    "transit_failure",
]

# French alias mapping
CONDITION_ALIAS_MAP: dict[str, str] = {
    "pluie": "rain",
    "greve_transport": "strike",
    "pic_activite": "peak",
    "nuit": "night",
    "defaillance_tc": "transit_failure",
}


def _resolve_condition(v: str) -> str:
    """Normalize French aliases to English canonical names."""
    v = v.strip().lower()
    return CONDITION_ALIAS_MAP.get(v, v)


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class ScenarioRequest(BaseModel):
    """Request to run a scenario simulation."""

    site_id: uuid.UUID
    condition_type: str = Field(max_length=30)
    demand_multiplier: float | None = Field(default=None, ge=0.1, le=5.0)
    custom_params: dict | None = None
    name: str | None = Field(default=None, max_length=100)

    @field_validator("condition_type")
    @classmethod
    def validate_condition(cls, v: str) -> str:
        resolved = _resolve_condition(v)
        if resolved not in SCENARIO_CONDITION_TYPES:
            raise ValueError(
                f"condition_type must be one of {SCENARIO_CONDITION_TYPES} "
                f"(French aliases also accepted: {list(CONDITION_ALIAS_MAP.keys())})"
            )
        return resolved


class ScenarioComparisonRequest(BaseModel):
    """Request to compare 2-3 scenarios side-by-side."""

    scenario_ids: list[uuid.UUID] = Field(min_length=2, max_length=3)


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class ScenarioResponse(BaseModel):
    """A single scenario simulation result."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    site_id: uuid.UUID
    baseline_optimization_id: uuid.UUID | None
    condition_type: str
    demand_multiplier: float
    custom_params: dict
    estimated_metrics: dict
    name: str | None
    created_at: datetime


class MetricDelta(BaseModel):
    """Pairwise metric delta between two scenarios."""

    scenario_a_id: uuid.UUID
    scenario_b_id: uuid.UUID
    vehicles_delta: int
    cost_delta_mad: float
    co2_delta_kg: float
    distance_delta_km: float
    duration_delta_minutes: float
    occupancy_delta_pct: float


class ScenarioComparisonResponse(BaseModel):
    """Side-by-side comparison of 2-3 scenarios."""

    scenarios: list[ScenarioResponse]
    deltas: list[MetricDelta]
