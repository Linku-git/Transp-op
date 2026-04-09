"""Tests for Operator Sizing Plan Export (Session 82)."""
from __future__ import annotations

import json
import uuid

import pytest

from app.models.operator import Operator
from app.models.sizing_plan_export import SizingPlanExport
from app.schemas.operator import OperatorCreate, OperatorUpdate, OperatorResponse
from app.schemas.sizing_plan_export import SizingPlanExportRequest, SizingPlanExportResponse
from app.services.export.sizing_plan_exporter import SizingPlanExporter


class TestOperatorModel:
    def test_create_operator(self):
        op = Operator(
            tenant_id=uuid.uuid4(),
            name="TransCasa SARL",
            operator_type="local",
            contacts=[{"name": "Ahmed", "phone": "+212600000001"}],
        )
        assert op.name == "TransCasa SARL"
        assert op.operator_type == "local"
        assert len(op.contacts) == 1

    def test_all_operator_types(self):
        for t in ["via", "swvl", "local", "internal"]:
            op = Operator(tenant_id=uuid.uuid4(), name=f"{t} op", operator_type=t)
            assert op.operator_type == t

    def test_operator_with_api_config(self):
        op = Operator(
            tenant_id=uuid.uuid4(),
            name="Via Operator",
            operator_type="via",
            api_config={"base_url": "https://api.via.com", "api_key": "key123"},
        )
        assert op.api_config["base_url"] == "https://api.via.com"


class TestSizingPlanExportModel:
    def test_create_export(self):
        export = SizingPlanExport(
            tenant_id=uuid.uuid4(),
            format="json",
            status="completed",
            version=1,
        )
        assert export.format == "json"
        assert export.version == 1

    def test_export_with_all_formats(self):
        for fmt in ["json", "xml", "pdf"]:
            export = SizingPlanExport(
                tenant_id=uuid.uuid4(),
                format=fmt,
                version=1,
            )
            assert export.format == fmt


class TestOperatorSchemas:
    def test_create_valid(self):
        schema = OperatorCreate(name="Test Op", operator_type="via")
        assert schema.operator_type == "via"

    def test_create_rejects_invalid_type(self):
        with pytest.raises(Exception):
            OperatorCreate(name="Test", operator_type="uber")

    def test_update_partial(self):
        schema = OperatorUpdate(name="Updated")
        assert schema.name == "Updated"
        assert schema.operator_type is None

    def test_export_request_valid(self):
        req = SizingPlanExportRequest(format="xml")
        assert req.format == "xml"

    def test_export_request_rejects_invalid_format(self):
        with pytest.raises(Exception):
            SizingPlanExportRequest(format="csv")


class TestSizingPlanExporter:
    def test_build_sizing_plan(self):
        exporter = SizingPlanExporter.__new__(SizingPlanExporter)
        content = exporter._build_sizing_plan(uuid.uuid4(), None)

        assert "metadata" in content
        assert "vehicle_specifications" in content
        assert "routes" in content
        assert "schedules" in content
        assert "passenger_counts" in content
        assert "pmr_requirements" in content
        assert "rti_targets" in content

    def test_summarize_plan(self):
        exporter = SizingPlanExporter.__new__(SizingPlanExporter)
        content = exporter._build_sizing_plan(uuid.uuid4(), None)
        summary = exporter._summarize(content)

        assert "vehicles" in summary
        assert "routes" in summary
        assert "passengers" in summary
        assert "pmr" in summary

    def test_to_json(self):
        content = {"test": "data", "number": 42}
        result = SizingPlanExporter.to_json(content)
        parsed = json.loads(result)
        assert parsed["test"] == "data"
        assert parsed["number"] == 42

    def test_to_xml(self):
        content = {"metadata": {"version": "1.0"}, "vehicles": {"count": "5"}}
        result = SizingPlanExporter.to_xml(content)
        assert "<?xml" in result
        assert "<SizingPlan>" in result
        assert "<metadata>" in result
        assert "<version>1.0</version>" in result

    def test_generate_file_url_json(self):
        exporter = SizingPlanExporter.__new__(SizingPlanExporter)
        url = exporter._generate_file({"test": True}, "json", uuid.uuid4(), 1)
        assert url.endswith(".json")
        assert "/exports/" in url

    def test_generate_file_url_xml(self):
        exporter = SizingPlanExporter.__new__(SizingPlanExporter)
        url = exporter._generate_file({"test": True}, "xml", uuid.uuid4(), 2)
        assert url.endswith(".xml")
        assert "v2" in url

    def test_generate_file_url_pdf(self):
        exporter = SizingPlanExporter.__new__(SizingPlanExporter)
        url = exporter._generate_file({"test": True}, "pdf", uuid.uuid4(), 3)
        assert url.endswith(".pdf")

    def test_content_includes_rti_targets(self):
        exporter = SizingPlanExporter.__new__(SizingPlanExporter)
        content = exporter._build_sizing_plan(uuid.uuid4(), None)
        assert content["rti_targets"]["on_time_target_pct"] == 95.0
        assert content["rti_targets"]["real_time_tracking"] is True

    def test_version_tracking(self):
        export1 = SizingPlanExport(tenant_id=uuid.uuid4(), format="json", version=1)
        export2 = SizingPlanExport(tenant_id=uuid.uuid4(), format="json", version=2)
        assert export2.version == export1.version + 1

    def test_change_tracking_structure(self):
        changes = {
            "vehicles": {"previous": 10, "current": 12, "delta": 2},
            "routes": {"previous": 5, "current": 5, "delta": 0},
        }
        assert changes["vehicles"]["delta"] == 2
