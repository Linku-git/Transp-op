"""Locust load testing scenarios for Transpop platform.

Run: locust -f tests/load/locustfile.py --host=http://localhost:8000
"""
from __future__ import annotations

import json
import random
import uuid

from locust import HttpUser, between, task, tag, events


class TranspopReadUser(HttpUser):
    """Simulates read-heavy users (dashboard, listing, KPIs)."""
    wait_time = between(1, 3)
    weight = 5  # 50% of users

    def on_start(self):
        """Login and get auth token."""
        # In real tests, authenticate first
        self.headers = {
            "Authorization": "Bearer test_token",
            "Content-Type": "application/json",
        }

    @tag("read", "dashboard")
    @task(3)
    def view_dashboard(self):
        self.client.get("/api/v1/kpis/dashboard", headers=self.headers)

    @tag("read", "sites")
    @task(2)
    def list_sites(self):
        self.client.get("/api/v1/sites/?page=1&page_size=20", headers=self.headers)

    @tag("read", "employees")
    @task(2)
    def list_employees(self):
        page = random.randint(1, 10)
        self.client.get(
            f"/api/v1/employees/?page={page}&page_size=50",
            headers=self.headers,
        )

    @tag("read", "vehicles")
    @task(1)
    def list_vehicles(self):
        self.client.get("/api/v1/vehicles/?page=1&page_size=50", headers=self.headers)

    @tag("read", "optimization")
    @task(1)
    def view_optimization_history(self):
        self.client.get("/api/v1/optimization/history", headers=self.headers)


class TranspopMobileUser(HttpUser):
    """Simulates mobile app users (trip booking, RTI, content)."""
    wait_time = between(2, 5)
    weight = 3  # 30% of users

    def on_start(self):
        self.headers = {
            "Authorization": "Bearer test_mobile_token",
            "Content-Type": "application/json",
        }
        self.employee_id = str(uuid.uuid4())

    @tag("mobile", "content")
    @task(3)
    def view_content_feed(self):
        self.client.get(
            f"/api/v1/content/feed?employee_id={self.employee_id}",
            headers=self.headers,
        )

    @tag("mobile", "trips")
    @task(2)
    def check_next_trip(self):
        self.client.get("/api/v1/trips/next", headers=self.headers)

    @tag("mobile", "rti")
    @task(2)
    def poll_vehicle_position(self):
        vehicle_id = str(uuid.uuid4())
        self.client.get(
            f"/api/v1/rti/vehicle-position/{vehicle_id}",
            headers=self.headers,
        )

    @tag("mobile", "notifications")
    @task(1)
    def check_notifications(self):
        self.client.get("/api/v1/notifications/unread-count", headers=self.headers)


class TranspopWriteUser(HttpUser):
    """Simulates write operations (optimization, reports, sync)."""
    wait_time = between(5, 15)
    weight = 1  # 10% of users

    def on_start(self):
        self.headers = {
            "Authorization": "Bearer test_admin_token",
            "Content-Type": "application/json",
        }

    @tag("write", "content")
    @task(2)
    def create_content(self):
        self.client.post(
            "/api/v1/content",
            headers=self.headers,
            json={
                "title": f"Load test content {random.randint(1, 10000)}",
                "body": "<p>Load test body</p>",
                "content_type": random.choice(["news", "training", "safety"]),
            },
        )

    @tag("write", "financial")
    @task(1)
    def calculate_tco(self):
        self.client.post(
            "/api/v1/financial/tco/calculate",
            headers=self.headers,
            json={"fleet_composition": [], "duration_years": 5},
        )

    @tag("write", "export")
    @task(1)
    def export_sizing_plan(self):
        self.client.post(
            "/api/v1/export/sizing-plan",
            headers=self.headers,
            json={"format": "json"},
        )


class TranspopOptimizationUser(HttpUser):
    """Simulates heavy optimization workloads."""
    wait_time = between(30, 60)
    weight = 1  # 10% of users

    def on_start(self):
        self.headers = {
            "Authorization": "Bearer test_admin_token",
            "Content-Type": "application/json",
        }

    @tag("optimization")
    @task(1)
    def run_optimization(self):
        self.client.post(
            "/api/v1/optimization/run",
            headers=self.headers,
            json={"site_id": str(uuid.uuid4()), "condition": "normal"},
        )
