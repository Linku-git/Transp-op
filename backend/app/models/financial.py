from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class FinancialScenario(BaseModel):
    """Investment scenario grouping TCO entries and ROI calculations."""

    __tablename__ = "financial_scenario"
    __table_args__ = (
        Index("idx_financial_scenario_tenant", "tenant_id"),
        Index("idx_financial_scenario_created_by", "created_by"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    investment_model: Mapped[str] = mapped_column(String(30), nullable=False)
    duration_years: Mapped[int] = mapped_column(
        Integer, server_default="5", nullable=False
    )
    fleet_composition: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, server_default="{}", nullable=True
    )
    params: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, server_default="{}", nullable=True
    )
    results: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, server_default="{}", nullable=True
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id"), nullable=True
    )

    # Relationships
    tco_entries: Mapped[list[TCOEntry]] = relationship(
        "TCOEntry", back_populates="financial_scenario", cascade="all, delete-orphan"
    )
    roi_calculations: Mapped[list[ROICalculation]] = relationship(
        "ROICalculation",
        back_populates="financial_scenario",
        cascade="all, delete-orphan",
    )


class TCOEntry(BaseModel):
    """Total Cost of Ownership line item for a vehicle type within a scenario."""

    __tablename__ = "tco_entry"
    __table_args__ = (
        Index("idx_tco_entry_financial_scenario", "financial_scenario_id"),
    )

    financial_scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("financial_scenario.id", ondelete="CASCADE"),
        nullable=False,
    )
    vehicle_type: Mapped[str] = mapped_column(String(50), nullable=False)
    motorization: Mapped[str | None] = mapped_column(String(30), nullable=True)
    quantity: Mapped[int] = mapped_column(
        Integer, server_default="1", nullable=False
    )
    purchase_price: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    annual_maintenance_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    energy_cost_per_km: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 4), nullable=True
    )
    annual_km: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    residual_value: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    infrastructure_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    tco_per_vehicle: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    tco_total: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2), nullable=True
    )

    # Relationships
    financial_scenario: Mapped[FinancialScenario] = relationship(
        "FinancialScenario", back_populates="tco_entries"
    )


class ROICalculation(BaseModel):
    """Return on Investment calculation for a financial scenario."""

    __tablename__ = "roi_calculation"
    __table_args__ = (
        Index("idx_roi_calculation_financial_scenario", "financial_scenario_id"),
    )

    financial_scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("financial_scenario.id", ondelete="CASCADE"),
        nullable=False,
    )
    baseline_absence_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    target_absence_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    headcount: Mapped[int | None] = mapped_column(Integer, nullable=True)
    daily_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    replacement_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    turnover_rate_before: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    turnover_rate_after: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    training_hour_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 2), nullable=True
    )
    engagement_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    annual_travel_hours: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 2), nullable=True
    )
    roi_absenteeism: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    roi_retention: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    roi_journey: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    roi_fleet_optimization: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    roi_total: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    payback_months: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 1), nullable=True
    )

    # Relationships
    financial_scenario: Mapped[FinancialScenario] = relationship(
        "FinancialScenario", back_populates="roi_calculations"
    )


class VehicleReference(BaseModel):
    """Global vehicle catalog entry for TCO benchmarking and fleet planning."""

    __tablename__ = "vehicle_reference"

    type: Mapped[str] = mapped_column(String(50), nullable=False)
    capacity_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    capacity_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    motorizations_available: Mapped[list[Any] | None] = mapped_column(
        JSONB, server_default="[]", nullable=True
    )
    recommended_use: Mapped[str | None] = mapped_column(Text, nullable=True)
    reference_tco_5y: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, server_default="{}", nullable=True
    )
    length_meters: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    zfe_compliant: Mapped[bool] = mapped_column(
        Boolean, server_default="true", nullable=False
    )
