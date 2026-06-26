from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.irve_infrastructure import IRVEInfrastructure
from app.schemas.irve import (
    ChargingOptimizationRequest,
    ChargingOptimizationResponse,
    IRVEInfrastructureCreate,
    IRVEInfrastructureResponse,
    IRVESizingRequest,
    IRVESizingResponse,
)
from app.schemas.technology import (
    BreakevenRequest,
    BreakevenResponse,
    RangeCorrectionRequest,
    RangeCorrectionResponse,
    TCO15YearRequest,
    TCO15YearResponse,
)
from app.services.sotreg.charging_optimizer import (
    compute_charging_schedule,
    compute_irve_sizing,
)
from app.services.sotreg.range_correction import (
    compute_corrected_range,
    compute_electrification_breakeven,
    compute_tco_15year,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sotreg/technologies")


# ---------------------------------------------------------------------------
# POST /sotreg/technologies/range-correction
# ---------------------------------------------------------------------------


@router.post("/range-correction", response_model=RangeCorrectionResponse)
async def range_correction(
    body: RangeCorrectionRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf", "responsable_parc")),
) -> RangeCorrectionResponse:
    """Compute corrected vehicle range with slope, season, and speed factors."""
    result = compute_corrected_range(
        nominal_range_km=body.nominal_range_km,
        pente_profile=body.pente_profile,
        saison_profile=body.saison_profile,
        vitesse_profile=body.vitesse_profile,
    )
    logger.info(
        "Range correction computed: %.1f km -> %.1f km (factor=%.3f) by user %s",
        body.nominal_range_km,
        result["corrected_range_km"],
        result["correction_factor"],
        current_user.id,
    )
    return RangeCorrectionResponse(**result)


# ---------------------------------------------------------------------------
# POST /sotreg/technologies/tco-15year
# ---------------------------------------------------------------------------


@router.post("/tco-15year", response_model=TCO15YearResponse)
async def tco_15year(
    body: TCO15YearRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf", "responsable_parc")),
) -> TCO15YearResponse:
    """Compute 15-year TCO with financing, depreciation, and energy escalation."""
    result = compute_tco_15year(
        purchase_price=body.purchase_price,
        annual_maintenance_cost=body.annual_maintenance_cost,
        energy_cost_per_km=body.energy_cost_per_km,
        annual_km=body.annual_km,
        residual_value_pct=body.residual_value_pct,
        duration_years=body.duration_years,
        loan_rate_pct=body.loan_rate_pct,
        loan_duration_years=body.loan_duration_years,
        energy_escalation_pct=body.energy_escalation_pct,
        maintenance_escalation_pct=body.maintenance_escalation_pct,
        currency=body.currency,
    )
    logger.info(
        "TCO 15-year computed: %.2f %s over %d years by user %s",
        result["total_tco"],
        body.currency,
        body.duration_years,
        current_user.id,
    )
    return TCO15YearResponse(**result)


# ---------------------------------------------------------------------------
# POST /sotreg/technologies/breakeven
# ---------------------------------------------------------------------------


@router.post("/breakeven", response_model=BreakevenResponse)
async def breakeven(
    body: BreakevenRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf", "responsable_parc")),
) -> BreakevenResponse:
    """Compute electrification breakeven km/year threshold."""
    result = compute_electrification_breakeven(
        capex_diesel=body.capex_diesel,
        capex_electric=body.capex_electric,
        opex_per_km_diesel=body.opex_per_km_diesel,
        opex_per_km_electric=body.opex_per_km_electric,
        currency=body.currency,
    )
    km_val = result["km_seuil"] if result["km_seuil"] is not None else 0.0
    logger.info(
        "Breakeven computed: %.0f km/year (viable=%s) by user %s",
        km_val,
        result["is_electric_viable"],
        current_user.id,
    )
    return BreakevenResponse(**result)


# ---------------------------------------------------------------------------
# POST /sotreg/technologies/charging-optimization
# ---------------------------------------------------------------------------


@router.post("/charging-optimization", response_model=ChargingOptimizationResponse)
async def charging_optimization(
    body: ChargingOptimizationRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf", "responsable_parc")),
) -> ChargingOptimizationResponse:
    """Compute optimal charging schedule with Qin 2016 SOC=62% target."""
    result = compute_charging_schedule(
        battery_capacity_kwh=body.battery_capacity_kwh,
        current_soc_pct=body.current_soc_pct,
        target_soc_pct=body.target_soc_pct,
        charger_power_kw=body.charger_power_kw,
        departure_hour=body.departure_hour,
        arrival_hour=body.arrival_hour,
        currency=body.currency,
    )
    logger.info(
        "Charging optimization: SOC %.0f%% -> %.0f%%, %.1f kWh, cost %.2f MAD by user %s",
        body.current_soc_pct,
        body.target_soc_pct,
        result["energy_needed_kwh"],
        result["total_energy_cost_mad"],
        current_user.id,
    )
    return ChargingOptimizationResponse(**result)


# ---------------------------------------------------------------------------
# POST /sotreg/technologies/irve-sizing
# ---------------------------------------------------------------------------


@router.post("/irve-sizing", response_model=IRVESizingResponse)
async def irve_sizing(
    body: IRVESizingRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf", "responsable_parc")),
) -> IRVESizingResponse:
    """Compute IRVE infrastructure sizing for a given fleet."""
    result = compute_irve_sizing(
        fleet_size=body.fleet_size,
        daily_km_per_vehicle=body.daily_km_per_vehicle,
        battery_capacity_kwh=body.battery_capacity_kwh,
        energy_consumption_kwh_per_km=body.energy_consumption_kwh_per_km,
        charging_window_hours=body.charging_window_hours,
        charger_utilization_target=body.charger_utilization_target,
        preferred_charger_type=body.preferred_charger_type,
        currency=body.currency,
    )
    logger.info(
        "IRVE sizing: %d chargers (%s), %.0f kW total, CAPEX %.0f MAD by user %s",
        result["charger_count"],
        result["charger_type"],
        result["total_installed_power_kw"],
        result["total_capex_mad"],
        current_user.id,
    )
    return IRVESizingResponse(**result)


# ---------------------------------------------------------------------------
# IRVE Infrastructure CRUD
# ---------------------------------------------------------------------------


@router.post(
    "/irve",
    response_model=IRVEInfrastructureResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_irve(
    body: IRVEInfrastructureCreate,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> IRVEInfrastructure:
    """Create a new IRVE infrastructure record."""
    irve = IRVEInfrastructure(
        tenant_id=current_user.tenant_id,
        site_id=body.site_id,
        charger_type=body.charger_type,
        charger_count=body.charger_count,
        power_per_charger_kw=body.power_per_charger_kw,
        total_installed_power_kw=body.total_installed_power_kw,
        hardware_cost_mad=body.hardware_cost_mad,
        installation_cost_mad=body.installation_cost_mad,
        transformer_cost_mad=body.transformer_cost_mad,
        grid_connection_cost_mad=body.grid_connection_cost_mad,
        total_capex_mad=body.total_capex_mad,
        annual_electricity_cost_mad=body.annual_electricity_cost_mad,
        fleet_size=body.fleet_size,
        daily_km_per_vehicle=body.daily_km_per_vehicle,
        battery_capacity_kwh=body.battery_capacity_kwh,
    )
    db.add(irve)
    await db.flush()
    await db.refresh(irve)
    logger.info("IRVE %s created by user %s", irve.id, current_user.id)
    return irve


@router.get("/irve", response_model=list[IRVEInfrastructureResponse])
async def list_irve(
    current_user: User = Depends(require_role("admin", "drh", "daf", "responsable_parc")),
    db: AsyncSession = Depends(get_db),
) -> list[IRVEInfrastructure]:
    """List all IRVE infrastructure records for the tenant."""
    stmt = (
        select(IRVEInfrastructure)
        .where(IRVEInfrastructure.tenant_id == current_user.tenant_id)
        .order_by(IRVEInfrastructure.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/irve/{irve_id}", response_model=IRVEInfrastructureResponse)
async def get_irve(
    irve_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "daf", "responsable_parc")),
    db: AsyncSession = Depends(get_db),
) -> IRVEInfrastructure:
    """Get a single IRVE infrastructure record."""
    stmt = select(IRVEInfrastructure).where(
        IRVEInfrastructure.id == irve_id,
        IRVEInfrastructure.tenant_id == current_user.tenant_id,
    )
    irve = (await db.execute(stmt)).scalar_one_or_none()
    if irve is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IRVE infrastructure not found",
        )
    return irve


@router.delete("/irve/{irve_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_irve(
    irve_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an IRVE infrastructure record."""
    stmt = select(IRVEInfrastructure).where(
        IRVEInfrastructure.id == irve_id,
        IRVEInfrastructure.tenant_id == current_user.tenant_id,
    )
    irve = (await db.execute(stmt)).scalar_one_or_none()
    if irve is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IRVE infrastructure not found",
        )
    await db.delete(irve)
    await db.flush()
    logger.info("IRVE %s deleted by user %s", irve_id, current_user.id)
