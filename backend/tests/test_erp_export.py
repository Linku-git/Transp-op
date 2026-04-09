"""Tests for ERP Finance Export (Session 85)."""
from __future__ import annotations

import csv
import io

import pytest

from app.services.erp_export import ERPExportService
from app.services.erp_formats.sap_fi_formatter import SAPFIFormatter, SAP_FI_HEADERS
from app.services.erp_formats.sage_formatter import SageFormatter, SAGE_HEADERS
from app.services.erp_formats.cegid_formatter import CegidFormatter, CEGID_HEADERS
from app.schemas.financial_export import FinancialExportRequest


SAMPLE_DATA = {
    "company_code": "1000",
    "currency": "MAD",
    "doc_number": "TRP202604",
    "tco_entries": [
        {"account": "6200000", "amount": 150000, "description": "TCO Flotte", "cost_center": "CC100"},
        {"account": "6200100", "amount": 25000, "description": "Maintenance", "cost_center": "CC100"},
    ],
    "roi_entries": [
        {"account": "6300000", "amount": -45000, "description": "Économies absentéisme"},
    ],
    "cost_per_trip": {"cost_per_trip": 12.50, "total_cost": 375000},
    "investment_comparator": {"recommended_model": "OPEX", "annual_cost": 180000},
}


class TestSAPFIFormatter:
    def test_generates_csv_with_headers(self):
        result = SAPFIFormatter.format(SAMPLE_DATA)
        reader = csv.reader(io.StringIO(result), delimiter=";")
        headers = next(reader)
        assert headers == SAP_FI_HEADERS

    def test_includes_tco_entries(self):
        result = SAPFIFormatter.format(SAMPLE_DATA)
        assert "TCO Flotte" in result
        assert "150000.00" in result

    def test_includes_roi_entries(self):
        result = SAPFIFormatter.format(SAMPLE_DATA)
        assert "Économies absentéisme" in result

    def test_includes_cost_per_trip(self):
        result = SAPFIFormatter.format(SAMPLE_DATA)
        assert "375000.00" in result

    def test_content_type(self):
        assert SAPFIFormatter.content_type() == "text/csv"

    def test_file_extension(self):
        assert SAPFIFormatter.file_extension() == "csv"


class TestSageFormatter:
    def test_generates_csv_with_headers(self):
        result = SageFormatter.format(SAMPLE_DATA)
        reader = csv.reader(io.StringIO(result), delimiter=";")
        headers = next(reader)
        assert headers == SAGE_HEADERS

    def test_includes_tco_entries(self):
        result = SageFormatter.format(SAMPLE_DATA)
        assert "TCO Flotte" in result
        assert "150000.00" in result

    def test_includes_roi_entries(self):
        result = SageFormatter.format(SAMPLE_DATA)
        assert "absentéisme" in result or "absent" in result

    def test_includes_investment_comparator(self):
        result = SageFormatter.format(SAMPLE_DATA)
        assert "OPEX" in result

    def test_includes_cost_per_trip(self):
        result = SageFormatter.format(SAMPLE_DATA)
        assert "12.50" in result


class TestCegidFormatter:
    def test_generates_csv_with_headers(self):
        result = CegidFormatter.format(SAMPLE_DATA)
        reader = csv.reader(io.StringIO(result), delimiter=";")
        headers = next(reader)
        assert headers == CEGID_HEADERS

    def test_includes_tco_entries(self):
        result = CegidFormatter.format(SAMPLE_DATA)
        assert "TCO Flotte" in result
        assert "150000.00" in result

    def test_includes_investment_comparator(self):
        result = CegidFormatter.format(SAMPLE_DATA)
        assert "OPEX" in result


class TestERPExportService:
    def test_generate_sap_fi(self):
        service = ERPExportService()
        content, ctype, ext = service.generate_export("sap_fi", SAMPLE_DATA)
        assert "BUKRS" in content
        assert ctype == "text/csv"
        assert ext == "csv"

    def test_generate_sage(self):
        service = ERPExportService()
        content, ctype, ext = service.generate_export("sage", SAMPLE_DATA)
        assert "Journal" in content
        assert ctype == "text/csv"

    def test_generate_cegid(self):
        service = ERPExportService()
        content, ctype, ext = service.generate_export("cegid", SAMPLE_DATA)
        assert "CodeJournal" in content
        assert ctype == "text/csv"

    def test_unknown_system_raises(self):
        service = ERPExportService()
        with pytest.raises(ValueError, match="Unknown target system"):
            service.generate_export("oracle", SAMPLE_DATA)

    def test_build_financial_data(self):
        data = ERPExportService.build_financial_data(
            tco_entries=[{"amount": 100}],
            currency="EUR",
        )
        assert data["currency"] == "EUR"
        assert len(data["tco_entries"]) == 1
        assert data["doc_number"].startswith("TRP")

    def test_data_integrity(self):
        """Exported values match source data."""
        service = ERPExportService()
        content, _, _ = service.generate_export("sap_fi", SAMPLE_DATA)
        assert "150000.00" in content  # TCO entry amount
        assert "25000.00" in content   # Maintenance amount
        assert "45000.00" in content   # ROI absolute value


class TestFinancialExportSchema:
    def test_valid_request(self):
        req = FinancialExportRequest(target_system="sap_fi")
        assert req.target_system == "sap_fi"

    def test_rejects_invalid_system(self):
        with pytest.raises(Exception):
            FinancialExportRequest(target_system="quickbooks")

    def test_defaults(self):
        req = FinancialExportRequest(target_system="sage")
        assert req.company_code == "1000"
        assert req.currency == "MAD"
