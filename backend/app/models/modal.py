from __future__ import annotations

import uuid

from datetime import time
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class EmployeeModal(BaseModel):
    """Employee modal analysis — transport mode preferences and mobility profile."""

    __tablename__ = "employee_modal"
    __table_args__ = (
        UniqueConstraint("employee_id", name="uq_employee_modal_employee_id"),
        Index("idx_modal_employee", "employee_id"),
    )

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employee.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Transport modes
    primary_mode: Mapped[str] = mapped_column(String(50), nullable=False)
    alternative_mode: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Commute metrics
    distance_km: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    travel_time_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    frequency: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Interest & reasoning
    interest_company_transport: Mapped[str | None] = mapped_column(
        String(30), nullable=True
    )
    reason_current_mode: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Schedule
    departure_time: Mapped[time | None] = mapped_column(Time, nullable=True)

    # Pickup preferences
    accepts_common_pickup: Mapped[bool] = mapped_column(
        Boolean, server_default="true", nullable=False
    )
    max_pickup_distance_meters: Mapped[int] = mapped_column(
        Integer, server_default="500", nullable=False
    )

    # Vehicle & carpooling
    has_private_car: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False
    )
    volunteer_driver: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False
    )
    carpool_seats_available: Mapped[int] = mapped_column(
        Integer, server_default="0", nullable=False
    )
    max_detour_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Opt-in & notes
    bonus_opt_in: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False
    )
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    employee: Mapped[Employee] = relationship("Employee", lazy="selectin")
