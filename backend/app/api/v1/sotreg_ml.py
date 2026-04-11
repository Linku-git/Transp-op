"""API endpoints for ML Model Registry and Feature Store."""
from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.schemas.ml_model import (
    FeatureResponse,
    MLModelListResponse,
    MLModelResponse,
    RetrainRequest,
    RetrainResponse,
)
from app.services.sotreg.model_registry import list_models
from app.services.sotreg.feature_store import get_features

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sotreg/ml")


@router.get("/models", response_model=MLModelListResponse)
async def get_models(
    model_type: str | None = Query(default=None, description="Filter by model type"),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> MLModelListResponse:
    """List all ML models in the registry."""
    models = await list_models(db, current_user.tenant_id, model_type)
    return MLModelListResponse(
        data=[MLModelResponse.model_validate(m) for m in models],
        total=len(models),
    )


@router.post("/retrain/{model_type}", response_model=RetrainResponse)
async def trigger_retrain(
    model_type: str = Path(..., description="Model type to retrain"),
    body: RetrainRequest = RetrainRequest(),
    current_user: User = Depends(require_role("admin")),
) -> RetrainResponse:
    """Trigger ML model retraining (async via Celery if available)."""
    from app.services.sotreg.model_registry import VALID_MODEL_TYPES

    if model_type not in VALID_MODEL_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model_type. Must be one of: {VALID_MODEL_TYPES}",
        )

    try:
        from app.tasks.ml_retrain import HAS_CELERY, run_retrain_sync
        if HAS_CELERY:
            from app.tasks.ml_retrain import ml_retrain_task
            result = ml_retrain_task.delay(
                model_type, str(current_user.tenant_id), body.force,
            )
            logger.info(
                "ML retrain task queued: %s (task_id=%s)", model_type, result.id,
            )
            return RetrainResponse(
                model_type=model_type,
                status="queued",
                message=f"Retraining {model_type} queued via Celery",
                task_id=str(result.id),
            )
        else:
            # Synchronous fallback
            result = run_retrain_sync(
                model_type, str(current_user.tenant_id), body.force,
            )
            return RetrainResponse(
                model_type=model_type,
                status=result.get("status", "completed"),
                message=f"Retraining {model_type} completed synchronously",
                task_id=None,
            )
    except Exception as exc:
        logger.exception("Failed to trigger retrain: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/features/{entity_type}/{entity_id}", response_model=FeatureResponse)
async def get_entity_features(
    entity_type: str = Path(..., description="Entity type (vehicle, driver, route, stop)"),
    entity_id: uuid.UUID = Path(..., description="Entity UUID"),
    window: str = Query(default="24h", description="Time window (1h, 24h, 7d, 30d)"),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> FeatureResponse:
    """Get cached features for a specific entity."""
    from app.services.sotreg.feature_store import VALID_ENTITY_TYPES, VALID_WINDOWS

    if entity_type not in VALID_ENTITY_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid entity_type. Must be one of: {VALID_ENTITY_TYPES}",
        )
    if window not in VALID_WINDOWS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid window. Must be one of: {VALID_WINDOWS}",
        )

    features = await get_features(
        db, current_user.tenant_id, entity_type, entity_id, window=window,
    )

    return FeatureResponse(
        entity_type=entity_type,
        entity_id=entity_id,
        features=features,
        window=window,
        computed_at=None,
    )
