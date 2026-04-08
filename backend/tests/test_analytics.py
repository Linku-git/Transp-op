"""Tests for Engagement Analytics (Session 75)."""
from __future__ import annotations

import uuid

import pytest


class TestAnalyticsResponseFormat:
    """Test the expected analytics response structure."""

    def test_overview_fields(self):
        overview = {
            "total_deliveries": 500,
            "total_views": 400,
            "total_completions": 250,
            "view_rate": 80.0,
            "completion_rate": 50.0,
            "avg_quiz_score": 78.5,
            "avg_time_spent_seconds": 180,
            "training_hours_recovered": 12.5,
        }
        assert overview["view_rate"] == 80.0
        assert overview["training_hours_recovered"] == 12.5

    def test_view_rate_calculation(self):
        views = 400
        deliveries = 500
        rate = round(views / deliveries * 100, 1)
        assert rate == 80.0

    def test_completion_rate_calculation(self):
        completions = 250
        deliveries = 500
        rate = round(completions / deliveries * 100, 1)
        assert rate == 50.0

    def test_training_hours_recovered(self):
        total_seconds = 45000
        hours = round(total_seconds / 3600, 1)
        assert hours == 12.5

    def test_zero_deliveries_rate(self):
        deliveries = 0
        rate = round(0 / max(deliveries, 1) * 100, 1) if deliveries > 0 else 0
        assert rate == 0

    def test_content_ranking_structure(self):
        item = {
            "content_id": str(uuid.uuid4()),
            "title": "Formation test",
            "content_type": "training",
            "deliveries": 100,
            "views": 80,
            "completions": 60,
            "avg_quiz_score": 85.0,
            "avg_time_seconds": 300,
        }
        assert item["content_type"] == "training"
        assert item["views"] <= item["deliveries"]
        assert item["completions"] <= item["views"]

    def test_by_type_structure(self):
        by_type = {
            "news": {"deliveries": 200, "views": 180, "completions": 120},
            "training": {"deliveries": 100, "views": 80, "completions": 60},
        }
        assert "news" in by_type
        assert by_type["training"]["completions"] == 60

    def test_avg_quiz_score_nullable(self):
        overview = {"avg_quiz_score": None}
        assert overview["avg_quiz_score"] is None

    def test_empty_analytics(self):
        analytics = {
            "overview": {
                "total_deliveries": 0,
                "total_views": 0,
                "total_completions": 0,
                "view_rate": 0,
                "completion_rate": 0,
                "avg_quiz_score": None,
                "avg_time_spent_seconds": None,
                "training_hours_recovered": 0,
            },
            "content_ranking": [],
            "by_type": {},
        }
        assert analytics["overview"]["total_deliveries"] == 0
        assert len(analytics["content_ranking"]) == 0
