from __future__ import annotations

import pytest

from app.services.sotreg.zfe_service import (
    ZFEResult,
    _check_local_registry,
    _haversine_km,
    _is_in_france,
    check_zfe_compliance,
    batch_check_zfe,
)


# ---------------------------------------------------------------------------
# Unit tests — haversine
# ---------------------------------------------------------------------------


def test_haversine_same_point() -> None:
    assert _haversine_km(33.57, -7.59, 33.57, -7.59) == pytest.approx(0.0, abs=0.01)


def test_haversine_known_distance() -> None:
    # Casablanca to Rabat: ~86 km
    dist = _haversine_km(33.5731, -7.5898, 33.9911, -6.8498)
    assert 80 < dist < 95


# ---------------------------------------------------------------------------
# Unit tests — France bounding box
# ---------------------------------------------------------------------------


def test_is_in_france_paris() -> None:
    assert _is_in_france(48.8566, 2.3522) is True


def test_is_in_france_casablanca() -> None:
    assert _is_in_france(33.5731, -7.5898) is False


# ---------------------------------------------------------------------------
# Unit tests — local ZFE registry
# ---------------------------------------------------------------------------


def test_local_registry_casablanca_centre() -> None:
    result = _check_local_registry(33.5731, -7.5898)
    assert result.is_in_zfe is True
    assert result.zone_name == "Casablanca Centre"
    assert result.restriction_level == "moderate"


def test_local_registry_outside_zfe() -> None:
    # Marrakech — not in any local ZFE zone
    result = _check_local_registry(31.6295, -7.9811)
    assert result.is_in_zfe is False
    assert result.zone_name is None


def test_local_registry_rabat() -> None:
    result = _check_local_registry(33.9911, -6.8498)
    assert result.is_in_zfe is True
    assert result.zone_name == "Rabat Agdal"
    assert result.restriction_level == "low"


def test_local_registry_tanger() -> None:
    result = _check_local_registry(35.7595, -5.8340)
    assert result.is_in_zfe is True
    assert result.zone_name == "Tanger Medina"


# ---------------------------------------------------------------------------
# Unit tests — ZFEResult dataclass
# ---------------------------------------------------------------------------


def test_zfe_result_defaults() -> None:
    result = ZFEResult(is_in_zfe=False)
    assert result.is_in_zfe is False
    assert result.zone_name is None
    assert result.restriction_level is None
    assert result.allowed_crit_air is None
    assert result.checked_at is not None


# ---------------------------------------------------------------------------
# Async tests — check_zfe_compliance (uses local fallback for Morocco)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_zfe_compliance_casablanca() -> None:
    """Casablanca centre should be detected via local registry."""
    result = await check_zfe_compliance(33.5731, -7.5898)
    assert result.is_in_zfe is True
    assert result.zone_name == "Casablanca Centre"


@pytest.mark.asyncio
async def test_check_zfe_compliance_outside() -> None:
    """Marrakech should not be in any ZFE."""
    result = await check_zfe_compliance(31.6295, -7.9811)
    assert result.is_in_zfe is False


@pytest.mark.asyncio
async def test_batch_check_zfe_empty() -> None:
    results = await batch_check_zfe([])
    assert results == []


@pytest.mark.asyncio
async def test_batch_check_zfe_multiple() -> None:
    coords = [
        (33.5731, -7.5898),   # Casablanca — in ZFE
        (31.6295, -7.9811),   # Marrakech — not in ZFE
        (33.9911, -6.8498),   # Rabat — in ZFE
    ]
    results = await batch_check_zfe(coords)
    assert len(results) == 3
    assert results[0].is_in_zfe is True
    assert results[1].is_in_zfe is False
    assert results[2].is_in_zfe is True
