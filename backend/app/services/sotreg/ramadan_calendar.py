"""Ramadan Calendar — Hijri calendar lookup for Morocco seasonality.

Provides binary is_ramadan flag for any date in the 2024-2030 range.
Uses pre-computed Ramadan date ranges for reliability when
hijri-converter is unavailable.

Session 119 — CDC SOTREG v5.0 Module M8/ML.
"""
from __future__ import annotations

import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)

# Pre-computed Ramadan start dates (approximate Gregorian equivalents).
# Ramadan lasts ~29-30 days. Dates may vary ±1 day based on moon sighting.
# Source: Islamic calendar projections for Morocco.
RAMADAN_RANGES: list[tuple[date, date]] = [
    (date(2024, 3, 11), date(2024, 4, 9)),    # 1445 AH
    (date(2025, 2, 28), date(2025, 3, 29)),    # 1446 AH
    (date(2026, 2, 17), date(2026, 3, 18)),    # 1447 AH
    (date(2027, 2, 7), date(2027, 3, 8)),      # 1448 AH
    (date(2028, 1, 27), date(2028, 2, 25)),    # 1449 AH
    (date(2029, 1, 15), date(2029, 2, 13)),    # 1450 AH
    (date(2030, 1, 5), date(2030, 2, 3)),      # 1451 AH
]


def is_ramadan(d: date) -> bool:
    """Check if a given date falls within Ramadan.

    First attempts to use hijri-converter for precise calculation.
    Falls back to pre-computed ranges if the library is unavailable.

    Args:
        d: Date to check.

    Returns:
        True if the date is during Ramadan.
    """
    try:
        from hijri_converter import Gregorian
        hijri = Gregorian(d.year, d.month, d.day).to_hijri()
        return hijri.month == 9  # Ramadan is month 9
    except ImportError:
        pass

    # Fallback: check pre-computed ranges
    for start, end in RAMADAN_RANGES:
        if start <= d <= end:
            return True
    return False


def get_ramadan_dates(year: int) -> tuple[date, date] | None:
    """Get the Ramadan start and end dates for a given Gregorian year.

    Args:
        year: Gregorian year (2024-2030).

    Returns:
        Tuple of (start_date, end_date) or None if year not in range.
    """
    for start, end in RAMADAN_RANGES:
        if start.year == year or end.year == year:
            return start, end
    return None


def ramadan_flag_series(start_date: date, num_days: int) -> list[bool]:
    """Generate a series of Ramadan flags for consecutive days.

    Args:
        start_date: First date in the series.
        num_days: Number of days to generate.

    Returns:
        List of booleans, one per day.
    """
    return [is_ramadan(start_date + timedelta(days=i)) for i in range(num_days)]
