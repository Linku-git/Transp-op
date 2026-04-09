from __future__ import annotations

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sync_conflict import SyncConflict

logger = logging.getLogger(__name__)


class ConflictResolver:
    """Resolves field-level conflicts between platform and SIRH data."""

    def __init__(self, strategy: str = "sirh_wins") -> None:
        self.strategy = strategy

    def resolve(
        self,
        field_name: str,
        platform_value: str | None,
        sirh_value: str | None,
    ) -> tuple[str | None, str]:
        """Resolve a conflict and return (resolved_value, resolution_type).

        Strategies:
        - sirh_wins: always use SIRH value
        - platform_wins: always use platform value
        - manual: mark as unresolved for human review
        """
        if platform_value == sirh_value:
            return platform_value, "no_conflict"

        if self.strategy == "sirh_wins":
            return sirh_value, "sirh_wins"
        elif self.strategy == "platform_wins":
            return platform_value, "platform_wins"
        else:
            return None, "unresolved"

    async def record_conflict(
        self,
        db: AsyncSession,
        sync_log_id: uuid.UUID,
        tenant_id: uuid.UUID,
        employee_id: uuid.UUID,
        field_name: str,
        platform_value: str | None,
        sirh_value: str | None,
        resolution: str,
    ) -> SyncConflict:
        """Store a conflict record in the database."""
        conflict = SyncConflict(
            sync_log_id=sync_log_id,
            tenant_id=tenant_id,
            employee_id=employee_id,
            field_name=field_name,
            platform_value=platform_value,
            sirh_value=sirh_value,
            resolution=resolution,
        )
        db.add(conflict)
        await db.flush()
        await db.refresh(conflict)
        return conflict

    async def resolve_conflict(
        self,
        db: AsyncSession,
        conflict: SyncConflict,
        resolution: str,
        manual_value: str | None = None,
    ) -> SyncConflict:
        """Manually resolve a stored conflict."""
        conflict.resolution = resolution
        if resolution == "manual" and manual_value is not None:
            conflict.sirh_value = manual_value
        await db.flush()
        await db.refresh(conflict)
        return conflict
