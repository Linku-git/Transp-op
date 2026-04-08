"""Tests for LMS Integration (Session 74)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from app.models.training_module import TrainingModule
from app.schemas.training_module import (
    TrainingModuleCreate,
    TrainingModuleResponse,
    CompletionRecord,
    SyncRequest,
    SyncResult,
    WebhookPayload,
)
from app.services.lms import get_connector, CONNECTORS
from app.services.lms.base_connector import LMSCourse, LMSCompletion


class TestTrainingModuleModel:
    def test_create_training_module(self):
        module = TrainingModule(
            tenant_id=uuid.uuid4(),
            content_id=uuid.uuid4(),
            lms_provider="cornerstone",
            lms_external_id="CST-001",
            duration_minutes=30,
            is_mandatory=True,
            certification_name="Sécurité routière",
        )
        assert module.lms_provider == "cornerstone"
        assert module.lms_external_id == "CST-001"
        assert module.duration_minutes == 30
        assert module.is_mandatory is True
        assert module.certification_name == "Sécurité routière"

    def test_module_with_metadata(self):
        module = TrainingModule(
            tenant_id=uuid.uuid4(),
            content_id=uuid.uuid4(),
            lms_provider="360learning",
            lms_external_id="360L-042",
            lms_metadata={"category": "safety", "level": "beginner"},
        )
        assert module.lms_metadata["category"] == "safety"

    def test_module_providers(self):
        for provider in ["cornerstone", "360learning", "talentlms"]:
            module = TrainingModule(
                tenant_id=uuid.uuid4(),
                content_id=uuid.uuid4(),
                lms_provider=provider,
                lms_external_id=f"{provider}-001",
            )
            assert module.lms_provider == provider


class TestTrainingModuleSchemas:
    def test_create_schema_valid(self):
        schema = TrainingModuleCreate(
            content_id=uuid.uuid4(),
            lms_provider="cornerstone",
            lms_external_id="CST-001",
            duration_minutes=45,
            is_mandatory=True,
        )
        assert schema.lms_provider == "cornerstone"

    def test_create_rejects_invalid_provider(self):
        with pytest.raises(Exception):
            TrainingModuleCreate(
                content_id=uuid.uuid4(),
                lms_provider="invalid",
                lms_external_id="X-001",
            )

    def test_sync_request_valid(self):
        req = SyncRequest(provider="360learning")
        assert req.provider == "360learning"

    def test_sync_request_rejects_invalid(self):
        with pytest.raises(Exception):
            SyncRequest(provider="unknown")

    def test_sync_result(self):
        result = SyncResult(provider="cornerstone", imported=5, exported=3)
        assert result.imported == 5
        assert result.exported == 3
        assert result.errors == []

    def test_completion_record(self):
        record = CompletionRecord(
            employee_id=uuid.uuid4(),
            content_id=uuid.uuid4(),
            completed_at=datetime.now(timezone.utc),
            quiz_score=85.0,
        )
        assert record.quiz_score == 85.0

    def test_webhook_payload(self):
        payload = WebhookPayload(
            provider="talentlms",
            event_type="completion",
            lms_external_id="TLM-101",
            employee_external_id="emp-42",
            score=92.5,
        )
        assert payload.event_type == "completion"
        assert payload.score == 92.5


class TestLMSConnectors:
    def test_connector_registry(self):
        assert "cornerstone" in CONNECTORS
        assert "360learning" in CONNECTORS
        assert "talentlms" in CONNECTORS

    def test_get_connector_valid(self):
        connector = get_connector("cornerstone")
        assert connector.provider_name == "cornerstone"

    def test_get_connector_invalid(self):
        with pytest.raises(ValueError, match="Unknown LMS provider"):
            get_connector("unknown_lms")

    def test_get_connector_360learning(self):
        connector = get_connector("360learning")
        assert connector.provider_name == "360learning"

    def test_get_connector_talentlms(self):
        connector = get_connector("talentlms")
        assert connector.provider_name == "talentlms"

    @pytest.mark.asyncio
    async def test_cornerstone_fetch_catalog(self):
        connector = get_connector("cornerstone")
        courses = await connector.fetch_catalog()
        assert isinstance(courses, list)

    @pytest.mark.asyncio
    async def test_cornerstone_export_completion(self):
        connector = get_connector("cornerstone")
        completion = LMSCompletion(
            external_id="CST-001",
            employee_external_id="emp-1",
            completed_at="2026-04-09T10:00:00Z",
            score=85.0,
        )
        result = await connector.export_completion(completion)
        assert result is True

    @pytest.mark.asyncio
    async def test_cornerstone_webhook(self):
        connector = get_connector("cornerstone")
        result = await connector.handle_webhook({
            "event_type": "completion",
            "course_id": "CST-001",
            "user_id": "emp-42",
            "completed_at": "2026-04-09T10:00:00Z",
            "score": 90.0,
        })
        assert result is not None
        assert result.external_id == "CST-001"
        assert result.score == 90.0

    @pytest.mark.asyncio
    async def test_webhook_ignores_non_completion(self):
        connector = get_connector("cornerstone")
        result = await connector.handle_webhook({
            "event_type": "enrollment",
            "course_id": "CST-001",
        })
        assert result is None

    @pytest.mark.asyncio
    async def test_360learning_webhook(self):
        connector = get_connector("360learning")
        result = await connector.handle_webhook({
            "event_type": "completion",
            "program_id": "360L-001",
            "learner_id": "emp-10",
            "completed_at": "2026-04-09T10:00:00Z",
        })
        assert result is not None
        assert result.external_id == "360L-001"


class TestLMSDataClasses:
    def test_lms_course(self):
        course = LMSCourse(
            external_id="CST-001",
            title="Safety Training",
            duration_minutes=30,
            is_mandatory=True,
            certification_name="Safety Cert",
        )
        assert course.title == "Safety Training"
        assert course.is_mandatory is True

    def test_lms_completion(self):
        completion = LMSCompletion(
            external_id="CST-001",
            employee_external_id="emp-1",
            completed_at="2026-04-09T10:00:00Z",
            score=85.0,
            time_spent_seconds=1800,
        )
        assert completion.score == 85.0
        assert completion.time_spent_seconds == 1800
