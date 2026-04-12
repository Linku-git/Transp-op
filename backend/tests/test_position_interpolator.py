"""Tests for Position Interpolation service (Session 121)."""
from __future__ import annotations

import math
import pytest

from app.services.sotreg.position_interpolator import (
    GeoPosition,
    calculate_bearing,
    extrapolate_position,
    generate_interpolated_frames,
    haversine_distance,
    interpolate_position,
)


class TestHaversineDistance:
    def test_same_point_zero(self) -> None:
        assert haversine_distance(33.57, -7.59, 33.57, -7.59) == pytest.approx(0, abs=0.1)

    def test_known_distance(self) -> None:
        # Casablanca (33.57, -7.59) to Rabat (34.02, -6.83) ≈ 86 km
        dist = haversine_distance(33.57, -7.59, 34.02, -6.83)
        assert 80_000 < dist < 95_000


class TestBearing:
    def test_north(self) -> None:
        bearing = calculate_bearing(33.0, -7.0, 34.0, -7.0)
        assert bearing == pytest.approx(0.0, abs=1.0)

    def test_east(self) -> None:
        bearing = calculate_bearing(33.0, -7.0, 33.0, -6.0)
        assert bearing == pytest.approx(90.0, abs=2.0)

    def test_south(self) -> None:
        bearing = calculate_bearing(34.0, -7.0, 33.0, -7.0)
        assert bearing == pytest.approx(180.0, abs=1.0)

    def test_range_0_360(self) -> None:
        bearing = calculate_bearing(33.0, -7.0, 33.0, -8.0)
        assert 0 <= bearing < 360


class TestInterpolation:
    def test_fraction_zero_returns_start(self) -> None:
        start = GeoPosition(lat=33.0, lng=-7.0, timestamp=0)
        end = GeoPosition(lat=34.0, lng=-6.0, timestamp=10)
        result = interpolate_position(start, end, 0.0)
        assert result.lat == pytest.approx(33.0)
        assert result.lng == pytest.approx(-7.0)

    def test_fraction_one_returns_end(self) -> None:
        start = GeoPosition(lat=33.0, lng=-7.0, timestamp=0)
        end = GeoPosition(lat=34.0, lng=-6.0, timestamp=10)
        result = interpolate_position(start, end, 1.0)
        assert result.lat == pytest.approx(34.0)
        assert result.lng == pytest.approx(-6.0)

    def test_midpoint(self) -> None:
        start = GeoPosition(lat=33.0, lng=-7.0, timestamp=0)
        end = GeoPosition(lat=35.0, lng=-5.0, timestamp=10)
        result = interpolate_position(start, end, 0.5)
        assert result.lat == pytest.approx(34.0)
        assert result.lng == pytest.approx(-6.0)


class TestExtrapolation:
    def test_zero_speed_no_movement(self) -> None:
        pos = GeoPosition(lat=33.0, lng=-7.0, speed_kmh=0, heading=0, timestamp=100)
        result = extrapolate_position(pos, 5.0)
        assert result.lat == pytest.approx(33.0)
        assert result.lng == pytest.approx(-7.0)

    def test_northward_extrapolation(self) -> None:
        pos = GeoPosition(lat=33.0, lng=-7.0, speed_kmh=36, heading=0, timestamp=100)
        result = extrapolate_position(pos, 10.0)  # 10m/s * 10s = 100m north
        assert result.lat > 33.0
        assert result.lng == pytest.approx(-7.0, abs=0.001)


class TestInterpolatedFrames:
    def test_frame_count(self) -> None:
        start = GeoPosition(lat=33.0, lng=-7.0, timestamp=0)
        end = GeoPosition(lat=34.0, lng=-6.0, timestamp=1.0)
        frames = generate_interpolated_frames(start, end, fps=10)
        assert len(frames) == 11  # 10 intervals + 1

    def test_zero_duration_single_frame(self) -> None:
        start = GeoPosition(lat=33.0, lng=-7.0, timestamp=5)
        end = GeoPosition(lat=34.0, lng=-6.0, timestamp=5)
        frames = generate_interpolated_frames(start, end, fps=10)
        assert len(frames) == 1
