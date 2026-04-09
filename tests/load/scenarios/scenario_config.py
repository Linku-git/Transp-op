"""Load test scenario configurations.

Each scenario defines user count, spawn rate, duration, and expected thresholds.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LoadScenario:
    name: str
    description: str
    users: int
    spawn_rate: int
    duration_seconds: int
    p95_target_ms: int
    max_error_rate: float
    tags: list[str]


SCENARIOS = {
    "scenario_1_api_reads": LoadScenario(
        name="API Reads (1K concurrent)",
        description="1,000 concurrent API reads: site/employee listing, dashboard KPIs",
        users=1000,
        spawn_rate=50,
        duration_seconds=300,
        p95_target_ms=300,
        max_error_rate=0.001,
        tags=["read", "dashboard", "sites", "employees"],
    ),
    "scenario_2_optimization": LoadScenario(
        name="Optimization Runs (100 concurrent)",
        description="100 concurrent optimization runs",
        users=100,
        spawn_rate=10,
        duration_seconds=600,
        p95_target_ms=30000,
        max_error_rate=0.01,
        tags=["optimization"],
    ),
    "scenario_3_mobile": LoadScenario(
        name="Mobile Users (5K concurrent)",
        description="5,000 concurrent mobile users: trip booking, RTI polling",
        users=5000,
        spawn_rate=100,
        duration_seconds=300,
        p95_target_ms=500,
        max_error_rate=0.001,
        tags=["mobile", "trips", "rti", "content"],
    ),
    "scenario_4_mixed": LoadScenario(
        name="Mixed Workload (10K concurrent)",
        description="10,000 concurrent users: reads, writes, WebSocket",
        users=10000,
        spawn_rate=200,
        duration_seconds=300,
        p95_target_ms=2000,
        max_error_rate=0.01,
        tags=["read", "write", "mobile", "optimization"],
    ),
    "scenario_5_sustained": LoadScenario(
        name="Sustained Load (1 hour @ 5K)",
        description="Sustained load at 5,000 concurrent for 1 hour",
        users=5000,
        spawn_rate=100,
        duration_seconds=3600,
        p95_target_ms=500,
        max_error_rate=0.001,
        tags=["read", "mobile"],
    ),
}


def get_scenario(name: str) -> LoadScenario:
    scenario = SCENARIOS.get(name)
    if not scenario:
        raise ValueError(f"Unknown scenario: {name}. Available: {list(SCENARIOS.keys())}")
    return scenario
