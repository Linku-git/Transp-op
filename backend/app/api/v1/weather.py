from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.site import Site
from app.models.weather import WeatherForecast
from app.schemas.weather import (
    ScenarioSuggestion,
    WeatherForecastResponse,
    WeatherRefreshAllResponse,
    WeatherRefreshResponse,
    WeatherSuggestionsResponse,
)
from app.services.weather import refresh_forecast_for_site, suggest_scenario

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/weather")


# ---------------------------------------------------------------------------
# POST /weather/refresh-all — refresh all sites (admin only)
# ---------------------------------------------------------------------------


@router.post("/refresh-all", response_model=WeatherRefreshAllResponse)
async def refresh_all_sites(
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> WeatherRefreshAllResponse:
    """Refresh weather forecasts for all tenant sites."""
    stmt = select(Site).where(
        Site.tenant_id == current_user.tenant_id,
        Site.lat.isnot(None),
        Site.lng.isnot(None),
    )
    result = await db.execute(stmt)
    sites = list(result.scalars().all())

    sites_refreshed = 0
    total_forecasts = 0
    errors: list[str] = []

    for site in sites:
        try:
            count = await refresh_forecast_for_site(db, site.id, site.lat, site.lng)
            total_forecasts += count
            sites_refreshed += 1
        except Exception as exc:
            logger.warning("Weather refresh failed for site %s: %s", site.id, exc)
            errors.append(f"{site.name} ({site.id}): {exc}")

    await db.commit()
    return WeatherRefreshAllResponse(
        sites_refreshed=sites_refreshed,
        total_forecasts_updated=total_forecasts,
        errors=errors,
    )


# ---------------------------------------------------------------------------
# GET /weather/{site_id} — get stored forecasts
# ---------------------------------------------------------------------------


@router.get("/{site_id}", response_model=list[WeatherForecastResponse])
async def get_forecasts(
    site_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> list[WeatherForecastResponse]:
    """Get stored weather forecasts for a site."""
    # Verify site belongs to tenant
    site = await _get_tenant_site(db, site_id, current_user.tenant_id)

    stmt = (
        select(WeatherForecast)
        .where(WeatherForecast.site_id == site.id)
        .order_by(WeatherForecast.date.asc())
    )
    result = await db.execute(stmt)
    forecasts = list(result.scalars().all())

    return [WeatherForecastResponse.model_validate(f) for f in forecasts]


# ---------------------------------------------------------------------------
# POST /weather/{site_id}/refresh — refresh from provider
# ---------------------------------------------------------------------------


@router.post("/{site_id}/refresh", response_model=WeatherRefreshResponse)
async def refresh_site_forecast(
    site_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> WeatherRefreshResponse:
    """Refresh weather forecasts for a single site from the provider."""
    site = await _get_tenant_site(db, site_id, current_user.tenant_id)

    try:
        count = await refresh_forecast_for_site(db, site.id, site.lat, site.lng)
    except Exception as exc:
        logger.exception("Weather refresh failed for site %s", site_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"External weather API error: {exc}",
        ) from exc

    await db.commit()
    return WeatherRefreshResponse(
        site_id=site.id,
        forecasts_updated=count,
        message=f"Refreshed {count} forecast(s) for {site.name}",
    )


# ---------------------------------------------------------------------------
# GET /weather/{site_id}/suggestions — scenario suggestions
# ---------------------------------------------------------------------------


@router.get("/{site_id}/suggestions", response_model=WeatherSuggestionsResponse)
async def get_suggestions(
    site_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> WeatherSuggestionsResponse:
    """Get scenario suggestions based on stored weather forecasts."""
    site = await _get_tenant_site(db, site_id, current_user.tenant_id)

    stmt = (
        select(WeatherForecast)
        .where(WeatherForecast.site_id == site.id)
        .order_by(WeatherForecast.date.asc())
    )
    result = await db.execute(stmt)
    forecasts = list(result.scalars().all())

    raw_suggestions = suggest_scenario(forecasts)
    suggestions = [ScenarioSuggestion(**s) for s in raw_suggestions]

    return WeatherSuggestionsResponse(site_id=site.id, suggestions=suggestions)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_tenant_site(
    db: AsyncSession, site_id: uuid.UUID, tenant_id: uuid.UUID
) -> Site:
    """Load a site and verify it belongs to the given tenant."""
    stmt = select(Site).where(Site.id == site_id, Site.tenant_id == tenant_id)
    result = await db.execute(stmt)
    site = result.scalar_one_or_none()
    if site is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )
    return site
