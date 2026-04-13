"""Tests for Financial Reconciliation page."""
from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestFinancialTable:
    """Test 7: Financial table data integrity."""

    def test_financial_data_has_lignes(self) -> None:
        """Financial data contains ligne entries."""
        from services.api_client import TranspopClient

        data = TranspopClient._demo_financial()
        assert "lignes" in data
        assert len(data["lignes"]) == 5

    def test_total_invoiced_is_sum(self) -> None:
        """Total invoiced MAD equals sum of all ligne amounts."""
        from services.api_client import TranspopClient

        data = TranspopClient._demo_financial()
        computed = sum(lg["amount_mad"] for lg in data["lignes"])
        assert data["total_invoiced_mad"] == computed

    def test_disputed_total_correct(self) -> None:
        """Total disputed MAD only counts disputed lignes."""
        from services.api_client import TranspopClient

        data = TranspopClient._demo_financial()
        computed = sum(
            lg["amount_mad"] for lg in data["lignes"] if lg["status"] == "disputed"
        )
        assert data["total_disputed_mad"] == computed


class TestDiscrepancyHighlighting:
    """Test 8: Discrepancy detection between invoiced and actual trips."""

    def test_discrepancy_detection(self) -> None:
        """Lines where invoiced_trips != actual_trips are flagged."""
        from services.api_client import TranspopClient

        data = TranspopClient._demo_financial()
        discrepancies: list[str] = []
        for lg in data["lignes"]:
            if lg["invoiced_trips"] != lg["actual_trips"]:
                discrepancies.append(lg["ligne"])

        # Ligne A1: 320 vs 315, Ligne C3: 250 vs 247, Ligne D4: 200 vs 205
        assert "Ligne A1" in discrepancies
        assert "Ligne C3" in discrepancies
        assert "Ligne D4" in discrepancies
        # Ligne B2: 280 vs 280, Ligne E5: 180 vs 180 -> no discrepancy
        assert "Ligne B2" not in discrepancies
        assert "Ligne E5" not in discrepancies

    def test_all_statuses_valid(self) -> None:
        """All ligne statuses are one of paid, pending, disputed."""
        from services.api_client import TranspopClient

        data = TranspopClient._demo_financial()
        valid_statuses = {"paid", "pending", "disputed"}
        for lg in data["lignes"]:
            assert lg["status"] in valid_statuses
