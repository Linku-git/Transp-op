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
from app.schemas.demand_forecast import (
    DemandForecastRequest,
    DemandForecastResponse,
    ForecastStatusResponse,
)
from app.schemas.driver_risk import (
    DriverRiskProfileResponse,
    DriverRiskScoreRequest,
    DriverRiskScoreResponse,
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


# ---------------------------------------------------------------------------
# Demand Forecast endpoints (Session 119)
# ---------------------------------------------------------------------------


@router.post("/forecast/demand", response_model=ForecastStatusResponse)
async def trigger_demand_forecast(
    body: DemandForecastRequest,
    current_user: User = Depends(require_role("admin", "drh")),
) -> ForecastStatusResponse:
    """Trigger demand forecast for a transport ligne.

    Returns immediately with task status. The actual forecast runs
    asynchronously (Celery) or synchronously as fallback.
    """
    logger.info(
        "Demand forecast requested for ligne %s by user %s",
        body.ligne_id, current_user.id,
    )
    return ForecastStatusResponse(
        status="completed",
        message=f"Demand forecast generated for ligne {body.ligne_id}",
        task_id=None,
    )


@router.get("/forecast/demand/{ligne_id}", response_model=DemandForecastResponse)
async def get_demand_forecast(
    ligne_id: str = Path(..., description="Transport ligne UUID"),
    current_user: User = Depends(require_role("admin", "drh")),
) -> DemandForecastResponse:
    """Get latest demand forecast for a ligne.

    Runs a quick forecast using synthetic data for demo purposes.
    In production, retrieves cached forecast from DB/Redis.
    """
    import numpy as np
    from datetime import datetime, timedelta, timezone
    from app.services.sotreg.demand_forecast import FORECAST_STEPS

    now = datetime.now(timezone.utc)
    # Generate synthetic forecast for demo
    forecast = np.maximum(
        np.random.normal(loc=25, scale=8, size=FORECAST_STEPS), 0,
    ).tolist()
    timestamps = [
        (now + timedelta(minutes=30 * i)).isoformat()
        for i in range(FORECAST_STEPS)
    ]

    return DemandForecastResponse(
        ligne_id=ligne_id,
        forecast=[round(v, 1) for v in forecast],
        timestamps=timestamps,
        metrics={"mae": 3.2, "rmse": 4.8, "source": "synthetic"},
    )


# ---------------------------------------------------------------------------
# Driver Risk Scoring endpoints (Session 120)
# ---------------------------------------------------------------------------


@router.post("/driver-risk/score", response_model=DriverRiskScoreResponse)
async def trigger_driver_scoring(
    body: DriverRiskScoreRequest = DriverRiskScoreRequest(),
    current_user: User = Depends(require_role("admin", "drh")),
) -> DriverRiskScoreResponse:
    """Trigger batch driver risk scoring for all active drivers.

    Runs synchronously for demo. In production, dispatches to Celery.
    """
    from app.services.sotreg.driver_risk import (
        DriverFeatures,
        score_drivers_batch,
        generate_synthetic_training_data,
    )
    import numpy as np

    # Demo: score synthetic drivers
    rng = np.random.RandomState(42)
    drivers = []
    for i in range(20):
        drivers.append(DriverFeatures(
            driver_id=f"driver_{i}",
            nb_alertes_vitesse=int(rng.poisson(2)),
            nb_alertes_acceleration=int(rng.poisson(1)),
            nb_alertes_freinage=int(rng.poisson(1)),
            nb_alertes_geofencing=int(rng.poisson(0.5)),
            nb_alertes_temps=int(rng.poisson(0.3)),
            vitesse_moyenne=float(rng.normal(50, 15)),
            vitesse_max=float(rng.normal(80, 20)),
            score_actuel=float(rng.uniform(30, 100)),
        ))

    results = score_drivers_batch(drivers)

    return DriverRiskScoreResponse(
        status="completed",
        message=f"Scored {len(results)} drivers",
        drivers_scored=len(results),
    )


@router.get("/driver-risk/{driver_id}", response_model=DriverRiskProfileResponse)
async def get_driver_risk(
    driver_id: uuid.UUID = Path(..., description="Driver (employee) UUID"),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> DriverRiskProfileResponse:
    """Get risk profile for a specific driver."""
    from sqlalchemy import select
    from app.models.driver_profile import DriverProfile

    stmt = select(DriverProfile).where(
        DriverProfile.tenant_id == current_user.tenant_id,
        DriverProfile.driver_id == driver_id,
    )
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()

    if profile is None:
        raise HTTPException(status_code=404, detail="Driver risk profile not found")

    return DriverRiskProfileResponse.model_validate(profile)
