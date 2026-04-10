from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from app.middleware.rbac import require_role
from app.models.auth import User
from app.schemas.technology import (
    BreakevenRequest,
    BreakevenResponse,
    RangeCorrectionRequest,
    RangeCorrectionResponse,
    TCO15YearRequest,
    TCO15YearResponse,
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
    current_user: User = Depends(require_role("admin", "drh", "daf")),
) -> RangeCorrectionResponse:
    """Compute corrected vehicle range with slope, season, and speed factors."""
    result = compute_corrected_range(
        nominal_range_km=body.nominal_range_km,
        pente_profile=body.pente_profile,
        saison_profile=body.saison_profile,
        vitesse_profile=body.vitesse_profile,
    )
    logger.info(
        "Range correction computed: %.1f km → %.1f km (factor=%.3f) by user %s",
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
    current_user: User = Depends(require_role("admin", "drh", "daf")),
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
    current_user: User = Depends(require_role("admin", "drh", "daf")),
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
