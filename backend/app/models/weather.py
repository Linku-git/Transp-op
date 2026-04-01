from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class WeatherForecast(BaseModel):
    """Weather forecast snapshot for a site on a given date."""

    __tablename__ = "weather_forecast"
    __table_args__ = (
        UniqueConstraint("site_id", "date", "source", name="uq_weather_site_date_source"),
        Index("idx_weather_forecast_site_id", "site_id"),
    )

    site_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("site.id"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    condition_summary: Mapped[str | None] = mapped_column(String(100), nullable=True)
    precipitation_mm: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2), nullable=True
    )
    temp_min_c: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    temp_max_c: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    wind_kph: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relationships
    site: Mapped[Site] = relationship("Site", lazy="selectin")
