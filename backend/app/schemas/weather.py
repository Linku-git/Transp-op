from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class WeatherForecastResponse(BaseModel):
    """Stored weather forecast record."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    site_id: uuid.UUID
    date: date
    condition_summary: str | None
    precipitation_mm: float | None
    temp_min_c: float | None
    temp_max_c: float | None
    wind_kph: float | None
    fetched_at: datetime
    source: str | None


class WeatherRefreshResponse(BaseModel):
    """Response for single-site weather refresh."""

    site_id: uuid.UUID
    forecasts_updated: int
    message: str


class WeatherRefreshAllResponse(BaseModel):
    """Response for refresh-all-sites operation."""

    sites_refreshed: int
    total_forecasts_updated: int
    errors: list[str]


class ScenarioSuggestion(BaseModel):
    """A scenario suggestion derived from weather data."""

    date: date
    condition_summary: str | None
    suggested_condition_type: str
    reason: str


class WeatherSuggestionsResponse(BaseModel):
    """Scenario suggestions for a site based on weather forecasts."""

    site_id: uuid.UUID
    suggestions: list[ScenarioSuggestion]
