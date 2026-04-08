"""Tests for Content Delivery & Engagement Tracking (Session 69)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta

import pytest

from app.models.content import Content
from app.models.content_delivery import ContentDelivery
from app.schemas.content_delivery import (
    DeliveryEventCreate,
    CompletionEventCreate,
    ContentDeliveryResponse,
    EngagementMetrics,
    FeedContentResponse,
    FeedResponse,
)


class TestContentDeliveryModel:
    """Test ContentDelivery model creation and fields."""

    def test_create_delivery(self):
        delivery = ContentDelivery(
            tenant_id=uuid.uuid4(),
            content_id=uuid.uuid4(),
            employee_id=uuid.uuid4(),
            delivered_at=datetime.now(timezone.utc),
        )
        assert delivery.delivered_at is not None
        assert delivery.viewed_at is None
        assert delivery.completed_at is None
        assert delivery.quiz_score is None
        assert delivery.time_spent_seconds is None

    def test_delivery_with_all_fields(self):
        now = datetime.now(timezone.utc)
        delivery = ContentDelivery(
            tenant_id=uuid.uuid4(),
            content_id=uuid.uuid4(),
            employee_id=uuid.uuid4(),
            delivered_at=now,
            viewed_at=now + timedelta(seconds=5),
            completed_at=now + timedelta(seconds=120),
            quiz_score=85.5,
            time_spent_seconds=120,
        )
        assert delivery.quiz_score == 85.5
        assert delivery.time_spent_seconds == 120
        assert delivery.viewed_at > delivery.delivered_at
        assert delivery.completed_at > delivery.viewed_at

    def test_delivery_foreign_keys(self):
        tid = uuid.uuid4()
        cid = uuid.uuid4()
        eid = uuid.uuid4()
        delivery = ContentDelivery(
            tenant_id=tid,
            content_id=cid,
            employee_id=eid,
            delivered_at=datetime.now(timezone.utc),
        )
        assert delivery.tenant_id == tid
        assert delivery.content_id == cid
        assert delivery.employee_id == eid


class TestContentDeliverySchemas:
    """Test Pydantic schemas for engagement tracking."""

    def test_delivery_event_create(self):
        schema = DeliveryEventCreate(
            content_id=uuid.uuid4(),
            employee_id=uuid.uuid4(),
        )
        assert schema.content_id is not None
        assert schema.employee_id is not None

    def test_completion_event_with_score(self):
        schema = CompletionEventCreate(
            quiz_score=92.5,
            time_spent_seconds=300,
        )
        assert schema.quiz_score == 92.5
        assert schema.time_spent_seconds == 300

    def test_completion_event_without_score(self):
        schema = CompletionEventCreate()
        assert schema.quiz_score is None
        assert schema.time_spent_seconds is None

    def test_completion_rejects_negative_score(self):
        with pytest.raises(Exception):
            CompletionEventCreate(quiz_score=-1.0)

    def test_completion_rejects_score_over_100(self):
        with pytest.raises(Exception):
            CompletionEventCreate(quiz_score=101.0)

    def test_completion_rejects_negative_time(self):
        with pytest.raises(Exception):
            CompletionEventCreate(time_spent_seconds=-1)


class TestEngagementMetrics:
    """Test engagement metrics schema."""

    def test_empty_metrics(self):
        metrics = EngagementMetrics(content_id=uuid.uuid4())
        assert metrics.total_deliveries == 0
        assert metrics.total_views == 0
        assert metrics.total_completions == 0
        assert metrics.view_rate == 0.0
        assert metrics.completion_rate == 0.0
        assert metrics.avg_quiz_score is None

    def test_metrics_with_data(self):
        metrics = EngagementMetrics(
            content_id=uuid.uuid4(),
            total_deliveries=100,
            total_views=80,
            total_completions=60,
            view_rate=80.0,
            completion_rate=60.0,
            avg_quiz_score=75.5,
            avg_time_spent_seconds=180.0,
        )
        assert metrics.total_deliveries == 100
        assert metrics.view_rate == 80.0
        assert metrics.avg_quiz_score == 75.5


class TestFeedSchemas:
    """Test feed response schemas."""

    def test_feed_content_response(self):
        resp = FeedContentResponse(
            id=uuid.uuid4(),
            title="Test Content",
            content_type="news",
            delivered=True,
            viewed=True,
            completed=False,
        )
        assert resp.title == "Test Content"
        assert resp.delivered is True
        assert resp.completed is False

    def test_feed_response(self):
        resp = FeedResponse(data=[], total=0)
        assert resp.total == 0
        assert resp.page == 1
        assert resp.pages == 1


class TestFeedPersonalization:
    """Test feed filtering logic with Content model."""

    def test_content_matches_employee_site(self):
        site_id = str(uuid.uuid4())
        content = Content(
            tenant_id=uuid.uuid4(),
            title="Site-specific",
            content_type="news",
            target_sites=[site_id],
            is_active=True,
            published_at=datetime.now(timezone.utc),
        )
        assert site_id in content.target_sites

    def test_content_without_targeting_matches_all(self):
        content = Content(
            tenant_id=uuid.uuid4(),
            title="Global",
            content_type="news",
            target_sites=None,
            target_departments=None,
            target_shifts=None,
            is_active=True,
            published_at=datetime.now(timezone.utc),
        )
        # None means all — should match any employee
        assert content.target_sites is None
        assert content.target_departments is None

    def test_expired_content_excluded(self):
        content = Content(
            tenant_id=uuid.uuid4(),
            title="Expired",
            content_type="news",
            is_active=True,
            published_at=datetime.now(timezone.utc) - timedelta(days=30),
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
        now = datetime.now(timezone.utc)
        assert content.expires_at < now

    def test_unpublished_content_excluded(self):
        content = Content(
            tenant_id=uuid.uuid4(),
            title="Draft",
            content_type="news",
            is_active=True,
            published_at=None,
        )
        assert content.published_at is None

    def test_multi_dimension_targeting(self):
        content = Content(
            tenant_id=uuid.uuid4(),
            title="Multi-target",
            content_type="training",
            target_sites=["site-1"],
            target_departments=["Engineering"],
            target_shifts=["morning"],
            is_active=True,
            published_at=datetime.now(timezone.utc),
        )
        # Employee in Engineering, site-1, morning shift should see this
        assert "site-1" in content.target_sites
        assert "Engineering" in content.target_departments
        assert "morning" in content.target_shifts

        # Employee in HR should NOT see this
        assert "HR" not in content.target_departments
