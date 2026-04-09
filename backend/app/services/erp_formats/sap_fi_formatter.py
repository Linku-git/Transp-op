"""SAP FI-compatible CSV export formatter."""
from __future__ import annotations

import csv
import io
from datetime import datetime, timezone

SAP_FI_HEADERS = [
    "BUKRS", "BELNR", "GJAHR", "BLDAT", "BUDAT", "BLART", "WAERS",
    "HKONT", "WRBTR", "SHKZG", "SGTXT", "KOSTL", "ZUONR",
]


class SAPFIFormatter:
    """Generate SAP FI-compliant CSV for journal entries."""

    @staticmethod
    def format(financial_data: dict) -> str:
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow(SAP_FI_HEADERS)

        company_code = financial_data.get("company_code", "1000")
        year = datetime.now(timezone.utc).strftime("%Y")
        posting_date = datetime.now(timezone.utc).strftime("%d.%m.%Y")
        currency = financial_data.get("currency", "MAD")
        doc_number = financial_data.get("doc_number", "0000000001")

        # TCO entries
        for entry in financial_data.get("tco_entries", []):
            writer.writerow([
                company_code, doc_number, year, posting_date, posting_date,
                "SA", currency,
                entry.get("account", "6200000"),
                f"{entry.get('amount', 0):.2f}",
                "S" if entry.get("amount", 0) >= 0 else "H",
                entry.get("description", "Transport TCO"),
                entry.get("cost_center", ""),
                entry.get("reference", ""),
            ])

        # ROI entries
        for entry in financial_data.get("roi_entries", []):
            writer.writerow([
                company_code, doc_number, year, posting_date, posting_date,
                "SA", currency,
                entry.get("account", "6300000"),
                f"{entry.get('amount', 0):.2f}",
                "S" if entry.get("amount", 0) >= 0 else "H",
                entry.get("description", "Transport ROI"),
                entry.get("cost_center", ""),
                entry.get("reference", ""),
            ])

        # Cost per trip
        if "cost_per_trip" in financial_data:
            cpt = financial_data["cost_per_trip"]
            writer.writerow([
                company_code, doc_number, year, posting_date, posting_date,
                "SA", currency,
                "6200100",
                f"{cpt.get('total_cost', 0):.2f}",
                "S", f"Coût/trajet: {cpt.get('cost_per_trip', 0):.2f} {currency}",
                "", "",
            ])

        return output.getvalue()

    @staticmethod
    def content_type() -> str:
        return "text/csv"

    @staticmethod
    def file_extension() -> str:
        return "csv"
