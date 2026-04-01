from __future__ import annotations

import logging
import uuid
from collections import Counter
from datetime import date, datetime, timedelta
from decimal import Decimal

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.weather import WeatherForecast

logger = logging.getLogger(__name__)

_SOURCE = "openweathermap"


async def fetch_forecast_from_api(lat: float, lng: float) -> list[dict] | None:
    """Fetch 5-day/3-hour forecast from OpenWeatherMap.

    Returns the raw interval list on success, or ``None`` on failure.
    """
    if not settings.weather_api_key:
        logger.warning("Weather API key not configured — skipping fetch")
        return None

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                settings.weather_api_url,
                params={
                    "lat": lat,
                    "lon": lng,
                    "appid": settings.weather_api_key,
                    "units": "metric",
                },
            )
            response.raise_for_status()
            data = response.json()
            intervals: list[dict] = data.get("list", [])
            logger.info(
                "Fetched %d weather intervals for (%.4f, %.4f)",
                len(intervals),
                lat,
                lng,
            )
            return intervals

    except httpx.HTTPStatusError as exc:
        logger.warning(
            "Weather API HTTP error for (%.4f, %.4f): %s %s",
            lat,
            lng,
            exc.response.status_code,
            exc.response.text[:200],
        )
        return None
    except (httpx.RequestError, ValueError, KeyError) as exc:
        logger.warning("Weather API failed for (%.4f, %.4f): %s", lat, lng, exc)
        return None


def aggregate_daily(raw_intervals: list[dict], max_days: int = 3) -> list[dict]:
    """Aggregate 3-hour intervals into daily summaries.

    Returns up to *max_days* daily records starting from today.
    """
    today = date.today()
    cutoff = today + timedelta(days=max_days)

    # Group intervals by date
    by_date: dict[str, list[dict]] = {}
    for interval in raw_intervals:
        dt_txt = interval.get("dt_txt", "")
        day_str = dt_txt[:10]  # "YYYY-MM-DD"
        if not day_str:
            continue
        try:
            day = date.fromisoformat(day_str)
        except ValueError:
            continue
        if day < today or day >= cutoff:
            continue
        by_date.setdefault(day_str, []).append(interval)

    results: list[dict] = []
    for day_str in sorted(by_date.keys()):
        intervals = by_date[day_str]

        temps_min: list[float] = []
        temps_max: list[float] = []
        precip_total = 0.0
        wind_speeds: list[float] = []
        conditions: list[str] = []

        for iv in intervals:
            main = iv.get("main", {})
            temps_min.append(main.get("temp_min", 0.0))
            temps_max.append(main.get("temp_max", 0.0))

            rain_3h = iv.get("rain", {}).get("3h", 0.0)
            snow_3h = iv.get("snow", {}).get("3h", 0.0)
            precip_total += rain_3h + snow_3h

            wind_speed_ms = iv.get("wind", {}).get("speed", 0.0)
            wind_speeds.append(wind_speed_ms * 3.6)  # m/s -> km/h

            weather_list = iv.get("weather", [])
            if weather_list:
                conditions.append(weather_list[0].get("main", "Clear"))

        # Most frequent condition
        condition_summary = "Clear"
        if conditions:
            condition_summary = Counter(conditions).most_common(1)[0][0]

        results.append({
            "date": date.fromisoformat(day_str),
            "condition_summary": condition_summary,
            "precipitation_mm": round(precip_total, 2),
            "temp_min_c": round(min(temps_min), 2) if temps_min else None,
            "temp_max_c": round(max(temps_max), 2) if temps_max else None,
            "wind_kph": round(max(wind_speeds), 2) if wind_speeds else None,
        })

    return results


async def refresh_forecast_for_site(
    db: AsyncSession,
    site_id: uuid.UUID,
    lat: float,
    lng: float,
) -> int:
    """Fetch and upsert weather forecasts for a single site.

    Returns the number of forecast records upserted.
    """
    raw = await fetch_forecast_from_api(lat, lng)
    if raw is None:
        return 0

    daily = aggregate_daily(raw)
    count = 0

    for day_data in daily:
        # Check for existing record
        stmt = select(WeatherForecast).where(
            WeatherForecast.site_id == site_id,
            WeatherForecast.date == day_data["date"],
            WeatherForecast.source == _SOURCE,
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.condition_summary = day_data["condition_summary"]
            existing.precipitation_mm = (
                Decimal(str(day_data["precipitation_mm"]))
                if day_data["precipitation_mm"] is not None
                else None
            )
            existing.temp_min_c = (
                Decimal(str(day_data["temp_min_c"]))
                if day_data["temp_min_c"] is not None
                else None
            )
            existing.temp_max_c = (
                Decimal(str(day_data["temp_max_c"]))
                if day_data["temp_max_c"] is not None
                else None
            )
            existing.wind_kph = (
                Decimal(str(day_data["wind_kph"]))
                if day_data["wind_kph"] is not None
                else None
            )
        else:
            forecast = WeatherForecast(
                site_id=site_id,
                date=day_data["date"],
                condition_summary=day_data["condition_summary"],
                precipitation_mm=(
                    Decimal(str(day_data["precipitation_mm"]))
                    if day_data["precipitation_mm"] is not None
                    else None
                ),
                temp_min_c=(
                    Decimal(str(day_data["temp_min_c"]))
                    if day_data["temp_min_c"] is not None
                    else None
                ),
                temp_max_c=(
                    Decimal(str(day_data["temp_max_c"]))
                    if day_data["temp_max_c"] is not None
                    else None
                ),
                wind_kph=(
                    Decimal(str(day_data["wind_kph"]))
                    if day_data["wind_kph"] is not None
                    else None
                ),
                source=_SOURCE,
            )
            db.add(forecast)

        count += 1

    await db.flush()
    return count


def suggest_scenario(forecasts: list[WeatherForecast]) -> list[dict]:
    """Map weather forecasts to optimization scenario suggestions."""
    suggestions: list[dict] = []

    for fc in forecasts:
        condition = (fc.condition_summary or "").lower()
        precip = float(fc.precipitation_mm) if fc.precipitation_mm else 0.0
        temp_max = float(fc.temp_max_c) if fc.temp_max_c else 20.0
        temp_min = float(fc.temp_min_c) if fc.temp_min_c else 10.0
        wind = float(fc.wind_kph) if fc.wind_kph else 0.0

        if "snow" in condition:
            suggested = "snow"
            reason = "Snowfall expected"
        elif "rain" in condition or "drizzle" in condition or precip > 5.0:
            suggested = "rain"
            reason = "Precipitation expected"
        elif temp_max > 38:
            suggested = "peak"
            reason = "Extreme heat warning"
        elif temp_min < 2:
            suggested = "night"
            reason = "Near-freezing temperatures"
        elif wind > 60:
            suggested = "rain"
            reason = "Strong wind advisory"
        else:
            suggested = "normal"
            reason = "Standard conditions"

        suggestions.append({
            "date": fc.date,
            "condition_summary": fc.condition_summary,
            "suggested_condition_type": suggested,
            "reason": reason,
        })

    return suggestions
