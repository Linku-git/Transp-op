"""ML Model Registry — versioning, serialization, and lifecycle management."""
from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ml_model import MLModel

logger = logging.getLogger(__name__)

MODEL_STORAGE_DIR = os.environ.get("ML_MODEL_DIR", "/tmp/transpop_ml_models")

VALID_MODEL_TYPES = {"isolation_forest", "random_forest", "lstm"}
VALID_STATUSES = {"training", "ready", "promoted", "retired"}


async def save_model(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    model_type: str,
    model_obj: Any,
    metrics: dict | None = None,
    feature_names: list[str] | None = None,
) -> MLModel:
    """Serialize and persist a trained ML model.

    Auto-increments version per model_type per tenant. Serializes using
    joblib (for sklearn models) and stores the file path.

    Args:
        db: Async database session.
        tenant_id: Tenant UUID.
        model_type: One of isolation_forest, random_forest, lstm.
        model_obj: The trained model object (sklearn or keras).
        metrics: Optional evaluation metrics dict.
        feature_names: Optional list of feature names used.

    Returns:
        Persisted MLModel instance.
    """
    if model_type not in VALID_MODEL_TYPES:
        raise ValueError(f"Invalid model_type: {model_type}. Must be one of {VALID_MODEL_TYPES}")

    # Compute next version
    stmt = select(func.coalesce(func.max(MLModel.version), 0)).where(
        and_(MLModel.tenant_id == tenant_id, MLModel.model_type == model_type)
    )
    result = await db.execute(stmt)
    max_version = result.scalar_one()
    next_version = max_version + 1

    # Serialize model
    os.makedirs(MODEL_STORAGE_DIR, exist_ok=True)
    filename = f"{model_type}_v{next_version}_{tenant_id}.joblib"
    file_path = os.path.join(MODEL_STORAGE_DIR, filename)

    try:
        import joblib
        joblib.dump(model_obj, file_path)
    except Exception as exc:
        logger.warning("joblib serialization failed, storing path only: %s", exc)
        file_path = f"pending://{filename}"

    ml_model = MLModel(
        tenant_id=tenant_id,
        model_type=model_type,
        version=next_version,
        status="ready",
        metrics=metrics,
        file_path=file_path,
        trained_at=datetime.now(timezone.utc),
        feature_names=feature_names,
    )
    db.add(ml_model)
    await db.flush()

    logger.info(
        "Saved model %s v%d for tenant %s (metrics=%s)",
        model_type, next_version, tenant_id, metrics,
    )
    return ml_model


async def load_model(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    model_type: str,
    version: int | None = None,
) -> tuple[Any | None, MLModel | None]:
    """Load a serialized model from the registry.

    Args:
        db: Async database session.
        tenant_id: Tenant UUID.
        model_type: Model type to load.
        version: Specific version, or None for latest promoted.

    Returns:
        Tuple of (deserialized model object or None, MLModel metadata or None).
    """
    if version is not None:
        stmt = select(MLModel).where(
            and_(
                MLModel.tenant_id == tenant_id,
                MLModel.model_type == model_type,
                MLModel.version == version,
            )
        )
    else:
        # Load latest promoted, fallback to latest ready
        stmt = (
            select(MLModel)
            .where(
                and_(
                    MLModel.tenant_id == tenant_id,
                    MLModel.model_type == model_type,
                    MLModel.status.in_(["promoted", "ready"]),
                )
            )
            .order_by(
                # promoted first, then by version desc
                MLModel.status.desc(),
                MLModel.version.desc(),
            )
            .limit(1)
        )

    result = await db.execute(stmt)
    ml_model = result.scalar_one_or_none()

    if ml_model is None:
        return None, None

    # Deserialize
    model_obj = None
    if ml_model.file_path and not ml_model.file_path.startswith("pending://"):
        try:
            import joblib
            model_obj = joblib.load(ml_model.file_path)
        except Exception as exc:
            logger.warning("Failed to load model file %s: %s", ml_model.file_path, exc)

    return model_obj, ml_model


async def promote(
    db: AsyncSession,
    model_id: uuid.UUID,
) -> MLModel | None:
    """Promote a model to production, retiring the previous promoted version.

    Args:
        db: Async database session.
        model_id: UUID of the model to promote.

    Returns:
        The promoted MLModel, or None if not found.
    """
    stmt = select(MLModel).where(MLModel.id == model_id)
    result = await db.execute(stmt)
    ml_model = result.scalar_one_or_none()
    if ml_model is None:
        return None

    # Retire current promoted model of same type/tenant
    retire_stmt = select(MLModel).where(
        and_(
            MLModel.tenant_id == ml_model.tenant_id,
            MLModel.model_type == ml_model.model_type,
            MLModel.status == "promoted",
            MLModel.id != model_id,
        )
    )
    retire_result = await db.execute(retire_stmt)
    for old_model in retire_result.scalars().all():
        old_model.status = "retired"
        logger.info("Retired model %s v%d", old_model.model_type, old_model.version)

    ml_model.status = "promoted"
    await db.flush()
    logger.info("Promoted model %s v%d", ml_model.model_type, ml_model.version)
    return ml_model


async def retire(
    db: AsyncSession,
    model_id: uuid.UUID,
) -> MLModel | None:
    """Retire a model.

    Args:
        db: Async database session.
        model_id: UUID of the model to retire.

    Returns:
        The retired MLModel, or None if not found.
    """
    stmt = select(MLModel).where(MLModel.id == model_id)
    result = await db.execute(stmt)
    ml_model = result.scalar_one_or_none()
    if ml_model is None:
        return None

    ml_model.status = "retired"
    await db.flush()
    logger.info("Retired model %s v%d", ml_model.model_type, ml_model.version)
    return ml_model


async def list_models(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    model_type: str | None = None,
) -> list[MLModel]:
    """List all models for a tenant, optionally filtered by type.

    Returns:
        List of MLModel instances ordered by model_type, version desc.
    """
    stmt = select(MLModel).where(MLModel.tenant_id == tenant_id)
    if model_type:
        stmt = stmt.where(MLModel.model_type == model_type)
    stmt = stmt.order_by(MLModel.model_type, MLModel.version.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())
