from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.scenario import Scenario
from app.models.site import Site
from app.schemas.scenario import (
    MetricDelta,
    ScenarioComparisonRequest,
    ScenarioComparisonResponse,
    ScenarioRequest,
    ScenarioResponse,
)
from app.services.scenarios import compute_deltas, simulate_scenario

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scenarios")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_tenant_site(
    db: AsyncSession, site_id: uuid.UUID, tenant_id: uuid.UUID
) -> Site:
    """Load a site and verify it belongs to the given tenant."""
    stmt = select(Site).where(Site.id == site_id, Site.tenant_id == tenant_id)
    result = await db.execute(stmt)
    site = result.scalar_one_or_none()
    if site is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )
    return site


# ---------------------------------------------------------------------------
# POST /scenarios/simulate — run scenario simulation
# ---------------------------------------------------------------------------


@router.post(
    "/simulate",
    response_model=ScenarioResponse,
    status_code=status.HTTP_201_CREATED,
)
async def simulate(
    body: ScenarioRequest,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> ScenarioResponse:
    """Run a scenario simulation with demand multipliers."""
    await _get_tenant_site(db, body.site_id, current_user.tenant_id)

    scenario = await simulate_scenario(
        db=db,
        tenant_id=current_user.tenant_id,
        site_id=body.site_id,
        condition_type=body.condition_type,
        demand_multiplier=body.demand_multiplier,
        custom_params=body.custom_params,
        name=body.name,
    )
    return ScenarioResponse.model_validate(scenario)


# ---------------------------------------------------------------------------
# GET /scenarios — list saved scenarios
# ---------------------------------------------------------------------------


@router.get("", response_model=list[ScenarioResponse])
async def list_scenarios(
    site_id: uuid.UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> list[ScenarioResponse]:
    """List saved scenarios, optionally filtered by site."""
    stmt = select(Scenario).where(Scenario.tenant_id == current_user.tenant_id)

    if site_id is not None:
        stmt = stmt.where(Scenario.site_id == site_id)

    stmt = (
        stmt.order_by(Scenario.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    scenarios = list(result.scalars().all())
    return [ScenarioResponse.model_validate(s) for s in scenarios]


# ---------------------------------------------------------------------------
# GET /scenarios/{scenario_id} — get single scenario
# ---------------------------------------------------------------------------


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(
    scenario_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> ScenarioResponse:
    """Get a single scenario by ID."""
    scenario = await _get_tenant_scenario(
        db, scenario_id, current_user.tenant_id
    )
    return ScenarioResponse.model_validate(scenario)


# ---------------------------------------------------------------------------
# DELETE /scenarios/{scenario_id} — delete scenario
# ---------------------------------------------------------------------------


@router.delete("/{scenario_id}")
async def delete_scenario(
    scenario_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Delete a scenario."""
    scenario = await _get_tenant_scenario(
        db, scenario_id, current_user.tenant_id
    )
    await db.delete(scenario)
    return {"detail": "Scenario deleted"}


# ---------------------------------------------------------------------------
# POST /scenarios/compare — compare 2-3 scenarios
# ---------------------------------------------------------------------------


@router.post("/compare", response_model=ScenarioComparisonResponse)
async def compare_scenarios(
    body: ScenarioComparisonRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> ScenarioComparisonResponse:
    """Compare 2-3 scenarios side-by-side with delta metrics."""
    scenarios: list[Scenario] = []
    for sid in body.scenario_ids:
        s = await _get_tenant_scenario(db, sid, current_user.tenant_id)
        scenarios.append(s)

    raw_deltas = compute_deltas(scenarios)
    deltas = [MetricDelta(**d) for d in raw_deltas]
    scenario_responses = [ScenarioResponse.model_validate(s) for s in scenarios]

    return ScenarioComparisonResponse(
        scenarios=scenario_responses,
        deltas=deltas,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _get_tenant_scenario(
    db: AsyncSession, scenario_id: uuid.UUID, tenant_id: uuid.UUID
) -> Scenario:
    """Load a scenario and verify it belongs to the given tenant."""
    stmt = select(Scenario).where(
        Scenario.id == scenario_id,
        Scenario.tenant_id == tenant_id,
    )
    result = await db.execute(stmt)
    scenario = result.scalar_one_or_none()
    if scenario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found",
        )
    return scenario
