from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_LEAVE_TYPES = ("vacation", "sick", "unpaid", "formation", "mission", "other")


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class LeaveCreate(BaseModel):
    """Schema for creating a new employee leave."""

    employee_id: uuid.UUID
    leave_type: str = Field(..., max_length=50)
    start_date: date
    end_date: date
    notes: str | None = None

    @field_validator("leave_type")
    @classmethod
    def validate_leave_type(cls, v: str) -> str:
        if v not in VALID_LEAVE_TYPES:
            raise ValueError(f"leave_type must be one of {VALID_LEAVE_TYPES}")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: date, info) -> date:
        start = info.data.get("start_date")
        if start is not None and v < start:
            raise ValueError("end_date must be >= start_date")
        return v


class LeaveUpdate(BaseModel):
    """Schema for updating an existing leave. All fields optional.

    Note: ``employee_id`` is not updatable after creation.
    """

    leave_type: str | None = Field(default=None, max_length=50)
    start_date: date | None = None
    end_date: date | None = None
    notes: str | None = None

    @field_validator("leave_type")
    @classmethod
    def validate_leave_type(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_LEAVE_TYPES:
            raise ValueError(f"leave_type must be one of {VALID_LEAVE_TYPES}")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: date | None, info) -> date | None:
        if v is not None:
            start = info.data.get("start_date")
            if start is not None and v < start:
                raise ValueError("end_date must be >= start_date")
        return v


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class LeaveResponse(BaseModel):
    """Full leave representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    leave_type: str
    start_date: date
    end_date: date
    notes: str | None

    # Timestamps (from BaseModel / TimestampMixin)
    created_at: datetime
    updated_at: datetime

    # Computed / joined field
    employee_name: str | None = None


# ---------------------------------------------------------------------------
# List / pagination schemas
# ---------------------------------------------------------------------------


class LeaveListMeta(BaseModel):
    """Pagination metadata."""

    page: int
    pages: int
    total: int
    page_size: int


class LeaveListResponse(BaseModel):
    """Paginated list response wrapper for leaves."""

    data: list[LeaveResponse]
    meta: LeaveListMeta
