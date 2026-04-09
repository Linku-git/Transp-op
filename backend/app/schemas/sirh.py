from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# --- Connection schemas ---

class SIRHConnectionCreate(BaseModel):
    provider: str = Field(..., pattern=r"^(sap|workday|talentsoft|sage)$")
    name: str = Field(..., min_length=1, max_length=255)
    config: dict | None = None
    sync_frequency: str = Field(default="daily", pattern=r"^(hourly|daily|weekly|manual)$")
    conflict_strategy: str = Field(
        default="sirh_wins", pattern=r"^(sirh_wins|platform_wins|manual)$"
    )


class SIRHConnectionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    config: dict | None = None
    sync_frequency: str | None = Field(
        default=None, pattern=r"^(hourly|daily|weekly|manual)$"
    )
    conflict_strategy: str | None = Field(
        default=None, pattern=r"^(sirh_wins|platform_wins|manual)$"
    )
    status: str | None = Field(
        default=None, pattern=r"^(active|paused|error)$"
    )


class SIRHConnectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    provider: str
    name: str
    config: dict | None = None
    sync_frequency: str
    last_sync_at: datetime | None = None
    status: str
    conflict_strategy: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SIRHConnectionListResponse(BaseModel):
    data: list[SIRHConnectionResponse]
    total: int
    page: int = 1
    pages: int = 1


# --- Sync Log schemas ---

class SyncLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    connection_id: uuid.UUID
    tenant_id: uuid.UUID
    started_at: datetime
    completed_at: datetime | None = None
    records_created: int = 0
    records_updated: int = 0
    records_failed: int = 0
    errors: list | None = None
    status: str
    created_at: datetime


class SyncLogListResponse(BaseModel):
    data: list[SyncLogResponse]
    total: int
    page: int = 1
    pages: int = 1


# --- Conflict schemas ---

class SyncConflictResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sync_log_id: uuid.UUID
    employee_id: uuid.UUID
    field_name: str
    platform_value: str | None = None
    sirh_value: str | None = None
    resolution: str


class ConflictResolveRequest(BaseModel):
    resolution: str = Field(..., pattern=r"^(sirh_wins|platform_wins|manual)$")
    manual_value: str | None = None


# --- Sync trigger ---

class SyncTriggerResponse(BaseModel):
    sync_log_id: uuid.UUID
    status: str
    message: str
