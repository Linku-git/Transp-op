from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_delivery import ContentDelivery
from app.models.training_module import TrainingModule
from app.services.lms import get_connector
from app.services.lms.base_connector import LMSCompletion

logger = logging.getLogger(__name__)


async def sync_catalog(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    provider: str,
    config: dict | None = None,
) -> tuple[int, list[str]]:
    """Import training catalog from LMS into TrainingModule records."""
    connector = get_connector(provider, config)
    errors: list[str] = []
    imported = 0

    try:
        courses = await connector.fetch_catalog()
    except Exception as e:
        return 0, [f"Failed to fetch catalog: {e}"]

    for course in courses:
        try:
            # Check if module already exists
            result = await db.execute(
                select(TrainingModule).where(
                    TrainingModule.tenant_id == tenant_id,
                    TrainingModule.lms_provider == provider,
                    TrainingModule.lms_external_id == course.external_id,
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                # Update
                existing.duration_minutes = course.duration_minutes
                existing.is_mandatory = course.is_mandatory
                existing.certification_name = course.certification_name
                existing.lms_metadata = course.metadata
                existing.last_synced_at = datetime.now(timezone.utc)
            else:
                # Create — requires a content_id, skip if no matching content
                logger.info(
                    "New LMS course %s from %s — needs content_id mapping",
                    course.external_id,
                    provider,
                )
                continue

            imported += 1
        except Exception as e:
            errors.append(f"Course {course.external_id}: {e}")

    if imported > 0:
        await db.flush()

    return imported, errors


async def export_completions(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    provider: str,
    config: dict | None = None,
) -> tuple[int, list[str]]:
    """Export completion records from ContentDelivery to LMS."""
    connector = get_connector(provider, config)
    errors: list[str] = []
    exported = 0

    # Get all training modules for this provider
    result = await db.execute(
        select(TrainingModule).where(
            TrainingModule.tenant_id == tenant_id,
            TrainingModule.lms_provider == provider,
            TrainingModule.is_active.is_(True),
        )
    )
    modules = list(result.scalars().all())

    for module in modules:
        # Get completed deliveries for this content
        deliveries_result = await db.execute(
            select(ContentDelivery).where(
                ContentDelivery.content_id == module.content_id,
                ContentDelivery.tenant_id == tenant_id,
                ContentDelivery.completed_at.isnot(None),
            )
        )
        deliveries = list(deliveries_result.scalars().all())

        for delivery in deliveries:
            try:
                completion = LMSCompletion(
                    external_id=module.lms_external_id,
                    employee_external_id=str(delivery.employee_id),
                    completed_at=delivery.completed_at.isoformat(),
                    score=delivery.quiz_score,
                    time_spent_seconds=delivery.time_spent_seconds,
                )
                success = await connector.export_completion(completion)
                if success:
                    exported += 1
            except Exception as e:
                errors.append(
                    f"Module {module.lms_external_id}, employee {delivery.employee_id}: {e}"
                )

    return exported, errors


async def full_sync(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    provider: str,
    config: dict | None = None,
) -> dict:
    """Run full bidirectional sync: import catalog + export completions."""
    imported, import_errors = await sync_catalog(db, tenant_id, provider, config)
    exported, export_errors = await export_completions(db, tenant_id, provider, config)

    return {
        "provider": provider,
        "imported": imported,
        "exported": exported,
        "errors": import_errors + export_errors,
    }


async def get_completions(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict], int]:
    """Get completion records with training module info."""
    conditions = [
        ContentDelivery.tenant_id == tenant_id,
        ContentDelivery.completed_at.isnot(None),
    ]

    total_result = await db.execute(
        select(func.count()).select_from(ContentDelivery).where(*conditions)
    )
    total = total_result.scalar() or 0

    result = await db.execute(
        select(ContentDelivery)
        .where(*conditions)
        .order_by(ContentDelivery.completed_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    deliveries = list(result.scalars().all())

    # Enrich with training module info
    records = []
    for d in deliveries:
        module_result = await db.execute(
            select(TrainingModule).where(
                TrainingModule.content_id == d.content_id,
                TrainingModule.tenant_id == tenant_id,
            )
        )
        module = module_result.scalar_one_or_none()

        records.append({
            "employee_id": d.employee_id,
            "content_id": d.content_id,
            "training_module_id": module.id if module else None,
            "lms_provider": module.lms_provider if module else None,
            "lms_external_id": module.lms_external_id if module else None,
            "completed_at": d.completed_at,
            "quiz_score": d.quiz_score,
            "time_spent_seconds": d.time_spent_seconds,
            "certification_name": module.certification_name if module else None,
        })

    return records, total


async def handle_webhook_event(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    provider: str,
    payload: dict,
) -> bool:
    """Process a real-time webhook from an LMS."""
    connector = get_connector(provider)
    completion = await connector.handle_webhook(payload)
    if not completion:
        return False

    # Find the training module
    result = await db.execute(
        select(TrainingModule).where(
            TrainingModule.tenant_id == tenant_id,
            TrainingModule.lms_provider == provider,
            TrainingModule.lms_external_id == completion.external_id,
        )
    )
    module = result.scalar_one_or_none()
    if not module:
        logger.warning(
            "Webhook: unknown module %s from %s",
            completion.external_id,
            provider,
        )
        return False

    # Update or create ContentDelivery
    delivery_result = await db.execute(
        select(ContentDelivery).where(
            ContentDelivery.content_id == module.content_id,
            ContentDelivery.employee_id == uuid.UUID(completion.employee_external_id)
            if completion.employee_external_id
            else ContentDelivery.employee_id.is_(None),
        )
    )
    delivery = delivery_result.scalar_one_or_none()

    now = datetime.now(timezone.utc)
    if delivery:
        delivery.completed_at = now
        if completion.score is not None:
            delivery.quiz_score = completion.score
        if completion.time_spent_seconds is not None:
            delivery.time_spent_seconds = completion.time_spent_seconds
    else:
        logger.info(
            "Webhook: no existing delivery for module %s — skipping",
            completion.external_id,
        )

    await db.flush()
    return True
