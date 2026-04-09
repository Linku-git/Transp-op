"""Realistic test data generator for load testing.

Generates 1,000+ employees across 10 sites with realistic Moroccan data.
"""
from __future__ import annotations

import random
import uuid
from datetime import datetime, timezone

MOROCCAN_FIRST_NAMES = [
    "Mohammed", "Ahmed", "Youssef", "Amine", "Omar", "Hassan", "Karim", "Samir",
    "Fatima", "Amina", "Khadija", "Salma", "Nadia", "Zineb", "Meryem", "Houda",
]

MOROCCAN_LAST_NAMES = [
    "Benali", "Elhilali", "Lahlou", "Tazi", "Alaoui", "Berrada", "Chraibi",
    "Fassi", "Idrissi", "Kettani", "Mansouri", "Naciri", "Ouazzani", "Rami",
]

DEPARTMENTS = [
    "Production", "Logistique", "Maintenance", "Administration",
    "Ressources Humaines", "Informatique", "Qualité", "Sécurité",
]

SHIFTS = ["Équipe Matin", "Équipe Après-midi", "Équipe Nuit", "Normal"]

SITES = [
    {"code": f"CASA-{i:02d}", "name": f"Casablanca Site {i}", "city": "Casablanca",
     "lat": 33.5731 + random.uniform(-0.1, 0.1), "lng": -7.5898 + random.uniform(-0.1, 0.1)}
    for i in range(1, 11)
]


def generate_employees(count: int = 1000, tenant_id: str | None = None) -> list[dict]:
    """Generate realistic employee records."""
    tid = tenant_id or str(uuid.uuid4())
    employees = []
    for i in range(count):
        site = random.choice(SITES)
        employees.append({
            "id": str(uuid.uuid4()),
            "tenant_id": tid,
            "matricule": f"EMP{i+1:05d}",
            "first_name": random.choice(MOROCCAN_FIRST_NAMES),
            "last_name": random.choice(MOROCCAN_LAST_NAMES),
            "email": f"emp{i+1:05d}@company.ma",
            "department": random.choice(DEPARTMENTS),
            "shift_time": random.choice(SHIFTS),
            "site_code": site["code"],
            "latitude": site["lat"] + random.uniform(-0.05, 0.05),
            "longitude": site["lng"] + random.uniform(-0.05, 0.05),
            "is_pmr": random.random() < 0.03,  # 3% PMR
            "active": True,
        })
    return employees


def generate_vehicles(count: int = 100, tenant_id: str | None = None) -> list[dict]:
    """Generate realistic vehicle records."""
    tid = tenant_id or str(uuid.uuid4())
    types = ["BUS", "MINIBUS", "VAN", "BERLINE"]
    capacities = {"BUS": 50, "MINIBUS": 20, "VAN": 9, "BERLINE": 4}
    vehicles = []
    for i in range(count):
        vtype = random.choice(types)
        vehicles.append({
            "id": str(uuid.uuid4()),
            "tenant_id": tid,
            "type": vtype,
            "brand": random.choice(["Mercedes", "Renault", "Toyota", "Hyundai"]),
            "capacity": capacities[vtype],
            "site_code": random.choice(SITES)["code"],
            "is_pmr_accessible": random.random() < 0.15,
            "motorization": random.choice(["diesel", "electric", "hybrid"]),
            "condition": random.choice(["good", "fair", "needs_maintenance"]),
        })
    return vehicles


# Performance thresholds for load test assertions
LOAD_TEST_THRESHOLDS = {
    "p95_1k_concurrent": 300,      # ms
    "p95_5k_concurrent": 500,      # ms
    "p99_10k_concurrent": 2000,    # ms
    "error_rate_normal": 0.001,    # 0.1%
    "error_rate_peak": 0.01,       # 1%
    "websocket_concurrent": 5000,
    "sustained_hours": 1,
}
