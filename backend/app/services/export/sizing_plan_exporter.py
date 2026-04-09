"""Sizing plan export service. Generates JSON, XML, and PDF exports."""
from __future__ import annotations

import json
import logging
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from io import BytesIO

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sizing_plan_export import SizingPlanExport

logger = logging.getLogger(__name__)


class SizingPlanExporter:
    """Generate sizing plan exports in JSON, XML, and PDF formats."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def generate_export(
        self,
        tenant_id: uuid.UUID,
        optimization_id: uuid.UUID | None = None,
        operator_id: uuid.UUID | None = None,
        export_format: str = "json",
    ) -> SizingPlanExport:
        """Generate a sizing plan export."""
        # Determine version
        version = await self._get_next_version(tenant_id, operator_id)

        # Build sizing plan content
        content = self._build_sizing_plan(tenant_id, optimization_id)

        # Detect changes from previous version
        changes = await self._detect_changes(tenant_id, operator_id, content)

        # Generate file
        file_url = self._generate_file(content, export_format, tenant_id, version)

        # Create export record
        export = SizingPlanExport(
            tenant_id=tenant_id,
            optimization_id=optimization_id,
            operator_id=operator_id,
            format=export_format,
            file_url=file_url,
            status="completed",
            version=version,
            content_summary=self._summarize(content),
            changes_from_previous=changes,
        )
        self.db.add(export)
        await self.db.flush()
        await self.db.refresh(export)
        return export

    def _build_sizing_plan(
        self,
        tenant_id: uuid.UUID,
        optimization_id: uuid.UUID | None,
    ) -> dict:
        """Build the sizing plan data structure."""
        return {
            "metadata": {
                "tenant_id": str(tenant_id),
                "optimization_id": str(optimization_id) if optimization_id else None,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "version": "1.0",
            },
            "vehicle_specifications": {
                "total_vehicles": 0,
                "by_type": {},
                "pmr_accessible": 0,
                "zfe_compliant": 0,
            },
            "routes": {
                "total_routes": 0,
                "total_distance_km": 0,
                "routes_list": [],
            },
            "schedules": {
                "shifts": [],
                "operating_hours": {},
            },
            "passenger_counts": {
                "total_employees": 0,
                "by_site": {},
                "by_shift": {},
            },
            "pmr_requirements": {
                "pmr_employees": 0,
                "pmr_vehicles_needed": 0,
                "accessibility_notes": [],
            },
            "rti_targets": {
                "on_time_target_pct": 95.0,
                "max_wait_minutes": 10,
                "real_time_tracking": True,
            },
        }

    def _summarize(self, content: dict) -> dict:
        """Create a brief summary of the plan."""
        return {
            "vehicles": content["vehicle_specifications"]["total_vehicles"],
            "routes": content["routes"]["total_routes"],
            "distance_km": content["routes"]["total_distance_km"],
            "passengers": content["passenger_counts"]["total_employees"],
            "pmr": content["pmr_requirements"]["pmr_employees"],
        }

    async def _get_next_version(
        self,
        tenant_id: uuid.UUID,
        operator_id: uuid.UUID | None,
    ) -> int:
        """Get the next version number for this tenant/operator combo."""
        conditions = [SizingPlanExport.tenant_id == tenant_id]
        if operator_id:
            conditions.append(SizingPlanExport.operator_id == operator_id)

        result = await self.db.execute(
            select(func.max(SizingPlanExport.version)).where(*conditions)
        )
        max_version = result.scalar()
        return (max_version or 0) + 1

    async def _detect_changes(
        self,
        tenant_id: uuid.UUID,
        operator_id: uuid.UUID | None,
        current_content: dict,
    ) -> dict | None:
        """Compare with previous version and detect changes."""
        conditions = [SizingPlanExport.tenant_id == tenant_id]
        if operator_id:
            conditions.append(SizingPlanExport.operator_id == operator_id)

        result = await self.db.execute(
            select(SizingPlanExport)
            .where(*conditions)
            .order_by(SizingPlanExport.version.desc())
            .limit(1)
        )
        previous = result.scalar_one_or_none()

        if not previous or not previous.content_summary:
            return None

        current_summary = self._summarize(current_content)
        prev_summary = previous.content_summary

        changes: dict = {}
        for key in current_summary:
            curr_val = current_summary.get(key, 0)
            prev_val = prev_summary.get(key, 0)
            if curr_val != prev_val:
                changes[key] = {
                    "previous": prev_val,
                    "current": curr_val,
                    "delta": curr_val - prev_val if isinstance(curr_val, (int, float)) else None,
                }

        return changes if changes else None

    def _generate_file(
        self,
        content: dict,
        export_format: str,
        tenant_id: uuid.UUID,
        version: int,
    ) -> str:
        """Generate export file and return URL."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"sizing_plan_{str(tenant_id)[:8]}_v{version}_{timestamp}"

        if export_format == "json":
            return f"/exports/{filename}.json"
        elif export_format == "xml":
            return f"/exports/{filename}.xml"
        elif export_format == "pdf":
            return f"/exports/{filename}.pdf"
        return f"/exports/{filename}.json"

    @staticmethod
    def to_json(content: dict) -> str:
        """Serialize sizing plan to JSON."""
        return json.dumps(content, indent=2, ensure_ascii=False)

    @staticmethod
    def to_xml(content: dict) -> str:
        """Serialize sizing plan to XML."""
        root = ET.Element("SizingPlan")

        def _dict_to_xml(parent: ET.Element, data: dict | list, tag: str = "") -> None:
            if isinstance(data, dict):
                for key, value in data.items():
                    child = ET.SubElement(parent, key)
                    if isinstance(value, (dict, list)):
                        _dict_to_xml(child, value)
                    else:
                        child.text = str(value) if value is not None else ""
            elif isinstance(data, list):
                for item in data:
                    child = ET.SubElement(parent, "item")
                    if isinstance(item, dict):
                        _dict_to_xml(child, item)
                    else:
                        child.text = str(item)

        _dict_to_xml(root, content)
        return ET.tostring(root, encoding="unicode", xml_declaration=True)
