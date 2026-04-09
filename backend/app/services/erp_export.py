"""ERP financial data export service."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from app.services.erp_formats import FORMATTERS

logger = logging.getLogger(__name__)


class ERPExportService:
    """Generate financial exports in ERP-compatible formats."""

    def generate_export(
        self,
        target_system: str,
        financial_data: dict,
    ) -> tuple[str, str, str]:
        """Generate export file content.

        Args:
            target_system: sap_fi, sage, or cegid
            financial_data: Dict with tco_entries, roi_entries, cost_per_trip, investment_comparator

        Returns:
            Tuple of (content, content_type, file_extension)
        """
        formatter_cls = FORMATTERS.get(target_system)
        if not formatter_cls:
            raise ValueError(f"Unknown target system: {target_system}")

        content = formatter_cls.format(financial_data)
        return content, formatter_cls.content_type(), formatter_cls.file_extension()

    @staticmethod
    def build_financial_data(
        tco_entries: list[dict] | None = None,
        roi_entries: list[dict] | None = None,
        cost_per_trip: dict | None = None,
        investment_comparator: dict | None = None,
        company_code: str = "1000",
        currency: str = "MAD",
    ) -> dict:
        """Build the financial data structure for export."""
        return {
            "company_code": company_code,
            "currency": currency,
            "doc_number": f"TRP{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}",
            "tco_entries": tco_entries or [],
            "roi_entries": roi_entries or [],
            "cost_per_trip": cost_per_trip,
            "investment_comparator": investment_comparator,
        }
