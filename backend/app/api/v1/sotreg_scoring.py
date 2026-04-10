from __future__ import annotations
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.mcda_scenario import MCDAScenario
from app.schemas.mcda_scenario import (
    MCDARequest, MCDAResponse, NormalizedAlternative,
    SensitivityRequest, SensitivityResponse, SensitivityCriterionResult,
    ModalChoiceRequest, ModalChoiceResponse, ModalChoiceProbability,
)
from app.services.sotreg.mcda_service import (
    compute_mcda_scores, compute_sensitivity_analysis, compute_mcfadden_logit,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sotreg/scoring")


@router.post("/mcda", response_model=MCDAResponse)
async def mcda_scoring(
    body: MCDARequest,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> MCDAResponse:
    alts = [a.model_dump() for a in body.alternatives]
    result = compute_mcda_scores(alts, weights=body.weights)
    # Persist scenario
    scenario = MCDAScenario(
        tenant_id=current_user.tenant_id, name=body.scenario_name,
        alternatives=alts, weights=result["weights_used"], results=result,
    )
    db.add(scenario)
    await db.flush()
    logger.info("MCDA scored %d alternatives by user %s", len(alts), current_user.id)
    return MCDAResponse(
        ranked_alternatives=[NormalizedAlternative(**a) for a in result["ranked_alternatives"]],
        weights_used=result["weights_used"],
        criteria_ranges=result["criteria_ranges"],
        best_alternative=result["best_alternative"],
        worst_alternative=result["worst_alternative"],
    )


@router.post("/sensitivity", response_model=SensitivityResponse)
async def sensitivity_analysis(
    body: SensitivityRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
) -> SensitivityResponse:
    alts = [a.model_dump() for a in body.alternatives]
    result = compute_sensitivity_analysis(alts, weights=body.weights, delta_pct=body.delta_pct)
    logger.info("Sensitivity analysis: stability=%.1f%% by user %s", result["stability_score"], current_user.id)
    return SensitivityResponse(
        base_ranking=result["base_ranking"],
        sensitivity_results=[SensitivityCriterionResult(**s) for s in result["sensitivity_results"]],
        critical_criteria=result["critical_criteria"],
        stability_score=result["stability_score"],
    )


@router.post("/modal-choice", response_model=ModalChoiceResponse)
async def modal_choice(
    body: ModalChoiceRequest,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
) -> ModalChoiceResponse:
    alts = [a.model_dump() for a in body.alternatives]
    result = compute_mcfadden_logit(alts, body.beta_cost, body.beta_time, body.beta_comfort)
    logger.info("Modal choice: dominant=%s by user %s", result["dominant_mode"], current_user.id)
    return ModalChoiceResponse(
        probabilities=[ModalChoiceProbability(**p) for p in result["probabilities"]],
        probabilities_sum=result["probabilities_sum"],
        dominant_mode=result["dominant_mode"],
    )
