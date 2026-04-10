from __future__ import annotations
import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.transition_plan import TransitionPlan, TransitionPhase
from app.schemas.transition_plan import (
    MilestoneResult, PhaseResult, TransitionPlanGenerateRequest,
    TransitionPlanGenerateResponse, TransitionPlanResponse,
    TransitionPhaseResponse,
)
from app.services.sotreg.transition_planner import generate_transition_plan

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sotreg/roadmap")


@router.post("/plan", response_model=TransitionPlanGenerateResponse)
async def create_plan(
    body: TransitionPlanGenerateRequest,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> TransitionPlanGenerateResponse:
    """Generate a new electrification transition plan."""
    result = generate_transition_plan(
        fleet_size=body.fleet_size, total_budget_mad=body.total_budget_mad,
        start_year=body.start_year, scenario_type=body.scenario_type,
        vehicle_unit_cost_mad=body.vehicle_unit_cost_mad,
        irve_cost_per_vehicle_mad=body.irve_cost_per_vehicle_mad,
        currency=body.currency,
    )
    plan = TransitionPlan(
        tenant_id=current_user.tenant_id, name=result["plan_name"],
        total_budget_mad=body.total_budget_mad, total_phases=result["total_phases"],
        fleet_size=body.fleet_size, scenario_type=body.scenario_type,
    )
    db.add(plan)
    await db.flush()
    await db.refresh(plan)

    for phase_data in result["phases"]:
        phase = TransitionPhase(
            tenant_id=current_user.tenant_id, plan_id=plan.id,
            name=phase_data["name"], technology_wave=phase_data["technology_wave"],
            start_year=phase_data["start_year"], end_year=phase_data["end_year"],
            vehicles_to_convert=phase_data["vehicles_to_convert"],
            target_pct_electric=phase_data["target_pct_electric"],
            budget_allocated_mad=phase_data["budget_allocated_mad"],
            vehicle_cost_mad=phase_data["vehicle_cost_mad"],
            infrastructure_cost_mad=phase_data["infrastructure_cost_mad"],
            status=phase_data["status"],
        )
        db.add(phase)
    await db.flush()

    logger.info("Transition plan %s created by user %s", plan.id, current_user.id)
    return TransitionPlanGenerateResponse(
        plan_name=result["plan_name"], scenario_type=result["scenario_type"],
        fleet_size=result["fleet_size"], total_budget_mad=result["total_budget_mad"],
        phases=[PhaseResult(**p) for p in result["phases"]],
        total_phases=result["total_phases"],
        total_vehicles_converted=result["total_vehicles_converted"],
        total_cost_mad=result["total_cost_mad"],
        budget_surplus_or_deficit_mad=result["budget_surplus_or_deficit_mad"],
        milestones=[MilestoneResult(**m) for m in result["milestones"]],
        currency=result.get("currency", "MAD"),
    )


@router.get("/plans", response_model=list[TransitionPlanResponse])
async def list_plans(
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> list[TransitionPlan]:
    stmt = select(TransitionPlan).where(
        TransitionPlan.tenant_id == current_user.tenant_id
    ).order_by(TransitionPlan.created_at.desc())
    return list((await db.execute(stmt)).scalars().all())


@router.get("/plan/{plan_id}", response_model=TransitionPlanResponse)
async def get_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> TransitionPlan:
    stmt = select(TransitionPlan).where(
        TransitionPlan.id == plan_id, TransitionPlan.tenant_id == current_user.tenant_id,
    )
    plan = (await db.execute(stmt)).scalar_one_or_none()
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return plan


@router.get("/plan/{plan_id}/phases", response_model=list[TransitionPhaseResponse])
async def get_plan_phases(
    plan_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> list[TransitionPhase]:
    stmt = select(TransitionPhase).where(
        TransitionPhase.plan_id == plan_id, TransitionPhase.tenant_id == current_user.tenant_id,
    ).order_by(TransitionPhase.start_year.asc())
    return list((await db.execute(stmt)).scalars().all())


@router.delete("/plan/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> None:
    stmt = select(TransitionPlan).where(
        TransitionPlan.id == plan_id, TransitionPlan.tenant_id == current_user.tenant_id,
    )
    plan = (await db.execute(stmt)).scalar_one_or_none()
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    # Delete phases first
    phase_stmt = select(TransitionPhase).where(TransitionPhase.plan_id == plan_id)
    phases = list((await db.execute(phase_stmt)).scalars().all())
    for p in phases:
        await db.delete(p)
    await db.delete(plan)
    await db.flush()
    logger.info("Plan %s deleted by user %s", plan_id, current_user.id)
