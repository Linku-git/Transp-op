from __future__ import annotations

import uuid

from datetime import date

from sqlalchemy import Date, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class EmployeeLeave(BaseModel):
    """Employee leave / absence record."""

    __tablename__ = "employee_leave"
    __table_args__ = (
        Index("idx_leave_employee", "employee_id"),
        Index("idx_leave_dates", "start_date", "end_date"),
    )

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employee.id", ondelete="CASCADE"),
        nullable=False,
    )
    leave_type: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    employee: Mapped[Employee] = relationship("Employee", lazy="selectin")
