from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

SCENARIO_TYPES = ["aggressive", "moderate", "conservative"]
WAVE_TYPES = ["pilot", "scale", "full"]
STATUS_TYPES = ["planned", "in_progress", "completed"]

class TransitionPlanGenerateRequest(BaseModel):
    fleet_size: int = Field(..., ge=1)
    total_budget_mad: float = Field(..., gt=0)
    start_year: int = Field(default=2026, ge=2024)
    scenario_type: str = Field(default="moderate")
    vehicle_unit_cost_mad: float = Field(default=300000.0, gt=0)
    irve_cost_per_vehicle_mad: float = Field(default=90000.0, ge=0)
    currency: str = Field(default="MAD")

    @field_validator("scenario_type")
    @classmethod
    def validate_scenario(cls, v: str) -> str:
        if v not in SCENARIO_TYPES:
            raise ValueError(f"scenario_type must be one of {SCENARIO_TYPES}")
        return v

class PhaseResult(BaseModel):
    name: str
    technology_wave: str
    start_year: int
    end_year: int
    vehicles_to_convert: int
    target_pct_electric: float
    budget_allocated_mad: float
    vehicle_cost_mad: float
    infrastructure_cost_mad: float
    status: str

class MilestoneResult(BaseModel):
    year: int
    description: str
    target_pct: float
    vehicles_converted_cumulative: int

class TransitionPlanGenerateResponse(BaseModel):
    plan_name: str
    scenario_type: str
    fleet_size: int
    total_budget_mad: float
    phases: list[PhaseResult]
    total_phases: int
    total_vehicles_converted: int
    total_cost_mad: float
    budget_surplus_or_deficit_mad: float
    milestones: list[MilestoneResult]
    currency: str = "MAD"

class PlanProgressResponse(BaseModel):
    pct_complete: float
    current_phase: str | None
    phases_completed: int
    phases_remaining: int
    budget_spent_mad: float
    budget_remaining_mad: float
    on_track: bool

class TransitionPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    total_budget_mad: float
    total_phases: int
    fleet_size: int
    scenario_type: str
    currency: str
    created_at: datetime
    updated_at: datetime

class TransitionPhaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    plan_id: uuid.UUID
    name: str
    technology_wave: str
    start_year: int
    end_year: int
    vehicles_to_convert: int
    target_pct_electric: float
    budget_allocated_mad: float
    vehicle_cost_mad: float
    infrastructure_cost_mad: float
    status: str
    created_at: datetime
    updated_at: datetime
