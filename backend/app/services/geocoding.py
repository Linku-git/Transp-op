from __future__ import annotations

import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)

# Nominatim requires a meaningful User-Agent to comply with their usage policy.
_USER_AGENT = "Transpop/0.1 (employee-transport-optimization)"
_NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"

# Nominatim usage policy: max 1 request per second.
_RATE_LIMIT_SECONDS = 1.1


async def geocode_address(address: str) -> tuple[float, float] | None:
    """Geocode a street address using the Nominatim (OpenStreetMap) API.

    Returns ``(lat, lng)`` on success, or ``None`` if the address could not
    be resolved or an error occurred.
    """
    if not address or not address.strip():
        return None

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{_NOMINATIM_BASE_URL}/search",
                params={"q": address, "format": "json", "limit": 1},
                headers={"User-Agent": _USER_AGENT},
            )
            response.raise_for_status()

            results = response.json()
            if not results:
                logger.info("Geocoding returned no results for: %s", address)
                return None

            lat = float(results[0]["lat"])
            lng = float(results[0]["lon"])
            logger.debug("Geocoded '%s' -> (%s, %s)", address, lat, lng)
            return (lat, lng)

    except httpx.HTTPStatusError as exc:
        logger.warning(
            "Geocoding HTTP error for '%s': %s %s",
            address,
            exc.response.status_code,
            exc.response.text[:200],
        )
        return None
    except (httpx.RequestError, ValueError, KeyError, IndexError) as exc:
        logger.warning("Geocoding failed for '%s': %s", address, exc)
        return None


async def reverse_geocode(lat: float, lng: float) -> str | None:
    """Reverse-geocode GPS coordinates to a human-readable address.

    Returns the display name string on success, or ``None`` on failure.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{_NOMINATIM_BASE_URL}/reverse",
                params={"lat": lat, "lon": lng, "format": "json"},
                headers={"User-Agent": _USER_AGENT},
            )
            response.raise_for_status()

            data = response.json()
            display_name: str | None = data.get("display_name")
            if display_name:
                logger.debug(
                    "Reverse-geocoded (%s, %s) -> '%s'", lat, lng, display_name
                )
            return display_name

    except httpx.HTTPStatusError as exc:
        logger.warning(
            "Reverse geocoding HTTP error for (%s, %s): %s %s",
            lat,
            lng,
            exc.response.status_code,
            exc.response.text[:200],
        )
        return None
    except (httpx.RequestError, ValueError, KeyError) as exc:
        logger.warning("Reverse geocoding failed for (%s, %s): %s", lat, lng, exc)
        return None


async def batch_geocode(
    addresses: list[str],
) -> list[tuple[float, float] | None]:
    """Geocode multiple addresses sequentially, respecting Nominatim rate limits.

    Returns a list of ``(lat, lng)`` tuples (or ``None`` for failures),
    in the same order as the input addresses.
    """
    results: list[tuple[float, float] | None] = []

    for idx, address in enumerate(addresses):
        result = await geocode_address(address)
        results.append(result)

        # Respect Nominatim rate limit (1 req/sec) — skip delay after last item
        if idx < len(addresses) - 1:
            await asyncio.sleep(_RATE_LIMIT_SECONDS)

    return results
