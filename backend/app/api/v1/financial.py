from __future__ import annotations

import logging
import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.financial import (
    FinancialScenario,
    ROICalculation,
    TCOEntry,
    VehicleReference,
)
from app.schemas.financial import (
    FinancialScenarioCreate,
    FinancialScenarioUpdate,
    FinancialScenarioResponse,
    TCOEntryCreate,
    TCOEntryResponse,
    TCOCalculateRequest,
    TCOCalculateResponse,
    ROICalculateRequest,
    ROICalculateResponse,
    InvestmentCompareRequest,
    InvestmentCompareResponse,
    SensitivityRequest,
    SensitivityResponse,
    CostAnalysisRequest,
    CostAnalysisResponse,
    VehicleReferenceResponse,
)
from app.services.cost_analysis import calculate_cost_analysis
from app.services.investment_comparator import compare_investment_models, sensitivity_analysis
from app.services.roi_calculator import calculate_roi
from app.services.tco_calculator import calculate_tco

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
# POST /financial/tco/calculate — compute TCO
# ---------------------------------------------------------------------------


@router.post("/tco/calculate", response_model=TCOCalculateResponse)
async def tco_calculate(
    body: TCOCalculateRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
) -> TCOCalculateResponse:
    """Calculate TCO for a fleet composition with optional evolution and comparison."""
    fleet_dicts = [item.model_dump(exclude_none=True) for item in body.fleet]

    result = calculate_tco(
        fleet=fleet_dicts,
        duration_years=body.duration_years,
        include_evolution=body.include_evolution,
        include_comparison=body.include_comparison,
    )

    logger.info(
        "TCO calculated for %d vehicle specs by user %s",
        len(body.fleet),
        current_user.id,
    )
    return TCOCalculateResponse(**result)


# ---------------------------------------------------------------------------
# POST /financial/roi/calculate — compute ROI
# ---------------------------------------------------------------------------


@router.post("/roi/calculate", response_model=ROICalculateResponse)
async def roi_calculate(
    body: ROICalculateRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> ROICalculateResponse:
    """Calculate ROI across 4 levers with optional DB persistence."""
    result = calculate_roi(
        headcount=body.headcount,
        daily_cost=body.daily_cost,
        baseline_absence_rate=body.baseline_absence_rate,
        target_absence_rate=body.target_absence_rate,
        replacement_cost=body.replacement_cost,
        turnover_rate_before=body.turnover_rate_before,
        turnover_rate_after=body.turnover_rate_after,
        annual_travel_hours=body.annual_travel_hours,
        engagement_rate=body.engagement_rate,
        training_hour_cost=body.training_hour_cost,
        total_investment=body.total_investment,
        current_fleet_annual_cost=body.current_fleet_annual_cost,
        optimized_fleet_annual_cost=body.optimized_fleet_annual_cost,
    )

    stored_id = None

    # Persist to DB if scenario_id is provided
    if body.scenario_id is not None:
        scenario = await _get_scenario_or_404(
            body.scenario_id, current_user.tenant_id, db
        )
        roi_record = ROICalculation(
            financial_scenario_id=scenario.id,
            baseline_absence_rate=body.baseline_absence_rate,
            target_absence_rate=body.target_absence_rate,
            headcount=body.headcount,
            daily_cost=body.daily_cost,
            replacement_cost=body.replacement_cost,
            turnover_rate_before=body.turnover_rate_before,
            turnover_rate_after=body.turnover_rate_after,
            training_hour_cost=body.training_hour_cost,
            engagement_rate=body.engagement_rate,
            annual_travel_hours=body.annual_travel_hours,
            roi_absenteeism=result["roi_absenteeism"],
            roi_retention=result["roi_retention"],
            roi_journey=result["roi_journey"],
            roi_fleet_optimization=result["roi_fleet_optimization"],
            roi_total=result["roi_total"],
            payback_months=result["payback_months"],
        )
        db.add(roi_record)
        await db.flush()
        await db.refresh(roi_record)
        stored_id = roi_record.id
        logger.info(
            "ROI calculation %s stored for scenario %s by user %s",
            roi_record.id,
            body.scenario_id,
            current_user.id,
        )

    logger.info("ROI calculated for %d headcount by user %s", body.headcount, current_user.id)
    return ROICalculateResponse(**result, stored_id=stored_id)


# ---------------------------------------------------------------------------
# POST /financial/compare — investment model comparison
# ---------------------------------------------------------------------------


@router.post("/compare", response_model=InvestmentCompareResponse)
async def investment_compare(
    body: InvestmentCompareRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
) -> InvestmentCompareResponse:
    """Compare CAPEX, Mise a Disposition, and OPEX investment models side by side."""
    result = compare_investment_models(
        vehicle_count=body.vehicle_count,
        headcount=body.headcount,
        annual_trips=body.annual_trips,
        duration_years=body.duration_years,
        capex_purchase_price=body.capex_purchase_price,
        capex_annual_maintenance=body.capex_annual_maintenance,
        capex_annual_fuel=body.capex_annual_fuel,
        capex_annual_insurance=body.capex_annual_insurance,
        capex_annual_driver_cost=body.capex_annual_driver_cost,
        capex_residual_value=body.capex_residual_value,
        mad_monthly_rental=body.mad_monthly_rental,
        mad_annual_fuel=body.mad_annual_fuel,
        mad_management_overhead_rate=body.mad_management_overhead_rate,
        opex_cost_per_km=body.opex_cost_per_km,
        opex_annual_km=body.opex_annual_km,
    )

    logger.info(
        "Investment comparison for %d vehicles by user %s",
        body.vehicle_count,
        current_user.id,
    )
    return InvestmentCompareResponse(**result)


# ---------------------------------------------------------------------------
# POST /financial/compare/sensitivity — sensitivity analysis
# ---------------------------------------------------------------------------


@router.post("/compare/sensitivity", response_model=SensitivityResponse)
async def investment_sensitivity(
    body: SensitivityRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
) -> SensitivityResponse:
    """Run sensitivity analysis on investment model comparison."""
    baseline_params = body.baseline.model_dump()
    # Convert Decimal fields to float for the comparator
    for key, val in baseline_params.items():
        if isinstance(val, Decimal):
            baseline_params[key] = float(val)

    result = sensitivity_analysis(
        baseline_params=baseline_params,
        fuel_price_delta_pct=body.fuel_price_delta_pct,
        headcount_delta_pct=body.headcount_delta_pct,
        fill_rate_pct=body.fill_rate_pct,
    )

    logger.info(
        "Sensitivity analysis (fuel=%+.0f%%, hc=%+.0f%%, fill=%.0f%%) by user %s",
        body.fuel_price_delta_pct,
        body.headcount_delta_pct,
        body.fill_rate_pct,
        current_user.id,
    )
    return SensitivityResponse(**result)


# ---------------------------------------------------------------------------
# POST /financial/cost-analysis — cost per trip and breakeven
# ---------------------------------------------------------------------------


@router.post("/cost-analysis", response_model=CostAnalysisResponse)
async def cost_analysis(
    body: CostAnalysisRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
) -> CostAnalysisResponse:
    """Calculate cost per seat, per employee, and breakeven vs kilometric allowance."""
    result = calculate_cost_analysis(
        annual_route_cost=body.annual_route_cost,
        vehicle_capacity=body.vehicle_capacity,
        fill_rate=body.fill_rate,
        transported_employees=body.transported_employees,
        average_distance_km=body.average_distance_km,
        kilometric_allowance_per_km=body.kilometric_allowance_per_km,
        working_days=body.working_days,
        trips_per_day=body.trips_per_day,
        total_annual_cost=body.total_annual_cost,
    )

    logger.info(
        "Cost analysis for %d-seat vehicle by user %s",
        body.vehicle_capacity,
        current_user.id,
    )
    return CostAnalysisResponse(**result)


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
