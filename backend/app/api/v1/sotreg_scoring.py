from __future__ import annotations
import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.mcda_scenario import MCDAScenario
from app.models.generated_report import GeneratedReport
from app.schemas.mcda_scenario import (
    MCDARequest, MCDAResponse, NormalizedAlternative,
    SensitivityRequest, SensitivityResponse, SensitivityCriterionResult,
    ModalChoiceRequest, ModalChoiceResponse, ModalChoiceProbability,
)
from app.services.sotreg.mcda_service import (
    compute_mcda_scores, compute_sensitivity_analysis, compute_mcfadden_logit,
)
from app.services.sotreg.mcda_report import generate_mcda_report

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


# ---------------------------------------------------------------------------
# MCDA Report generation endpoints
# ---------------------------------------------------------------------------


@router.post("/report/pdf/{scenario_id}")
async def generate_mcda_pdf_report(
    scenario_id: uuid.UUID = Path(..., description="MCDAScenario UUID"),
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Generate a PDF comparison report for an MCDA scenario.

    Returns the PDF bytes directly with appropriate content headers.
    For large scenarios, consider using the Celery task endpoint instead.
    """
    report_bytes = await generate_mcda_report(scenario_id, db, "pdf")
    if report_bytes is None:
        raise HTTPException(status_code=404, detail="MCDA scenario not found")

    # Persist report record
    report = GeneratedReport(
        tenant_id=current_user.tenant_id,
        report_type="mcda_scenario",
        format="pdf",
        generated_by=current_user.id,
        params={"scenario_id": str(scenario_id)},
    )
    db.add(report)
    await db.flush()

    logger.info(
        "MCDA PDF report generated for scenario %s by user %s (%d bytes)",
        scenario_id, current_user.id, len(report_bytes),
    )

    return Response(
        content=report_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="mcda_report_{scenario_id}.pdf"',
        },
    )


@router.post("/report/excel/{scenario_id}")
async def generate_mcda_excel_report(
    scenario_id: uuid.UUID = Path(..., description="MCDAScenario UUID"),
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Generate an Excel comparison report for an MCDA scenario.

    Returns a multi-sheet .xlsx workbook with Summary, Scores,
    Sensitivity, and Raw Data sheets.
    """
    report_bytes = await generate_mcda_report(scenario_id, db, "xlsx")
    if report_bytes is None:
        raise HTTPException(status_code=404, detail="MCDA scenario not found")

    # Persist report record
    report = GeneratedReport(
        tenant_id=current_user.tenant_id,
        report_type="mcda_scenario",
        format="xlsx",
        generated_by=current_user.id,
        params={"scenario_id": str(scenario_id)},
    )
    db.add(report)
    await db.flush()

    logger.info(
        "MCDA Excel report generated for scenario %s by user %s (%d bytes)",
        scenario_id, current_user.id, len(report_bytes),
    )

    return Response(
        content=report_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="mcda_report_{scenario_id}.xlsx"',
        },
    )
