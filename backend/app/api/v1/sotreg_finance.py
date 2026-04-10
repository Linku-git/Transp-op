from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from app.middleware.rbac import require_role
from app.models.auth import User
from app.schemas.finance_advanced import (
    CO2SavingsNPVRequest,
    CO2SavingsNPVResponse,
    CO2ValorizationRequest,
    CO2ValorizationResponse,
    EfficientFrontierRequest,
    EfficientFrontierResponse,
    IRRRequest,
    IRRResponse,
    LinkFlow,
    PortfolioOptimizeRequest,
    PortfolioOptimizeResponse,
    PortfolioResult,
    SupernetworkRequest,
    SupernetworkResponse,
    InvestmentAnalysisRequest,
    InvestmentAnalysisResponse,
    NPVRequest,
    NPVResponse,
    PaybackRequest,
    PaybackResponse,
    PresentValueEntry,
    YearlyCO2Saving,
)
from app.services.sotreg.co2_externalities import (
    compute_co2_savings_npv,
    compute_co2_valorization,
)
from app.services.sotreg.npv_calculator import (
    compute_full_investment_analysis,
    compute_irr,
    compute_npv,
    compute_payback_period,
)
from app.services.sotreg.portfolio_optimizer import (
    compute_efficient_frontier,
    compute_portfolio_optimization,
)
from app.services.sotreg.supernetwork_equilibrium import (
    compute_supernetwork_equilibrium,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sotreg/finance")


# ---------------------------------------------------------------------------
# POST /sotreg/finance/npv
# ---------------------------------------------------------------------------


@router.post("/npv", response_model=NPVResponse)
async def npv_endpoint(
    body: NPVRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
) -> NPVResponse:
    """Compute Net Present Value from cash flows."""
    result = compute_npv(
        cash_flows=body.cash_flows,
        discount_rate=body.discount_rate,
        currency=body.currency,
    )
    logger.info(
        "NPV computed: %.2f %s (rate=%.2f%%, viable=%s) by user %s",
        result["npv"],
        body.currency,
        body.discount_rate * 100,
        result["is_viable"],
        current_user.id,
    )
    return NPVResponse(
        npv=result["npv"],
        discount_rate=result["discount_rate"],
        cash_flow_count=result["cash_flow_count"],
        present_values=[PresentValueEntry(**pv) for pv in result["present_values"]],
        is_viable=result["is_viable"],
        currency=result["currency"],
    )


# ---------------------------------------------------------------------------
# POST /sotreg/finance/irr
# ---------------------------------------------------------------------------


@router.post("/irr", response_model=IRRResponse)
async def irr_endpoint(
    body: IRRRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
) -> IRRResponse:
    """Compute Internal Rate of Return."""
    result = compute_irr(body.cash_flows)
    logger.info(
        "IRR computed: %s (converged=%s) by user %s",
        result.get("irr_pct"),
        result["converged"],
        current_user.id,
    )
    return IRRResponse(**result)


# ---------------------------------------------------------------------------
# POST /sotreg/finance/payback
# ---------------------------------------------------------------------------


@router.post("/payback", response_model=PaybackResponse)
async def payback_endpoint(
    body: PaybackRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
) -> PaybackResponse:
    """Compute payback period."""
    result = compute_payback_period(body.cash_flows, currency=body.currency)
    return PaybackResponse(**result)


# ---------------------------------------------------------------------------
# POST /sotreg/finance/investment-analysis
# ---------------------------------------------------------------------------


@router.post("/investment-analysis", response_model=InvestmentAnalysisResponse)
async def investment_analysis_endpoint(
    body: InvestmentAnalysisRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
) -> InvestmentAnalysisResponse:
    """Full investment analysis: NPV + IRR + payback."""
    result = compute_full_investment_analysis(
        cash_flows=body.cash_flows,
        discount_rate=body.discount_rate,
        currency=body.currency,
    )
    logger.info(
        "Investment analysis completed for user %s",
        current_user.id,
    )
    return InvestmentAnalysisResponse(**result)


# ---------------------------------------------------------------------------
# POST /sotreg/finance/co2-valorization
# ---------------------------------------------------------------------------


@router.post("/co2-valorization", response_model=CO2ValorizationResponse)
async def co2_valorization_endpoint(
    body: CO2ValorizationRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
) -> CO2ValorizationResponse:
    """Monetize avoided CO2 emissions from fleet transition."""
    result = compute_co2_valorization(
        fleet_annual_km=body.fleet_annual_km,
        current_motorization=body.current_motorization,
        target_motorization=body.target_motorization,
        carbon_price_mad_tco2=body.carbon_price_mad_tco2,
        vehicle_count=body.vehicle_count,
        energy_consumption_kwh_per_km=body.energy_consumption_kwh_per_km,
        currency=body.currency,
    )
    logger.info(
        "CO2 valorization: %.2f tCO2 avoided, %.2f MAD by user %s",
        result["avoided_emissions_tco2"],
        result["valorization_mad"],
        current_user.id,
    )
    return CO2ValorizationResponse(**result)


# ---------------------------------------------------------------------------
# POST /sotreg/finance/co2-savings-npv
# ---------------------------------------------------------------------------


@router.post("/co2-savings-npv", response_model=CO2SavingsNPVResponse)
async def co2_savings_npv_endpoint(
    body: CO2SavingsNPVRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
) -> CO2SavingsNPVResponse:
    """NPV of CO2 savings over a horizon."""
    result = compute_co2_savings_npv(
        fleet_annual_km=body.fleet_annual_km,
        current_motorization=body.current_motorization,
        target_motorization=body.target_motorization,
        carbon_price_mad_tco2=body.carbon_price_mad_tco2,
        carbon_price_escalation_pct=body.carbon_price_escalation_pct,
        discount_rate=body.discount_rate,
        horizon_years=body.horizon_years,
        vehicle_count=body.vehicle_count,
        energy_consumption_kwh_per_km=body.energy_consumption_kwh_per_km,
        currency=body.currency,
    )
    logger.info(
        "CO2 savings NPV: %.2f MAD over %d years by user %s",
        result["npv_co2_savings_mad"],
        body.horizon_years,
        current_user.id,
    )
    return CO2SavingsNPVResponse(
        npv_co2_savings_mad=result["npv_co2_savings_mad"],
        yearly_savings=[YearlyCO2Saving(**y) for y in result["yearly_savings"]],
        total_avoided_tco2=result["total_avoided_tco2"],
        horizon_years=result["horizon_years"],
        discount_rate=result["discount_rate"],
        currency=result["currency"],
    )


# ---------------------------------------------------------------------------
# POST /sotreg/finance/portfolio-optimize (Session 107)
# ---------------------------------------------------------------------------


@router.post("/portfolio-optimize", response_model=PortfolioOptimizeResponse)
async def portfolio_optimize_endpoint(
    body: PortfolioOptimizeRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
) -> PortfolioOptimizeResponse:
    """Run Markowitz mean-variance portfolio optimization."""
    result = compute_portfolio_optimization(
        expected_returns=body.expected_returns,
        covariance_matrix=body.covariance_matrix,
        risk_aversion=body.risk_aversion,
        technology_names=body.technology_names,
    )
    logger.info(
        "Portfolio optimization: E[r]=%.4f, std=%.4f, sharpe=%.4f by user %s",
        result["expected_return"],
        result["portfolio_std"],
        result["sharpe_ratio"],
        current_user.id,
    )
    return PortfolioOptimizeResponse(**result)


# ---------------------------------------------------------------------------
# POST /sotreg/finance/efficient-frontier (Session 107)
# ---------------------------------------------------------------------------


@router.post("/efficient-frontier", response_model=EfficientFrontierResponse)
async def efficient_frontier_endpoint(
    body: EfficientFrontierRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
) -> EfficientFrontierResponse:
    """Compute efficient frontier (Pareto-optimal portfolios)."""
    result = compute_efficient_frontier(
        expected_returns=body.expected_returns,
        covariance_matrix=body.covariance_matrix,
        n_points=body.n_points,
        technology_names=body.technology_names,
    )
    logger.info(
        "Efficient frontier: %d points computed by user %s",
        len(result["frontier"]),
        current_user.id,
    )
    return EfficientFrontierResponse(
        frontier=[PortfolioResult(**p) for p in result["frontier"]],
        min_risk_portfolio=PortfolioResult(**result["min_risk_portfolio"]),
        max_return_portfolio=PortfolioResult(**result["max_return_portfolio"]),
        technology_names=result["technology_names"],
    )


# ---------------------------------------------------------------------------
# POST /sotreg/finance/supernetwork-equilibrium (Session 107)
# ---------------------------------------------------------------------------


@router.post("/supernetwork-equilibrium", response_model=SupernetworkResponse)
async def supernetwork_equilibrium_endpoint(
    body: SupernetworkRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
) -> SupernetworkResponse:
    """Compute supernetwork equilibrium using Frank-Wolfe algorithm."""
    links_data = [
        {"from_node": l.from_node, "to_node": l.to_node, "free_flow_cost": l.free_flow_cost, "capacity": l.capacity}
        for l in body.links
    ]
    od_data = [
        {"origin": d.origin, "destination": d.destination, "demand": d.demand}
        for d in body.od_demands
    ]
    result = compute_supernetwork_equilibrium(
        links=links_data,
        od_demands=od_data,
        max_iterations=body.max_iterations,
        tolerance=body.tolerance,
    )
    logger.info(
        "Supernetwork equilibrium: cost=%.2f, iterations=%d, converged=%s by user %s",
        result["total_system_cost"],
        result["iterations"],
        result["converged"],
        current_user.id,
    )
    return SupernetworkResponse(
        link_flows=[LinkFlow(**f) for f in result["link_flows"]],
        total_system_cost=result["total_system_cost"],
        iterations=result["iterations"],
        converged=result["converged"],
        gap=result["gap"],
    )
