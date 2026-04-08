"""Tests for Security Questionnaire (Session 61)."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.models.security_questionnaire import SecurityQuestionnaire
from app.schemas.security_questionnaire import (
    SecurityQuestionnaireSubmit,
    SecurityQuestionnaireResponse,
    SecurityQuestionnaireHistory,
    ReassessmentStatus,
)
from app.services.reassessment_scheduler import (
    is_reassessment_due,
    next_due_date,
    get_interval_days,
    ReassessmentInterval,
)


class TestSecurityQuestionnaireModel:
    def test_create(self):
        q = SecurityQuestionnaire(
            tenant_id=uuid.uuid4(),
            employee_id=uuid.uuid4(),
            version=1,
            overall_safety_rating=4,
            responses={"q1": "a", "q2": "b"},
            vulnerable_stops=["stop-1", "stop-2"],
            night_concerns="Dark streets",
            submitted_at=datetime.now(timezone.utc),
            trigger_type="periodic",
        )
        assert q.overall_safety_rating == 4
        assert q.version == 1
        assert len(q.vulnerable_stops) == 2

    def test_trigger_types(self):
        for trigger in ["periodic", "incident", "initial"]:
            q = SecurityQuestionnaire(
                tenant_id=uuid.uuid4(),
                employee_id=uuid.uuid4(),
                version=1,
                overall_safety_rating=3,
                submitted_at=datetime.now(timezone.utc),
                trigger_type=trigger,
            )
            assert q.trigger_type == trigger


class TestSecurityQuestionnaireSchemas:
    def test_submit_schema_valid(self):
        schema = SecurityQuestionnaireSubmit(
            overall_safety_rating=3,
            responses={"feeling": "safe"},
            vulnerable_stops=["s1"],
            night_concerns="Too dark",
        )
        assert schema.overall_safety_rating == 3

    def test_submit_rejects_rating_below_1(self):
        with pytest.raises(Exception):
            SecurityQuestionnaireSubmit(overall_safety_rating=0)

    def test_submit_rejects_rating_above_5(self):
        with pytest.raises(Exception):
            SecurityQuestionnaireSubmit(overall_safety_rating=6)

    def test_submit_rejects_invalid_trigger(self):
        with pytest.raises(Exception):
            SecurityQuestionnaireSubmit(
                overall_safety_rating=3, trigger_type="invalid"
            )

    def test_history_empty(self):
        history = SecurityQuestionnaireHistory()
        assert history.latest is None
        assert history.total_submissions == 0

    def test_reassessment_status(self):
        status = ReassessmentStatus(
            employee_id=uuid.uuid4(),
            is_due=True,
            trigger_type="incident",
        )
        assert status.is_due is True


class TestReassessmentScheduler:
    def test_due_when_never_submitted(self):
        assert is_reassessment_due(None) is True

    def test_not_due_when_recently_submitted(self):
        recent = datetime.now(timezone.utc) - timedelta(days=10)
        assert is_reassessment_due(recent) is False

    def test_due_when_quarterly_expired(self):
        old = datetime.now(timezone.utc) - timedelta(days=100)
        assert is_reassessment_due(old, ReassessmentInterval.QUARTERLY) is True

    def test_not_due_within_quarter(self):
        recent = datetime.now(timezone.utc) - timedelta(days=60)
        assert is_reassessment_due(recent, ReassessmentInterval.QUARTERLY) is False

    def test_semi_annual_interval(self):
        old = datetime.now(timezone.utc) - timedelta(days=200)
        assert is_reassessment_due(old, ReassessmentInterval.SEMI_ANNUAL) is True

    def test_annual_interval(self):
        old = datetime.now(timezone.utc) - timedelta(days=400)
        assert is_reassessment_due(old, ReassessmentInterval.ANNUAL) is True
        recent = datetime.now(timezone.utc) - timedelta(days=300)
        assert is_reassessment_due(recent, ReassessmentInterval.ANNUAL) is False

    def test_next_due_date_none(self):
        result = next_due_date(None)
        assert result is not None

    def test_next_due_date_quarterly(self):
        submitted = datetime(2026, 1, 1, tzinfo=timezone.utc)
        due = next_due_date(submitted, ReassessmentInterval.QUARTERLY)
        assert due == submitted + timedelta(days=90)

    def test_interval_days(self):
        assert get_interval_days(ReassessmentInterval.QUARTERLY) == 90
        assert get_interval_days(ReassessmentInterval.SEMI_ANNUAL) == 180
        assert get_interval_days(ReassessmentInterval.ANNUAL) == 365

    def test_interval_from_string(self):
        assert get_interval_days("quarterly") == 90
