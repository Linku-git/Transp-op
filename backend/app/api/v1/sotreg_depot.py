from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.depot_plan import DepotPlan
from app.schemas.depot_plan import (
    DepotCostEstimateRequest,
    DepotCostEstimateResponse,
    DepotLayoutRequest,
    DepotLayoutResponse,
    DepotPlanCreate,
    DepotPlanResponse,
    ChargerPosition,
)
from app.services.sotreg.depot_layout import compute_depot_layout
from app.services.sotreg.irve_cost_calculator import compute_depot_electrification_cost

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sotreg/depot")


# ---------------------------------------------------------------------------
# POST /sotreg/depot/cost-estimate
# ---------------------------------------------------------------------------


@router.post("/cost-estimate", response_model=DepotCostEstimateResponse)
async def cost_estimate(
    body: DepotCostEstimateRequest,
    current_user: User = Depends(require_role("admin", "drh", "responsable_parc")),
) -> DepotCostEstimateResponse:
    """Compute depot electrification cost with 7-component breakdown."""
    result = compute_depot_electrification_cost(
        charger_count=body.charger_count,
        charger_type=body.charger_type,
        contingency_pct=body.contingency_pct,
        currency=body.currency,
    )
    logger.info(
        "Depot cost estimate: %d x %s, total %.0f MAD by user %s",
        body.charger_count,
        body.charger_type,
        result["total_cost_mad"],
        current_user.id,
    )
    return DepotCostEstimateResponse(**result)


# ---------------------------------------------------------------------------
# POST /sotreg/depot/layout-plan
# ---------------------------------------------------------------------------


@router.post("/layout-plan", response_model=DepotLayoutResponse)
async def layout_plan(
    body: DepotLayoutRequest,
    current_user: User = Depends(require_role("admin", "drh", "responsable_parc")),
) -> DepotLayoutResponse:
    """Plan depot layout for N chargers and M vehicles."""
    result = compute_depot_layout(
        charger_count=body.charger_count,
        fleet_size=body.fleet_size,
        charger_type=body.charger_type,
        include_maintenance=body.include_maintenance,
        currency=body.currency,
    )
    logger.info(
        "Depot layout: %.0f m2 total, %d chargers, %d bays by user %s",
        result["total_area_m2"],
        body.charger_count,
        result["parking_bays"],
        current_user.id,
    )
    positions = [ChargerPosition(**p) for p in result["charger_positions"]]
    return DepotLayoutResponse(
        total_area_m2=result["total_area_m2"],
        charging_area_m2=result["charging_area_m2"],
        parking_area_m2=result["parking_area_m2"],
        maintenance_area_m2=result["maintenance_area_m2"],
        circulation_area_m2=result["circulation_area_m2"],
        charger_positions=positions,
        parking_bays=result["parking_bays"],
        charger_count=result["charger_count"],
        charger_type=result["charger_type"],
        dimensions=result["dimensions"],
        currency=result.get("currency", body.currency),
    )


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------


@router.post("/plans", response_model=DepotPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_depot_plan(
    body: DepotPlanCreate,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> DepotPlan:
    """Create a depot plan record."""
    plan = DepotPlan(
        tenant_id=current_user.tenant_id,
        site_id=body.site_id,
        name=body.name,
        total_area_m2=body.total_area_m2,
        charging_area_m2=body.charging_area_m2,
        parking_area_m2=body.parking_area_m2,
        maintenance_area_m2=body.maintenance_area_m2,
        charger_count=body.charger_count,
        charger_type=body.charger_type,
        parking_bays=body.parking_bays,
        fleet_size=body.fleet_size,
        total_cost_mad=body.total_cost_mad,
        cost_breakdown=body.cost_breakdown,
    )
    db.add(plan)
    await db.flush()
    await db.refresh(plan)
    logger.info("DepotPlan %s created by user %s", plan.id, current_user.id)
    return plan


@router.get("/plans", response_model=list[DepotPlanResponse])
async def list_depot_plans(
    current_user: User = Depends(require_role("admin", "drh", "responsable_parc")),
    db: AsyncSession = Depends(get_db),
) -> list[DepotPlan]:
    """List all depot plans for the tenant."""
    stmt = (
        select(DepotPlan)
        .where(DepotPlan.tenant_id == current_user.tenant_id)
        .order_by(DepotPlan.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/plans/{plan_id}", response_model=DepotPlanResponse)
async def get_depot_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "responsable_parc")),
    db: AsyncSession = Depends(get_db),
) -> DepotPlan:
    """Get a single depot plan."""
    stmt = select(DepotPlan).where(
        DepotPlan.id == plan_id,
        DepotPlan.tenant_id == current_user.tenant_id,
    )
    plan = (await db.execute(stmt)).scalar_one_or_none()
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depot plan not found")
    return plan


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_depot_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a depot plan."""
    stmt = select(DepotPlan).where(
        DepotPlan.id == plan_id,
        DepotPlan.tenant_id == current_user.tenant_id,
    )
    plan = (await db.execute(stmt)).scalar_one_or_none()
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Depot plan not found")
    await db.delete(plan)
    await db.flush()
    logger.info("DepotPlan %s deleted by user %s", plan_id, current_user.id)
