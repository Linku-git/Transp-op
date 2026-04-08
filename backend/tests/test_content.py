"""Tests for Content Model & CRUD API (Session 67)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from app.models.content import Content
from app.schemas.content import (
    ContentCreate,
    ContentUpdate,
    ContentResponse,
    ContentListResponse,
)


class TestContentModel:
    def test_create(self):
        content = Content(
            tenant_id=uuid.uuid4(),
            title="Test News",
            body="<p>News body</p>",
            content_type="news",
            is_active=True,
        )
        assert content.title == "Test News"
        assert content.content_type == "news"
        assert content.is_active is True

    def test_all_content_types(self):
        for ct in ["news", "training", "safety", "survey"]:
            content = Content(
                tenant_id=uuid.uuid4(),
                title=f"{ct} content",
                content_type=ct,
            )
            assert content.content_type == ct

    def test_with_targeting(self):
        content = Content(
            tenant_id=uuid.uuid4(),
            title="Targeted",
            content_type="news",
            target_sites=["site-1", "site-2"],
            target_departments=["IT"],
            target_shifts=["shift-1"],
        )
        assert len(content.target_sites) == 2
        assert content.target_departments == ["IT"]


class TestContentSchemas:
    def test_create_schema(self):
        schema = ContentCreate(
            title="Test",
            body="Body",
            content_type="training",
            target_sites=["s1"],
        )
        assert schema.content_type == "training"

    def test_create_rejects_invalid_type(self):
        with pytest.raises(Exception):
            ContentCreate(title="Test", content_type="invalid")

    def test_create_rejects_empty_title(self):
        with pytest.raises(Exception):
            ContentCreate(title="", content_type="news")

    def test_update_schema_partial(self):
        schema = ContentUpdate(title="Updated Title")
        assert schema.title == "Updated Title"
        assert schema.body is None

    def test_update_rejects_invalid_type(self):
        with pytest.raises(Exception):
            ContentUpdate(content_type="invalid")

    def test_list_response(self):
        resp = ContentListResponse(data=[], total=0)
        assert resp.total == 0
        assert resp.page == 1


class TestAudienceTargeting:
    """Test audience filtering logic."""

    def test_content_without_targeting_matches_all(self):
        content = Content(
            tenant_id=uuid.uuid4(),
            title="Global",
            content_type="news",
            target_sites=None,
        )
        # None means all sites
        assert content.target_sites is None

    def test_content_with_site_targeting(self):
        content = Content(
            tenant_id=uuid.uuid4(),
            title="Site-specific",
            content_type="news",
            target_sites=["site-1", "site-2"],
        )
        assert "site-1" in content.target_sites
        assert "site-3" not in content.target_sites

    def test_multiple_targeting_dimensions(self):
        content = Content(
            tenant_id=uuid.uuid4(),
            title="Multi-target",
            content_type="safety",
            target_sites=["s1"],
            target_departments=["Engineering", "HR"],
            target_shifts=["night"],
        )
        assert len(content.target_departments) == 2
        assert "night" in content.target_shifts
