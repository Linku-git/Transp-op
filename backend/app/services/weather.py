from __future__ import annotations

import logging
import uuid
from collections import Counter
from datetime import date, timedelta
from decimal import Decimal

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.weather import WeatherForecast

logger = logging.getLogger(__name__)

_SOURCE = "open-meteo"

_OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

_WMO_TO_CONDITION: dict[int, str] = {
    0: "Clear",
    1: "Clear",
    2: "Clouds",
    3: "Clouds",
    45: "Fog",
    48: "Fog",
    51: "Drizzle",
    53: "Drizzle",
    55: "Drizzle",
    56: "Drizzle",
    57: "Drizzle",
    61: "Rain",
    63: "Rain",
    65: "Rain",
    66: "Rain",
    67: "Rain",
    71: "Snow",
    73: "Snow",
    75: "Snow",
    77: "Snow",
    80: "Rain",
    81: "Rain",
    82: "Rain",
    85: "Snow",
    86: "Snow",
    95: "Thunderstorm",
    96: "Thunderstorm",
    99: "Thunderstorm",
}


def _wmo_to_condition(code: int | None) -> str:
    if code is None:
        return "Clear"
    return _WMO_TO_CONDITION.get(code, "Clouds")


async def fetch_forecast_from_api(lat: float, lng: float) -> list[dict] | None:
    """Fetch 5-day daily forecast from Open-Meteo (no API key required).

    Returns a list of daily summary dicts on success, or ``None`` on failure.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                _OPEN_METEO_URL,
                params={
                    "latitude": lat,
                    "longitude": lng,
                    "daily": ",".join([
                        "weathercode",
                        "temperature_2m_max",
                        "temperature_2m_min",
                        "precipitation_sum",
                        "windspeed_10m_max",
                    ]),
                    "timezone": "auto",
                    "forecast_days": 5,
                },
            )
            response.raise_for_status()
            data = response.json()

            daily = data.get("daily", {})
            times: list[str] = daily.get("time", [])
            weathercodes: list[int | None] = daily.get("weathercode", [])
            temp_max: list[float | None] = daily.get("temperature_2m_max", [])
            temp_min: list[float | None] = daily.get("temperature_2m_min", [])
            precip: list[float | None] = daily.get("precipitation_sum", [])
            wind: list[float | None] = daily.get("windspeed_10m_max", [])

            days: list[dict] = []
            today = date.today()
            for i, day_str in enumerate(times):
                try:
                    day = date.fromisoformat(day_str)
                except ValueError:
                    continue
                if day < today:
                    continue
                wmo = weathercodes[i] if i < len(weathercodes) else None
                days.append({
                    "date": day,
                    "condition_summary": _wmo_to_condition(wmo),
                    "temp_max_c": temp_max[i] if i < len(temp_max) else None,
                    "temp_min_c": temp_min[i] if i < len(temp_min) else None,
                    "precipitation_mm": precip[i] if i < len(precip) else None,
                    "wind_kph": wind[i] if i < len(wind) else None,
                })

            logger.info(
                "Fetched %d daily forecasts from Open-Meteo for (%.4f, %.4f)",
                len(days),
                lat,
                lng,
            )
            return days

    except httpx.HTTPStatusError as exc:
        logger.warning(
            "Open-Meteo HTTP error for (%.4f, %.4f): %s %s",
            lat,
            lng,
            exc.response.status_code,
            exc.response.text[:200],
        )
        return None
    except (httpx.RequestError, ValueError, KeyError) as exc:
        logger.warning("Open-Meteo request failed for (%.4f, %.4f): %s", lat, lng, exc)
        return None


async def refresh_forecast_for_site(
    db: AsyncSession,
    site_id: uuid.UUID,
    lat: float,
    lng: float,
) -> int:
    """Fetch and upsert weather forecasts for a single site.

    Returns the number of forecast records upserted.
    """
    days = await fetch_forecast_from_api(lat, lng)
    if days is None:
        return 0

    count = 0

    for day_data in days:
        stmt = select(WeatherForecast).where(
            WeatherForecast.site_id == site_id,
            WeatherForecast.date == day_data["date"],
            WeatherForecast.source == _SOURCE,
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        def _decimal(val: float | None) -> Decimal | None:
            return Decimal(str(val)) if val is not None else None

        if existing:
            existing.condition_summary = day_data["condition_summary"]
            existing.precipitation_mm = _decimal(day_data["precipitation_mm"])
            existing.temp_min_c = _decimal(day_data["temp_min_c"])
            existing.temp_max_c = _decimal(day_data["temp_max_c"])
            existing.wind_kph = _decimal(day_data["wind_kph"])
        else:
            forecast = WeatherForecast(
                site_id=site_id,
                date=day_data["date"],
                condition_summary=day_data["condition_summary"],
                precipitation_mm=_decimal(day_data["precipitation_mm"]),
                temp_min_c=_decimal(day_data["temp_min_c"]),
                temp_max_c=_decimal(day_data["temp_max_c"]),
                wind_kph=_decimal(day_data["wind_kph"]),
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
