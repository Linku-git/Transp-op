from __future__ import annotations

import uuid
from datetime import date, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from tests.conftest import login_as_admin


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_site(
    client: AsyncClient, token: str, name: str = "Weather Site"
) -> str:
    code = f"WS-{uuid.uuid4().hex[:6]}"
    resp = await client.post(
        "/api/v1/sites/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": code,
            "name": name,
            "address": "123 Rue Meteo",
            "city": "Casablanca",
            "lat": 33.57,
            "lng": -7.59,
        },
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def _mock_owm_response() -> list[dict]:
    """Build a fake OpenWeatherMap 5-day/3-hour response with rain on day 1."""
    today = date.today()
    intervals: list[dict] = []

    for day_offset in range(3):
        day = today + timedelta(days=day_offset)
        for hour in range(0, 24, 3):
            interval: dict = {
                "dt_txt": f"{day.isoformat()} {hour:02d}:00:00",
                "main": {
                    "temp_min": 15.0 + day_offset,
                    "temp_max": 25.0 + day_offset,
                },
                "wind": {"speed": 3.5},
                "weather": [{"main": "Clear", "description": "clear sky"}],
            }
            # Add rain on day 0
            if day_offset == 0:
                interval["rain"] = {"3h": 2.5}
                interval["weather"] = [
                    {"main": "Rain", "description": "moderate rain"}
                ]
            intervals.append(interval)

    return intervals


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fetch_forecast(client: AsyncClient) -> None:
    """Mocked API returns valid forecast intervals."""
    from unittest.mock import MagicMock

    mock_intervals = _mock_owm_response()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"list": mock_intervals}
    mock_response.raise_for_status = MagicMock()

    with patch("app.services.weather.settings") as mock_settings:
        mock_settings.weather_api_key = "test-key"
        mock_settings.weather_api_url = "https://api.openweathermap.org/data/2.5/forecast"

        with patch("app.services.weather.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            from app.services.weather import fetch_forecast_from_api

            result = await fetch_forecast_from_api(33.57, -7.59)

    assert result is not None
    assert len(result) > 0


@pytest.mark.asyncio
async def test_store_snapshot(client: AsyncClient) -> None:
    """POST refresh stores forecasts in database, retrievable via GET."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    mock_intervals = _mock_owm_response()

    with patch(
        "app.services.weather.fetch_forecast_from_api",
        return_value=mock_intervals,
    ):
        resp = await client.post(
            f"/api/v1/weather/{site_id}/refresh",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["forecasts_updated"] >= 1
    assert data["site_id"] == site_id


@pytest.mark.asyncio
async def test_get_forecasts(client: AsyncClient) -> None:
    """GET returns stored forecasts with correct structure."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    mock_intervals = _mock_owm_response()

    with patch(
        "app.services.weather.fetch_forecast_from_api",
        return_value=mock_intervals,
    ):
        await client.post(
            f"/api/v1/weather/{site_id}/refresh",
            headers={"Authorization": f"Bearer {token}"},
        )

    resp = await client.get(
        f"/api/v1/weather/{site_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    forecasts = resp.json()
    assert isinstance(forecasts, list)
    assert len(forecasts) >= 1

    fc = forecasts[0]
    assert "date" in fc
    assert "condition_summary" in fc
    assert "temp_min_c" in fc
    assert "temp_max_c" in fc
    assert fc["site_id"] == site_id


@pytest.mark.asyncio
async def test_scenario_suggestions(client: AsyncClient) -> None:
    """Rain forecast suggests rain scenario condition."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    mock_intervals = _mock_owm_response()

    with patch(
        "app.services.weather.fetch_forecast_from_api",
        return_value=mock_intervals,
    ):
        await client.post(
            f"/api/v1/weather/{site_id}/refresh",
            headers={"Authorization": f"Bearer {token}"},
        )

    resp = await client.get(
        f"/api/v1/weather/{site_id}/suggestions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["site_id"] == site_id
    assert len(data["suggestions"]) >= 1

    # Day 0 has rain in mock data
    rain_suggestions = [
        s for s in data["suggestions"] if s["suggested_condition_type"] == "rain"
    ]
    assert len(rain_suggestions) >= 1


@pytest.mark.asyncio
async def test_refresh_all_sites(client: AsyncClient) -> None:
    """POST refresh-all refreshes all tenant sites."""
    token = await login_as_admin(client)
    site_id_1 = await _create_site(client, token, name="Site Alpha")
    site_id_2 = await _create_site(client, token, name="Site Beta")
    mock_intervals = _mock_owm_response()

    with patch(
        "app.services.weather.fetch_forecast_from_api",
        return_value=mock_intervals,
    ):
        resp = await client.post(
            "/api/v1/weather/refresh-all",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["sites_refreshed"] >= 2
    assert data["total_forecasts_updated"] >= 4
    assert data["errors"] == []
