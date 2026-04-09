from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.models.sirh_connection import SIRHConnection
from app.models.sync_log import SyncLog
from app.models.sync_conflict import SyncConflict
from app.services.sirh.conflict_resolver import ConflictResolver

logger = logging.getLogger(__name__)


# Fields that are synced from SIRH
SYNCABLE_FIELDS = [
    "first_name", "last_name", "email", "department",
    "shift_time", "matricule", "phone",
]


class SyncEngine:
    """Base sync engine for SIRH integrations with delta update support."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def run_sync(
        self,
        connection: SIRHConnection,
        employee_data: list[dict],
    ) -> SyncLog:
        """Execute a sync with delta update and conflict detection.

        Args:
            connection: The SIRH connection configuration
            employee_data: List of employee records from SIRH
        """
        now = datetime.now(timezone.utc)
        resolver = ConflictResolver(strategy=connection.conflict_strategy)

        # Create sync log
        sync_log = SyncLog(
            connection_id=connection.id,
            tenant_id=connection.tenant_id,
            started_at=now,
            status="running",
            records_created=0,
            records_updated=0,
            records_failed=0,
            errors=[],
        )
        self.db.add(sync_log)
        await self.db.flush()
        await self.db.refresh(sync_log)

        created = 0
        updated = 0
        failed = 0
        errors: list[str] = []

        for record in employee_data:
            try:
                matricule = record.get("matricule")
                if not matricule:
                    errors.append(f"Record missing matricule: {record}")
                    failed += 1
                    continue

                # Delta check: skip if not modified since last sync
                if connection.last_sync_at and record.get("modified_at"):
                    modified = datetime.fromisoformat(record["modified_at"])
                    if modified < connection.last_sync_at:
                        continue

                # Find existing employee
                result = await self.db.execute(
                    select(Employee).where(
                        Employee.tenant_id == connection.tenant_id,
                        Employee.matricule == matricule,
                    )
                )
                employee = result.scalar_one_or_none()

                if employee:
                    # Update with conflict detection
                    for field in SYNCABLE_FIELDS:
                        if field not in record:
                            continue
                        platform_val = str(getattr(employee, field, None) or "")
                        sirh_val = str(record.get(field) or "")

                        resolved_val, resolution = resolver.resolve(
                            field, platform_val, sirh_val
                        )

                        if resolution != "no_conflict":
                            await resolver.record_conflict(
                                self.db,
                                sync_log.id,
                                connection.tenant_id,
                                employee.id,
                                field,
                                platform_val,
                                sirh_val,
                                resolution,
                            )

                        if resolved_val is not None and resolution != "unresolved":
                            setattr(employee, field, resolved_val)

                    updated += 1
                else:
                    # Create new employee — minimal fields
                    new_employee = Employee(
                        tenant_id=connection.tenant_id,
                        matricule=matricule,
                        first_name=record.get("first_name", ""),
                        last_name=record.get("last_name", ""),
                        email=record.get("email"),
                        department=record.get("department"),
                        shift_time=record.get("shift_time"),
                        site_id=record.get("site_id"),
                    )
                    self.db.add(new_employee)
                    created += 1

            except Exception as e:
                errors.append(f"Error processing {record.get('matricule', '?')}: {e}")
                failed += 1

        # Update sync log
        sync_log.records_created = created
        sync_log.records_updated = updated
        sync_log.records_failed = failed
        sync_log.errors = errors if errors else None
        sync_log.completed_at = datetime.now(timezone.utc)
        sync_log.status = "completed" if failed == 0 else "completed_with_errors"

        # Update connection last_sync_at
        connection.last_sync_at = now

        await self.db.flush()
        await self.db.refresh(sync_log)
        return sync_log

    async def get_sync_logs(
        self,
        connection_id: uuid.UUID,
        tenant_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[SyncLog], int]:
        """Get sync history for a connection."""
        conditions = [
            SyncLog.connection_id == connection_id,
            SyncLog.tenant_id == tenant_id,
        ]

        total_result = await self.db.execute(
            select(func.count()).select_from(SyncLog).where(*conditions)
        )
        total = total_result.scalar() or 0

        result = await self.db.execute(
            select(SyncLog)
            .where(*conditions)
            .order_by(SyncLog.started_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(result.scalars().all())
        return items, total

    async def get_conflicts(
        self,
        sync_log_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> list[SyncConflict]:
        """Get conflicts for a sync log."""
        result = await self.db.execute(
            select(SyncConflict).where(
                SyncConflict.sync_log_id == sync_log_id,
                SyncConflict.tenant_id == tenant_id,
            )
        )
        return list(result.scalars().all())
