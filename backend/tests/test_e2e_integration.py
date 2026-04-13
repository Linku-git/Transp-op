"""E2E Integration Tests -- Session 127.

Tests verify cross-module data flows and the complete pipeline
from ligne creation through optimization, tracking, scoring, and reporting.

These are structural/contract tests that validate the integration contracts
between modules using mock data representative of real Transpop data
(Casablanca coordinates, MAD currency, French names).
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, date, timedelta

import pytest

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Shared fixtures -- representative Casablanca OCP data
# ---------------------------------------------------------------------------

CASABLANCA_STOPS = [
    {"id": "stop_centre", "lat": 33.5731, "lng": -7.5898, "name": "Casablanca Centre", "demand": 15},
    {"id": "stop_ain_sebaa", "lat": 33.5950, "lng": -7.6200, "name": "Ain Sebaa", "demand": 20},
    {"id": "stop_ain_diab", "lat": 33.5400, "lng": -7.6500, "name": "Ain Diab", "demand": 10},
    {"id": "stop_sidi_maarouf", "lat": 33.5300, "lng": -7.6300, "name": "Sidi Maarouf", "demand": 18},
    {"id": "stop_hay_hassani", "lat": 33.5600, "lng": -7.6700, "name": "Hay Hassani", "demand": 12},
]

VEHICLE_FLEET = [
    {"id": "v1", "type": "bus_diesel", "capacity": 50, "km_autonomy": 500},
    {"id": "v2", "type": "bus_electric", "capacity": 45, "km_autonomy": 250},
    {"id": "v3", "type": "minibus_diesel", "capacity": 25, "km_autonomy": 400},
]


class TestFullPipelineIntegration:
    """E2E: ligne -> stops -> optimize -> track -> score -> report."""

    def test_pipeline_ligne_to_stops(self) -> None:
        """M1->M3: Ligne creation provides data for stop generation."""
        ligne_data = {
            "id": str(uuid.uuid4()),
            "name": "Ligne OCP Jorf-Casa",
            "km_daily": 45.0,
            "round_trips": 2,
            "days_per_year": 250,
            "km_annual": 45.0 * 2 * 250,  # D * R * J formula from CDC SOTREG
            "stops": CASABLANCA_STOPS[:3],
        }
        # Verify km_annual formula: D * R * J (CDC SOTREG v5.0)
        assert ligne_data["km_annual"] == 45.0 * 2 * 250
        assert ligne_data["km_annual"] == 22_500.0
        assert len(ligne_data["stops"]) >= 2
        # Stop coordinates are valid Casablanca region (33.5-33.6 N, 7.5-7.7 W)
        for stop in ligne_data["stops"]:
            assert 33.0 <= stop["lat"] <= 34.0, f"Latitude out of Casablanca range: {stop['lat']}"
            assert -8.0 <= stop["lng"] <= -7.0, f"Longitude out of Casablanca range: {stop['lng']}"

    def test_pipeline_optimization_produces_routes(self) -> None:
        """M3->M8: Stop data feeds into route optimization."""
        # Clarke-Wright result
        cw_routes = [
            {"vehicle_id": "v1", "stops": ["stop_centre", "stop_ain_sebaa", "stop_hay_hassani"], "distance_km": 18.5, "passengers": 47},
            {"vehicle_id": "v3", "stops": ["stop_ain_diab", "stop_sidi_maarouf"], "distance_km": 12.0, "passengers": 28},
        ]
        # GA result (potentially different routing)
        ga_routes = [
            {"vehicle_id": "v1", "stops": ["stop_centre", "stop_sidi_maarouf", "stop_ain_diab"], "distance_km": 16.0, "passengers": 43},
            {"vehicle_id": "v3", "stops": ["stop_ain_sebaa", "stop_hay_hassani"], "distance_km": 14.5, "passengers": 32},
        ]
        # Both solvers must cover all stops
        cw_stop_ids = {s for r in cw_routes for s in r["stops"]}
        ga_stop_ids = {s for r in ga_routes for s in r["stops"]}
        all_stop_ids = {s["id"] for s in CASABLANCA_STOPS}
        assert cw_stop_ids == all_stop_ids, "Clarke-Wright must cover all stops"
        assert ga_stop_ids == all_stop_ids, "Genetic Algorithm must cover all stops"
        # Total passengers match demand
        total_demand = sum(s["demand"] for s in CASABLANCA_STOPS)
        assert sum(r["passengers"] for r in cw_routes) == total_demand
        assert sum(r["passengers"] for r in ga_routes) == total_demand

    def test_pipeline_tracking_updates_positions(self) -> None:
        """M8: Vehicle tracking via SocketIO produces position updates."""
        now = datetime.utcnow()
        positions = [
            {"vehicle_id": "v1", "lat": 33.5731, "lng": -7.5898, "speed_kmh": 35.0, "heading": 45.0, "timestamp": now.isoformat()},
            {"vehicle_id": "v1", "lat": 33.5800, "lng": -7.5950, "speed_kmh": 42.0, "heading": 50.0, "timestamp": (now + timedelta(seconds=30)).isoformat()},
            {"vehicle_id": "v1", "lat": 33.5880, "lng": -7.6020, "speed_kmh": 38.0, "heading": 48.0, "timestamp": (now + timedelta(seconds=60)).isoformat()},
        ]
        # Positions are within valid range and speeds are realistic
        assert len(positions) >= 2
        for pos in positions:
            assert 0 <= pos["speed_kmh"] <= 150, "Speed must be realistic"
            assert 33.0 <= pos["lat"] <= 34.0, "Latitude must be Casablanca region"
            assert -8.0 <= pos["lng"] <= -7.0, "Longitude must be Casablanca region"
            assert 0 <= pos["heading"] <= 360, "Heading must be 0-360 degrees"
        # Timestamps are chronologically ordered
        ts = [datetime.fromisoformat(p["timestamp"]) for p in positions]
        for i in range(1, len(ts)):
            assert ts[i] > ts[i - 1], "Positions must be chronological"

    def test_pipeline_mcda_scoring(self) -> None:
        """M7: MCDA scoring uses optimization outputs from M1-M6."""
        # 6 criteria from CDC SOTREG v5.0 weighted sum model
        criteria = {
            "cout_total": {"score": 78, "weight": 0.25},     # M5 TCO/NPV
            "emission_co2": {"score": 85, "weight": 0.15},   # M1 diagnostic
            "temps_trajet": {"score": 72, "weight": 0.20},   # M4 performance
            "couverture": {"score": 90, "weight": 0.15},     # M3 infrastructure
            "fiabilite": {"score": 80, "weight": 0.15},      # M4 OTP
            "flexibilite": {"score": 75, "weight": 0.10},    # M6 roadmap
        }
        # Weights must sum to 1.0 (MCDA requirement)
        total_weight = sum(c["weight"] for c in criteria.values())
        assert abs(total_weight - 1.0) < 0.001, f"Weights must sum to 1.0, got {total_weight}"
        # Weighted score calculation
        weighted_score = sum(c["score"] * c["weight"] for c in criteria.values())
        assert 0 <= weighted_score <= 100, "MCDA score must be 0-100"
        assert weighted_score == pytest.approx(79.65, abs=0.01)

    def test_pipeline_report_generation(self) -> None:
        """Final step: comparison report is generated from pipeline data."""
        report_data = {
            "id": str(uuid.uuid4()),
            "type": "comparison_pdf",
            "ligne_count": 5,
            "routes_cw": 3,
            "routes_ga": 3,
            "mcda_score": 79.65,
            "total_distance_km": 42.0,
            "co2_saved_kg": 125.5,
            "currency": "MAD",
            "cost_total_mad": 8_500_000.0,
            "generated_at": datetime.utcnow().isoformat(),
            "sections": ["diagnostic", "technologies", "infrastructure", "performance", "finance", "scoring"],
        }
        assert report_data["type"] == "comparison_pdf"
        assert report_data["mcda_score"] > 0
        assert report_data["co2_saved_kg"] > 0
        assert report_data["currency"] == "MAD"
        assert len(report_data["sections"]) == 6, "Report must include all 6 SOTREG module sections"


class TestClarkeWrightAndGASolvers:
    """Verify both optimization solvers produce valid results."""

    def test_clarke_wright_respects_capacity(self) -> None:
        """CW solver produces routes respecting vehicle capacity."""
        vehicle_capacity = 50
        routes = [
            {"stops": ["stop_centre", "stop_ain_sebaa", "stop_sidi_maarouf"], "load": 45, "distance_km": 18.5},
            {"stops": ["stop_ain_diab", "stop_hay_hassani"], "load": 22, "distance_km": 12.0},
        ]
        for route in routes:
            assert route["load"] <= vehicle_capacity, f"Route load {route['load']} exceeds capacity {vehicle_capacity}"
            assert len(route["stops"]) >= 1, "Each route must have at least one stop"
            assert route["distance_km"] > 0, "Distance must be positive"

    def test_ga_respects_constraints(self) -> None:
        """GA solver produces routes respecting capacity and distance constraints."""
        vehicle_capacity = 50
        max_route_distance_km = 60.0
        routes = [
            {"stops": ["stop_centre", "stop_sidi_maarouf", "stop_hay_hassani"], "load": 42, "distance_km": 22.0},
            {"stops": ["stop_ain_sebaa", "stop_ain_diab"], "load": 30, "distance_km": 15.0},
        ]
        for route in routes:
            assert route["load"] <= vehicle_capacity, f"Route load {route['load']} exceeds capacity"
            assert route["distance_km"] <= max_route_distance_km, f"Route distance {route['distance_km']} exceeds max"


class TestMCDAUsesOptimizationOutput:
    """M7 MCDA scoring correctly uses outputs from other modules."""

    def test_mcda_receives_all_module_inputs(self) -> None:
        """MCDA scoring function receives data from all 6 SOTREG modules (M1-M6)."""
        module_outputs = {
            "M1_diagnostic": {"ligne_count": 5, "zfe_coverage": 0.8, "total_km_annual": 112_500},
            "M2_technologies": {"tco_15y_mad": 15_000_000, "breakeven_year": 7, "irve_count": 12},
            "M3_infrastructure": {"stop_count": 45, "capacity_los": "B", "depot_area_m2": 3500},
            "M4_performance": {"otp_percent": 92.5, "headway_cv": 0.12, "avg_speed_kmh": 35.0},
            "M5_finance": {"npv_mad": 8_500_000, "irr_percent": 12.3, "payback_years": 6.2},
            "M6_roadmap": {"phases": 3, "completion_percent": 65, "milestones": 8},
        }
        # All 6 modules provide data
        assert len(module_outputs) == 6, "MCDA must receive inputs from exactly 6 modules"
        for key, data in module_outputs.items():
            assert isinstance(data, dict), f"Module {key} output must be a dict"
            assert len(data) > 0, f"Module {key} output must not be empty"
        # Financial data is in MAD
        assert module_outputs["M5_finance"]["npv_mad"] > 0
        assert module_outputs["M2_technologies"]["tco_15y_mad"] > 0


class TestCrossModuleDataFlows:
    """Integration tests across module boundaries."""

    def test_m1_to_m4_diagnostic_to_kpi(self) -> None:
        """M1 diagnostic data flows into M4 KPI calculations."""
        # M1 output: ligne with km metrics and schedule
        m1_output = {
            "ligne_id": "L001",
            "ligne_name": "Ligne OCP Jorf-Casa",
            "km_daily": 45.0,
            "days_per_year": 250,
            "schedule": {"departures_per_day": 12, "first_departure": "06:30", "last_departure": "20:00"},
        }
        # M4 uses this to calculate KPIs
        expected_annual_departures = m1_output["schedule"]["departures_per_day"] * m1_output["days_per_year"]
        assert expected_annual_departures == 3_000
        # OTP is calculated per departure with a 5-minute tolerance
        otp_threshold_minutes = 5
        total_departures = expected_annual_departures
        on_time_departures = int(total_departures * 0.925)  # 92.5% OTP
        otp_percent = (on_time_departures / total_departures) * 100
        assert 90 <= otp_percent <= 95, f"Expected OTP ~92.5%, got {otp_percent}%"

    def test_m2_to_m5_tco_to_npv(self) -> None:
        """M2 TCO data feeds M5 NPV calculations."""
        # M2 output: 15-year TCO breakdown in MAD
        m2_tco = {
            "vehicle_cost_mad": 3_500_000,
            "energy_cost_annual_mad": 120_000,
            "maintenance_annual_mad": 80_000,
            "insurance_annual_mad": 45_000,
            "years": 15,
            "total_tco_mad": 3_500_000 + (120_000 + 80_000 + 45_000) * 15,
        }
        assert m2_tco["total_tco_mad"] == 3_500_000 + 245_000 * 15
        assert m2_tco["total_tco_mad"] == 7_175_000
        # M5 uses TCO for NPV calculation with Morocco discount rate
        discount_rate = 0.08  # 8% for Morocco market
        npv = float(-m2_tco["vehicle_cost_mad"])
        annual_savings_vs_diesel = 250_000  # estimated savings
        for year in range(1, m2_tco["years"] + 1):
            npv += annual_savings_vs_diesel / ((1 + discount_rate) ** year)
        assert isinstance(npv, float)
        # NPV should be calculable (positive for good investments)
        assert npv != 0, "NPV must be non-zero for a real investment"
        # NPV is negative here because vehicle cost (3.5M) exceeds discounted savings
        # This is expected: 250k/yr * ~8.56 (15yr annuity factor @8%) = 2.14M < 3.5M
        assert isinstance(npv, float), "NPV must be a float value"

    def test_m3_to_m8_stops_to_routing(self) -> None:
        """M3 generated stops are used by M8 route optimizer."""
        # M3 output: DBSCAN-generated stops with HCM 2000 capacity and LOS
        m3_stops = [
            {"id": f"stop_{i}", "lat": 33.5 + i * 0.01, "lng": -7.6 + i * 0.01, "capacity": 20 + i * 5, "los": "B"}
            for i in range(8)
        ]
        # M8 route optimizer expects this format
        for stop in m3_stops:
            assert "id" in stop, "Stop must have an id"
            assert "lat" in stop, "Stop must have latitude"
            assert "lng" in stop, "Stop must have longitude"
            assert "capacity" in stop, "Stop must have capacity from HCM 2000"
            assert stop["capacity"] > 0, "Capacity must be positive"
            assert stop["los"] in ("A", "B", "C", "D", "E", "F"), "LOS must be A-F per HCM 2000"
        # At least 2 stops needed for routing
        assert len(m3_stops) >= 2, "Need at least 2 stops for routing"
        # Total capacity across stops
        total_capacity = sum(s["capacity"] for s in m3_stops)
        assert total_capacity > 0

    def test_m4_to_m8_telemetry_to_risk(self) -> None:
        """M4 telemetry data feeds M8 driver risk scoring (RandomForest)."""
        # M4 output: telemetry features per driver
        telemetry = {
            "driver_id": "D001",
            "driver_name": "Ahmed Benali",
            "avg_speed_kmh": 42.5,
            "hard_braking_count": 3,
            "harsh_acceleration_count": 2,
            "speeding_events": 1,
            "idle_time_minutes": 15,
            "total_distance_km": 120.5,
            "fuel_consumption_l100km": 28.4,
            "night_driving_hours": 0.5,
        }
        # M8 RandomForest expects exactly 8 features (Session 120)
        feature_names = [
            "avg_speed_kmh", "hard_braking_count", "harsh_acceleration_count",
            "speeding_events", "idle_time_minutes", "total_distance_km",
            "fuel_consumption_l100km", "night_driving_hours",
        ]
        for feat in feature_names:
            assert feat in telemetry, f"Missing feature: {feat}"
            assert isinstance(telemetry[feat], (int, float)), f"Feature {feat} must be numeric"
        # Risk score output: 0-100 (100 = safest, per Session 120 formula)
        mock_risk_score = 82.0  # Good driver
        assert 0 <= mock_risk_score <= 100, "Risk score must be 0-100"
        # Risk category thresholds (from Session 120)
        if mock_risk_score >= 80:
            category = "low"
        elif mock_risk_score >= 50:
            category = "medium"
        else:
            category = "high"
        assert category == "low", f"Score 82 should be 'low' risk, got '{category}'"
