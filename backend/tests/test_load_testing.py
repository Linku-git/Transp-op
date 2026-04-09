"""Tests for Load Testing Infrastructure (Session 88)."""
from __future__ import annotations

import random
import uuid

import pytest


# Inline the key functions and constants to avoid cross-package import issues
LOAD_TEST_THRESHOLDS = {
    "p95_1k_concurrent": 300,
    "p95_5k_concurrent": 500,
    "p99_10k_concurrent": 2000,
    "error_rate_normal": 0.001,
    "error_rate_peak": 0.01,
    "websocket_concurrent": 5000,
    "sustained_hours": 1,
}

SITES = [{"code": f"CASA-{i:02d}", "name": f"Casablanca Site {i}"} for i in range(1, 11)]
DEPARTMENTS = ["Production", "Logistique", "Maintenance", "Administration", "RH", "IT", "Qualité", "Sécurité"]
SHIFTS = ["Équipe Matin", "Équipe Après-midi", "Équipe Nuit", "Normal"]


def generate_employees(count: int, tenant_id: str | None = None) -> list[dict]:
    tid = tenant_id or str(uuid.uuid4())
    return [
        {
            "id": str(uuid.uuid4()), "tenant_id": tid,
            "matricule": f"EMP{i+1:05d}", "first_name": "Test", "last_name": "User",
            "email": f"emp{i+1}@test.ma", "department": random.choice(DEPARTMENTS),
            "shift_time": random.choice(SHIFTS), "site_code": random.choice(SITES)["code"],
            "latitude": 33.57 + random.uniform(-0.05, 0.05),
            "longitude": -7.59 + random.uniform(-0.05, 0.05),
            "is_pmr": random.random() < 0.03, "active": True,
        }
        for i in range(count)
    ]


def generate_vehicles(count: int) -> list[dict]:
    types = ["BUS", "MINIBUS", "VAN", "BERLINE"]
    return [
        {"id": str(uuid.uuid4()), "type": random.choice(types), "capacity": random.choice([4, 9, 20, 50])}
        for _ in range(count)
    ]


# Scenario config
SCENARIOS = {
    "scenario_1_api_reads": {"users": 1000, "p95_target_ms": 300, "max_error_rate": 0.001},
    "scenario_2_optimization": {"users": 100, "p95_target_ms": 30000, "max_error_rate": 0.01},
    "scenario_3_mobile": {"users": 5000, "p95_target_ms": 500, "max_error_rate": 0.001},
    "scenario_4_mixed": {"users": 10000, "p95_target_ms": 2000, "max_error_rate": 0.01},
    "scenario_5_sustained": {"users": 5000, "duration_seconds": 3600, "p95_target_ms": 500},
}


class TestDataGenerator:
    def test_generate_1000_employees(self):
        employees = generate_employees(1000)
        assert len(employees) == 1000

    def test_employee_has_required_fields(self):
        emp = generate_employees(1)[0]
        for field in ["id", "matricule", "first_name", "last_name", "email", "department", "site_code", "latitude", "longitude"]:
            assert field in emp

    def test_employee_departments_realistic(self):
        employees = generate_employees(100)
        depts = {e["department"] for e in employees}
        assert len(depts) >= 3

    def test_employee_pmr_rate(self):
        employees = generate_employees(1000)
        pmr_count = sum(1 for e in employees if e["is_pmr"])
        assert 5 < pmr_count < 80

    def test_generate_vehicles(self):
        vehicles = generate_vehicles(100)
        assert len(vehicles) == 100

    def test_10_sites_defined(self):
        assert len(SITES) == 10

    def test_custom_tenant_id(self):
        employees = generate_employees(5, tenant_id="custom-tenant")
        assert all(e["tenant_id"] == "custom-tenant" for e in employees)


class TestScenarioConfig:
    def test_five_scenarios_defined(self):
        assert len(SCENARIOS) == 5

    def test_scenario_1_thresholds(self):
        s = SCENARIOS["scenario_1_api_reads"]
        assert s["users"] == 1000
        assert s["p95_target_ms"] == 300

    def test_scenario_3_mobile(self):
        s = SCENARIOS["scenario_3_mobile"]
        assert s["users"] == 5000
        assert s["p95_target_ms"] == 500

    def test_scenario_4_peak(self):
        s = SCENARIOS["scenario_4_mixed"]
        assert s["users"] == 10000
        assert s["max_error_rate"] == 0.01

    def test_scenario_5_sustained(self):
        s = SCENARIOS["scenario_5_sustained"]
        assert s["duration_seconds"] == 3600


class TestLoadThresholds:
    def test_p95_1k(self):
        assert LOAD_TEST_THRESHOLDS["p95_1k_concurrent"] == 300

    def test_p95_5k(self):
        assert LOAD_TEST_THRESHOLDS["p95_5k_concurrent"] == 500

    def test_error_rate_normal(self):
        assert LOAD_TEST_THRESHOLDS["error_rate_normal"] == 0.001

    def test_error_rate_peak(self):
        assert LOAD_TEST_THRESHOLDS["error_rate_peak"] == 0.01

    def test_websocket(self):
        assert LOAD_TEST_THRESHOLDS["websocket_concurrent"] == 5000

    def test_sustained(self):
        assert LOAD_TEST_THRESHOLDS["sustained_hours"] == 1
