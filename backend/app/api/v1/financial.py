from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.financial import FinancialScenario, TCOEntry, VehicleReference
from app.schemas.financial import (
    FinancialScenarioCreate,
    FinancialScenarioUpdate,
    FinancialScenarioResponse,
    TCOEntryCreate,
    TCOEntryResponse,
    VehicleReferenceResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/financial")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_scenario_or_404(
    scenario_id: uuid.UUID,
    tenant_id: uuid.UUID,
    db: AsyncSession,
) -> FinancialScenario:
    """Fetch a financial scenario by ID and tenant, raising 404 if missing."""
    stmt = select(FinancialScenario).where(
        FinancialScenario.id == scenario_id,
        FinancialScenario.tenant_id == tenant_id,
    )
    result = await db.execute(stmt)
    scenario = result.scalar_one_or_none()
    if scenario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial scenario not found",
        )
    return scenario


# ---------------------------------------------------------------------------
# POST /financial/scenarios — create financial scenario
# ---------------------------------------------------------------------------


@router.post(
    "/scenarios",
    response_model=FinancialScenarioResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_scenario(
    body: FinancialScenarioCreate,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> FinancialScenarioResponse:
    """Create a new financial scenario."""
    scenario = FinancialScenario(
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        **body.model_dump(),
    )
    db.add(scenario)
    await db.flush()
    await db.refresh(scenario)

    logger.info(
        "Financial scenario %s created by user %s", scenario.id, current_user.id
    )
    return FinancialScenarioResponse.model_validate(scenario)


# ---------------------------------------------------------------------------
# GET /financial/scenarios — list financial scenarios
# ---------------------------------------------------------------------------


@router.get("/scenarios", response_model=dict)
async def list_scenarios(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List financial scenarios for the current tenant with pagination."""
    conditions = [FinancialScenario.tenant_id == current_user.tenant_id]

    # Count
    count_stmt = (
        select(func.count()).select_from(FinancialScenario).where(*conditions)
    )
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    # Paginated data
    offset = (page - 1) * page_size
    data_stmt = (
        select(FinancialScenario)
        .where(*conditions)
        .order_by(FinancialScenario.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    data_result = await db.execute(data_stmt)
    scenarios = list(data_result.scalars().all())

    pages = max(1, (total + page_size - 1) // page_size)

    return {
        "data": [
            FinancialScenarioResponse.model_validate(s).model_dump(mode="json")
            for s in scenarios
        ],
        "total": total,
        "page": page,
        "pages": pages,
    }


# ---------------------------------------------------------------------------
# GET /financial/scenarios/{scenario_id} — get single scenario
# ---------------------------------------------------------------------------


@router.get("/scenarios/{scenario_id}", response_model=FinancialScenarioResponse)
async def get_scenario(
    scenario_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> FinancialScenarioResponse:
    """Retrieve a single financial scenario by ID."""
    scenario = await _get_scenario_or_404(
        scenario_id, current_user.tenant_id, db
    )
    return FinancialScenarioResponse.model_validate(scenario)


# ---------------------------------------------------------------------------
# PUT /financial/scenarios/{scenario_id} — update scenario
# ---------------------------------------------------------------------------


@router.put("/scenarios/{scenario_id}", response_model=FinancialScenarioResponse)
async def update_scenario(
    scenario_id: uuid.UUID,
    body: FinancialScenarioUpdate,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> FinancialScenarioResponse:
    """Update an existing financial scenario."""
    scenario = await _get_scenario_or_404(
        scenario_id, current_user.tenant_id, db
    )

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(scenario, field, value)

    await db.flush()
    await db.refresh(scenario)

    logger.info(
        "Financial scenario %s updated by user %s", scenario_id, current_user.id
    )
    return FinancialScenarioResponse.model_validate(scenario)


# ---------------------------------------------------------------------------
# DELETE /financial/scenarios/{scenario_id} — delete scenario
# ---------------------------------------------------------------------------


@router.delete(
    "/scenarios/{scenario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def delete_scenario(
    scenario_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a financial scenario (cascades to TCO entries and ROI calculations)."""
    scenario = await _get_scenario_or_404(
        scenario_id, current_user.tenant_id, db
    )

    await db.delete(scenario)
    await db.flush()

    logger.info(
        "Financial scenario %s deleted by user %s", scenario_id, current_user.id
    )


# ---------------------------------------------------------------------------
# POST /financial/scenarios/{scenario_id}/tco-entries — create TCO entry
# ---------------------------------------------------------------------------


@router.post(
    "/scenarios/{scenario_id}/tco-entries",
    response_model=TCOEntryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tco_entry(
    scenario_id: uuid.UUID,
    body: TCOEntryCreate,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> TCOEntryResponse:
    """Create a TCO entry for a financial scenario."""
    # Validate scenario exists and belongs to tenant
    await _get_scenario_or_404(scenario_id, current_user.tenant_id, db)

    tco_entry = TCOEntry(
        financial_scenario_id=scenario_id,
        **body.model_dump(),
    )
    db.add(tco_entry)
    await db.flush()
    await db.refresh(tco_entry)

    logger.info(
        "TCO entry %s created for scenario %s by user %s",
        tco_entry.id,
        scenario_id,
        current_user.id,
    )
    return TCOEntryResponse.model_validate(tco_entry)


# ---------------------------------------------------------------------------
# GET /financial/scenarios/{scenario_id}/tco-entries — list TCO entries
# ---------------------------------------------------------------------------


@router.get(
    "/scenarios/{scenario_id}/tco-entries",
    response_model=list[TCOEntryResponse],
)
async def list_tco_entries(
    scenario_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> list[TCOEntryResponse]:
    """List all TCO entries for a financial scenario."""
    # Validate scenario exists and belongs to tenant
    await _get_scenario_or_404(scenario_id, current_user.tenant_id, db)

    stmt = (
        select(TCOEntry)
        .where(TCOEntry.financial_scenario_id == scenario_id)
        .order_by(TCOEntry.created_at.asc())
    )
    result = await db.execute(stmt)
    entries = list(result.scalars().all())

    return [TCOEntryResponse.model_validate(e) for e in entries]


# ---------------------------------------------------------------------------
# GET /financial/vehicles — vehicle reference catalog
# ---------------------------------------------------------------------------


@router.get("/vehicles", response_model=list[VehicleReferenceResponse])
async def list_vehicle_references(
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> list[VehicleReferenceResponse]:
    """Return the global vehicle reference catalog (no tenant filter)."""
    stmt = select(VehicleReference).order_by(VehicleReference.type.asc())
    result = await db.execute(stmt)
    refs = list(result.scalars().all())

    return [VehicleReferenceResponse.model_validate(r) for r in refs]
