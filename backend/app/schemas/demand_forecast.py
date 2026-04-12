"""Pydantic schemas for LSTM demand forecasting (Session 119)."""
from __future__ import annotations

from pydantic import BaseModel, Field


class DemandForecastRequest(BaseModel):
    """Request to trigger demand forecast for a ligne."""

    ligne_id: str = Field(..., description="UUID of the transport ligne")
    lookback_days: int = Field(default=7, ge=1, le=30, description="Lookback window in days")
    include_weather: bool = Field(default=True, description="Include weather features")


class DemandForecastResponse(BaseModel):
    """Response containing demand forecast results."""

    ligne_id: str
    forecast: list[float] = Field(..., description="Forecast values (48 steps, 30-min intervals)")
    timestamps: list[str] = Field(..., description="ISO timestamps for each forecast step")
    metrics: dict = Field(default_factory=dict, description="Model metrics (MAE, RMSE)")
    model_version: int | None = None
    horizon_hours: int = Field(default=24, description="Forecast horizon in hours")


class ForecastStatusResponse(BaseModel):
    """Status of a forecast task."""

    status: str
    message: str
    task_id: str | None = None
