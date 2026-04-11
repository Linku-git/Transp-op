"""Feature Store — computed feature caching for ML pipelines."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feature_store import FeatureRecord

logger = logging.getLogger(__name__)

VALID_ENTITY_TYPES = {"vehicle", "driver", "route", "stop"}
VALID_WINDOWS = {"1h", "24h", "7d", "30d"}

# Feature computation functions (pluggable per entity type)
FEATURE_COMPUTERS: dict[str, Any] = {}


def register_feature_computer(entity_type: str, func: Any) -> None:
    """Register a feature computation function for an entity type."""
    FEATURE_COMPUTERS[entity_type] = func


async def compute_features(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    entity_type: str,
    entity_id: uuid.UUID,
    window: str = "24h",
    feature_values: dict[str, float] | None = None,
) -> list[FeatureRecord]:
    """Compute and cache features for a single entity.

    If feature_values is provided, stores them directly. Otherwise uses
    the registered feature computer for the entity type.

    Args:
        db: Async database session.
        tenant_id: Tenant UUID.
        entity_type: One of vehicle, driver, route, stop.
        entity_id: Entity UUID.
        window: Time window (1h, 24h, 7d, 30d).
        feature_values: Optional pre-computed feature dict.

    Returns:
        List of persisted FeatureRecord instances.
    """
    if entity_type not in VALID_ENTITY_TYPES:
        raise ValueError(f"Invalid entity_type: {entity_type}")
    if window not in VALID_WINDOWS:
        raise ValueError(f"Invalid window: {window}")

    now = datetime.now(timezone.utc)

    if feature_values is None:
        computer = FEATURE_COMPUTERS.get(entity_type)
        if computer:
            feature_values = await computer(db, tenant_id, entity_id, window)
        else:
            # Default dummy features for testing
            feature_values = {
                "mean_speed": 45.0,
                "fuel_efficiency": 8.5,
                "trip_count": 12.0,
                "avg_load": 0.65,
            }

    # Delete old features for this entity/window
    del_stmt = delete(FeatureRecord).where(
        and_(
            FeatureRecord.tenant_id == tenant_id,
            FeatureRecord.entity_type == entity_type,
            FeatureRecord.entity_id == entity_id,
            FeatureRecord.window == window,
        )
    )
    await db.execute(del_stmt)

    records: list[FeatureRecord] = []
    for name, value in feature_values.items():
        record = FeatureRecord(
            tenant_id=tenant_id,
            entity_type=entity_type,
            entity_id=entity_id,
            feature_name=name,
            feature_value=float(value),
            computed_at=now,
            window=window,
        )
        db.add(record)
        records.append(record)

    await db.flush()
    logger.info(
        "Computed %d features for %s/%s window=%s",
        len(records), entity_type, entity_id, window,
    )
    return records


async def get_features(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    entity_type: str,
    entity_id: uuid.UUID,
    feature_names: list[str] | None = None,
    window: str = "24h",
) -> dict[str, float]:
    """Retrieve latest features for an entity.

    Args:
        db: Async database session.
        tenant_id: Tenant UUID.
        entity_type: Entity type.
        entity_id: Entity UUID.
        feature_names: Optional filter for specific feature names.
        window: Time window.

    Returns:
        Dict mapping feature_name to feature_value.
    """
    stmt = select(FeatureRecord).where(
        and_(
            FeatureRecord.tenant_id == tenant_id,
            FeatureRecord.entity_type == entity_type,
            FeatureRecord.entity_id == entity_id,
            FeatureRecord.window == window,
        )
    )
    if feature_names:
        stmt = stmt.where(FeatureRecord.feature_name.in_(feature_names))

    result = await db.execute(stmt)
    records = result.scalars().all()

    return {r.feature_name: r.feature_value for r in records}


async def bulk_compute(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    entity_type: str,
    entity_ids: list[uuid.UUID],
    window: str = "24h",
) -> dict[str, dict[str, float]]:
    """Batch compute features for multiple entities.

    Args:
        db: Async database session.
        tenant_id: Tenant UUID.
        entity_type: Entity type.
        entity_ids: List of entity UUIDs.
        window: Time window.

    Returns:
        Dict mapping entity_id (str) to feature dict.
    """
    results: dict[str, dict[str, float]] = {}
    for eid in entity_ids:
        await compute_features(db, tenant_id, entity_type, eid, window)
        features = await get_features(db, tenant_id, entity_type, eid, window=window)
        results[str(eid)] = features

    logger.info(
        "Bulk computed features for %d %s entities",
        len(entity_ids), entity_type,
    )
    return results
