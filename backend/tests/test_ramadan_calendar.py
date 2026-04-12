"""Tests for Ramadan Calendar helper (Session 119)."""
from __future__ import annotations

from datetime import date

import pytest

from app.services.sotreg.ramadan_calendar import (
    RAMADAN_RANGES,
    get_ramadan_dates,
    is_ramadan,
    ramadan_flag_series,
)


class TestIsRamadan:
    """Tests for is_ramadan function."""

    def test_ramadan_2026_start(self) -> None:
        """Feb 17 2026 is during Ramadan 1447 AH."""
        assert is_ramadan(date(2026, 2, 20)) is True

    def test_ramadan_2026_end(self) -> None:
        """Mar 18 2026 is last day of Ramadan 1447 AH."""
        assert is_ramadan(date(2026, 3, 18)) is True

    def test_non_ramadan_date(self) -> None:
        """June 15 2026 is not during Ramadan."""
        assert is_ramadan(date(2026, 6, 15)) is False

    def test_ramadan_2024(self) -> None:
        """Ramadan 2024 correctly detected."""
        assert is_ramadan(date(2024, 3, 15)) is True
        assert is_ramadan(date(2024, 4, 5)) is True

    def test_before_ramadan_2024(self) -> None:
        """Before Ramadan 2024 returns False."""
        assert is_ramadan(date(2024, 2, 1)) is False

    def test_all_years_covered(self) -> None:
        """Pre-computed ranges cover 2024-2030."""
        years_covered = set()
        for start, end in RAMADAN_RANGES:
            years_covered.add(start.year)
        assert years_covered == {2024, 2025, 2026, 2027, 2028, 2029, 2030}


class TestGetRamadanDates:
    """Tests for get_ramadan_dates function."""

    def test_get_2026_dates(self) -> None:
        """Returns Ramadan dates for 2026."""
        result = get_ramadan_dates(2026)
        assert result is not None
        start, end = result
        assert start.year == 2026
        assert start.month == 2

    def test_out_of_range_year(self) -> None:
        """Returns None for year outside 2024-2030."""
        assert get_ramadan_dates(2035) is None


class TestRamadanFlagSeries:
    """Tests for ramadan_flag_series function."""

    def test_series_length(self) -> None:
        """Series has correct number of entries."""
        flags = ramadan_flag_series(date(2026, 1, 1), 365)
        assert len(flags) == 365

    def test_series_contains_true(self) -> None:
        """Series contains True values during Ramadan."""
        flags = ramadan_flag_series(date(2026, 2, 1), 60)
        assert any(flags)  # Feb-Mar 2026 includes Ramadan

    def test_series_all_false_outside(self) -> None:
        """Series is all False outside Ramadan period."""
        flags = ramadan_flag_series(date(2026, 7, 1), 30)
        assert not any(flags)
