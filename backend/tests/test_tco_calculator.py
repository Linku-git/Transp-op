from __future__ import annotations

from decimal import Decimal

import pytest
from httpx import AsyncClient

from app.services.tco_calculator import (
    compute_tco_single,
    compute_tco_evolution,
    compare_motorizations,
    compute_fleet_tco,
    calculate_tco,
)
from tests.conftest import login_as_admin


# ---------------------------------------------------------------------------
# Unit tests — TCO calculator service
# ---------------------------------------------------------------------------


def test_tco_single_vehicle_known_values() -> None:
    """Known input produces expected TCO output."""
    # TCO = 200000 + (10000 × 5) + (0.10 × 40000 × 5) − 30000
    # TCO = 200000 + 50000 + 20000 − 30000 = 240000
    result = compute_tco_single(
        purchase_price=Decimal("200000"),
        annual_maintenance_cost=Decimal("10000"),
        energy_cost_per_km=Decimal("0.10"),
        annual_km=Decimal("40000"),
        residual_value=Decimal("30000"),
        duration_years=5,
        quantity=1,
    )
    assert result["tco_per_vehicle"] == 240000.0
    assert result["tco_total"] == 240000.0


def test_tco_formula_components() -> None:
    """Each formula component is calculated correctly."""
    result = compute_tco_single(
        purchase_price=Decimal("150000"),
        annual_maintenance_cost=Decimal("8000"),
        energy_cost_per_km=Decimal("0.15"),
        annual_km=Decimal("50000"),
        residual_value=Decimal("25000"),
        duration_years=3,
        quantity=2,
    )
    # maintenance_total = 8000 × 3 = 24000
    assert result["maintenance_total"] == 24000.0
    # energy_total = 0.15 × 50000 × 3 = 22500
    assert result["energy_total"] == 22500.0
    # tco_per_vehicle = 150000 + 24000 + 22500 − 25000 = 171500
    assert result["tco_per_vehicle"] == 171500.0
    # tco_total = 171500 × 2 = 343000
    assert result["tco_total"] == 343000.0
    assert result["quantity"] == 2
    assert result["duration_years"] == 3


def test_tco_diesel_vs_electric() -> None:
    """Electric has higher purchase but lower energy cost; over 10 years electric can be cheaper."""
    diesel = compute_tco_single(
        purchase_price=Decimal("180000"),
        annual_maintenance_cost=Decimal("12000"),
        energy_cost_per_km=Decimal("0.15"),
        annual_km=Decimal("40000"),
        residual_value=Decimal("30000"),
        duration_years=10,
        quantity=1,
    )
    electric = compute_tco_single(
        purchase_price=Decimal("300000"),
        annual_maintenance_cost=Decimal("6000"),
        energy_cost_per_km=Decimal("0.06"),
        annual_km=Decimal("40000"),
        residual_value=Decimal("50000"),
        duration_years=10,
        quantity=1,
    )
    # Diesel: 180000 + 120000 + 60000 − 30000 = 330000
    assert diesel["tco_per_vehicle"] == 330000.0
    # Electric: 300000 + 60000 + 24000 − 50000 = 334000
    assert electric["tco_per_vehicle"] == 334000.0
    # Both are close; diesel slightly cheaper at 10y with these numbers
    assert diesel["purchase_price"] < electric["purchase_price"]
    assert diesel["energy_cost_per_km"] > electric["energy_cost_per_km"]


def test_tco_motorization_comparison() -> None:
    """All available motorizations for midibus are computed and returned sorted."""
    results = compare_motorizations(
        vehicle_type="midibus",
        duration_years=5,
        quantity=1,
    )
    # midibus has diesel, hybrid, electric, gnv
    motorizations = [r["motorization"] for r in results]
    assert len(results) >= 4
    assert "diesel" in motorizations
    assert "hybrid" in motorizations
    assert "electric" in motorizations
    assert "gnv" in motorizations

    # Sorted by tco_per_vehicle ascending
    tcos = [r["tco_per_vehicle"] for r in results]
    assert tcos == sorted(tcos)


def test_tco_fleet_aggregation() -> None:
    """Fleet of mixed vehicles sums correctly."""
    fleet_result = compute_fleet_tco(
        fleet=[
            {"vehicle_type": "minibus", "motorization": "diesel", "quantity": 3},
            {"vehicle_type": "midibus", "motorization": "electric", "quantity": 2},
        ],
        duration_years=5,
    )
    assert len(fleet_result["vehicles"]) == 2
    assert fleet_result["vehicle_count"] == 5

    # Fleet total should be sum of individual tco_totals
    expected_total = sum(v["tco_total"] for v in fleet_result["vehicles"])
    assert abs(fleet_result["fleet_tco_total"] - expected_total) < 0.01


def test_tco_evolution_over_years() -> None:
    """Year-by-year fleet TCO is monotonically increasing."""
    result = calculate_tco(
        fleet=[
            {"vehicle_type": "minibus", "motorization": "diesel", "quantity": 2},
        ],
        duration_years=10,
        include_evolution=True,
        include_comparison=False,
    )
    evolution = result["evolution"]
    assert len(evolution) == 10

    totals = [e["fleet_tco_total"] for e in evolution]
    for i in range(1, len(totals)):
        assert totals[i] > totals[i - 1], (
            f"Year {i + 1} ({totals[i]}) should be > year {i} ({totals[i - 1]})"
        )


def test_tco_with_custom_overrides() -> None:
    """Override default costs and verify output changes."""
    # Default midibus diesel
    default_result = compute_fleet_tco(
        fleet=[{"vehicle_type": "midibus", "motorization": "diesel", "quantity": 1}],
        duration_years=5,
    )

    # Overridden with much higher purchase price
    override_result = compute_fleet_tco(
        fleet=[{
            "vehicle_type": "midibus",
            "motorization": "diesel",
            "quantity": 1,
            "purchase_price": 500000,
        }],
        duration_years=5,
    )

    assert override_result["fleet_tco_total"] > default_result["fleet_tco_total"]
    assert override_result["vehicles"][0]["purchase_price"] == 500000.0


# ---------------------------------------------------------------------------
# Integration test — API endpoint
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tco_endpoint_response(client: AsyncClient) -> None:
    """POST /financial/tco/calculate returns valid response structure."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        "/api/v1/financial/tco/calculate",
        headers=headers,
        json={
            "fleet": [
                {
                    "vehicle_type": "minibus",
                    "motorization": "diesel",
                    "quantity": 3,
                },
                {
                    "vehicle_type": "bus_standard",
                    "motorization": "electric",
                    "quantity": 2,
                },
            ],
            "duration_years": 5,
            "include_evolution": True,
            "include_comparison": True,
        },
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()

    # Fleet TCO
    assert "fleet_tco" in data
    fleet = data["fleet_tco"]
    assert fleet["vehicle_count"] == 5
    assert fleet["duration_years"] == 5
    assert len(fleet["vehicles"]) == 2
    assert fleet["fleet_tco_total"] > 0

    # Evolution
    assert "evolution" in data
    assert len(data["evolution"]) == 5
    assert data["evolution"][0]["year"] == 1

    # Motorization comparisons
    assert "motorization_comparisons" in data
    assert len(data["motorization_comparisons"]) == 2
    vehicle_types = [c["vehicle_type"] for c in data["motorization_comparisons"]]
    assert "minibus" in vehicle_types
    assert "bus_standard" in vehicle_types
