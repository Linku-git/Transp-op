"""Cegid export formatter."""
from __future__ import annotations

import csv
import io
from datetime import datetime, timezone

CEGID_HEADERS = [
    "CodeJournal", "DateEcriture", "NumPiece", "NumCompte",
    "LibelleEcriture", "MontantDebit", "MontantCredit",
    "CodeAnalytique", "NumFacture",
]


class CegidFormatter:
    """Generate Cegid-compatible CSV."""

    @staticmethod
    def format(financial_data: dict) -> str:
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow(CEGID_HEADERS)

        journal = "OD"
        date = datetime.now(timezone.utc).strftime("%d%m%Y")
        piece = financial_data.get("doc_number", "TRP0001")

        for entry in financial_data.get("tco_entries", []):
            amount = entry.get("amount", 0)
            writer.writerow([
                journal, date, piece,
                entry.get("account", "622000"),
                entry.get("description", "Transport TCO"),
                f"{amount:.2f}" if amount >= 0 else "0.00",
                f"{abs(amount):.2f}" if amount < 0 else "0.00",
                entry.get("cost_center", ""),
                entry.get("reference", ""),
            ])

        for entry in financial_data.get("roi_entries", []):
            amount = entry.get("amount", 0)
            writer.writerow([
                journal, date, piece,
                entry.get("account", "628000"),
                entry.get("description", "Transport ROI"),
                f"{amount:.2f}" if amount >= 0 else "0.00",
                f"{abs(amount):.2f}" if amount < 0 else "0.00",
                entry.get("cost_center", ""),
                entry.get("reference", ""),
            ])

        if "cost_per_trip" in financial_data:
            cpt = financial_data["cost_per_trip"]
            writer.writerow([
                journal, date, piece, "622100",
                f"Cout trajet {cpt.get('cost_per_trip', 0):.2f}",
                f"{cpt.get('total_cost', 0):.2f}", "0.00", "", "",
            ])

        if "investment_comparator" in financial_data:
            inv = financial_data["investment_comparator"]
            writer.writerow([
                journal, date, piece, "620000",
                f"Investissement {inv.get('recommended_model', '')}",
                f"{inv.get('annual_cost', 0):.2f}", "0.00", "", "",
            ])

        return output.getvalue()

    @staticmethod
    def content_type() -> str:
        return "text/csv"

    @staticmethod
    def file_extension() -> str:
        return "csv"
