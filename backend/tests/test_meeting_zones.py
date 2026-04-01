from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.services.clustering import ClusterResult, EmployeePoint
from app.services.meeting_zones import (
    AccessLeg,
    MeetingZone,
    optimize_meeting_zones,
)
from app.services.osrm_client import NearestResult, RouteResult, _haversine_meters
from tests.conftest import login_as_admin


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_cluster(
    employees: list[EmployeePoint],
) -> ClusterResult:
    """Build a ClusterResult from a list of employee points."""
    lats = [e.lat for e in employees]
    lngs = [e.lng for e in employees]
    return ClusterResult(
        centroid_lat=sum(lats) / len(lats),
        centroid_lng=sum(lngs) / len(lngs),
        employee_ids=[e.employee_id for e in employees],
        pmr_count=sum(1 for e in employees if e.is_pmr),
        employee_count=len(employees),
    )


def _make_point(
    lat: float = 33.57, lng: float = -7.60, is_pmr: bool = False
) -> EmployeePoint:
    return EmployeePoint(
        employee_id=uuid.uuid4(), lat=lat, lng=lng, is_pmr=is_pmr
    )


# ---------------------------------------------------------------------------
# Unit tests — meeting zone optimization (no OSRM)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_centroid_snap_to_road() -> None:
    """With OSRM mocked, centroid is snapped to nearest road."""
    emp1 = _make_point(33.570, -7.600)
    emp2 = _make_point(33.572, -7.598)
    cluster = _make_cluster([emp1, emp2])

    snapped = NearestResult(lat=33.5715, lng=-7.5995, distance_meters=12.0, road_name="Rue Test")

    with patch(
        "app.services.meeting_zones.osrm_nearest",
        new_callable=AsyncMock,
        return_value=snapped,
    ), patch(
        "app.services.meeting_zones.osrm_route",
        new_callable=AsyncMock,
        return_value=RouteResult(distance_meters=150.0, duration_seconds=120.0),
    ):
        zones = await optimize_meeting_zones(
            clusters=[cluster],
            employees=[emp1, emp2],
            max_walking_distance_meters=800.0,
            use_osrm=True,
        )

    assert len(zones) == 1
    zone = zones[0]
    # Zone should be at the snapped location, not raw centroid
    assert zone.lat == 33.5715
    assert zone.lng == -7.5995
    assert zone.road_name == "Rue Test"
    assert zone.snap_distance_meters == 12.0


@pytest.mark.asyncio
async def test_walking_distance_constraint() -> None:
    """All employees must be within max walking distance."""
    # Two close employees + one far employee
    emp_close1 = _make_point(33.570, -7.600)
    emp_close2 = _make_point(33.571, -7.601)
    emp_far = _make_point(33.590, -7.580)  # ~2.5km away

    cluster = _make_cluster([emp_close1, emp_close2, emp_far])

    zones = await optimize_meeting_zones(
        clusters=[cluster],
        employees=[emp_close1, emp_close2, emp_far],
        max_walking_distance_meters=800.0,
        use_osrm=False,
    )

    assert len(zones) == 1
    zone = zones[0]

    # At least one access leg should violate the constraint
    assert not zone.all_within_constraint
    violators = [leg for leg in zone.access_legs if not leg.within_constraint]
    assert len(violators) >= 1


@pytest.mark.asyncio
async def test_pmr_accessibility() -> None:
    """PMR clusters get accessibility flag based on snap distance."""
    pmr_emp = _make_point(33.570, -7.600, is_pmr=True)
    normal_emp = _make_point(33.571, -7.601)
    cluster = _make_cluster([pmr_emp, normal_emp])

    # Close snap = PMR accessible
    close_snap = NearestResult(lat=33.5705, lng=-7.6005, distance_meters=10.0)
    with patch(
        "app.services.meeting_zones.osrm_nearest",
        new_callable=AsyncMock,
        return_value=close_snap,
    ), patch(
        "app.services.meeting_zones.osrm_route",
        new_callable=AsyncMock,
        return_value=RouteResult(distance_meters=50.0, duration_seconds=40.0),
    ):
        zones = await optimize_meeting_zones(
            [cluster], [pmr_emp, normal_emp], use_osrm=True
        )
    assert zones[0].pmr_accessible is True

    # Far snap = NOT PMR accessible
    far_snap = NearestResult(lat=33.5705, lng=-7.6005, distance_meters=100.0)
    with patch(
        "app.services.meeting_zones.osrm_nearest",
        new_callable=AsyncMock,
        return_value=far_snap,
    ), patch(
        "app.services.meeting_zones.osrm_route",
        new_callable=AsyncMock,
        return_value=RouteResult(distance_meters=50.0, duration_seconds=40.0),
    ):
        zones = await optimize_meeting_zones(
            [cluster], [pmr_emp, normal_emp], use_osrm=True
        )
    assert zones[0].pmr_accessible is False


@pytest.mark.asyncio
async def test_employee_assignment() -> None:
    """Each employee is assigned to exactly one meeting zone."""
    emp1 = _make_point(33.570, -7.600)
    emp2 = _make_point(33.571, -7.601)
    emp3 = _make_point(33.580, -7.590)
    emp4 = _make_point(33.581, -7.591)

    cluster_a = _make_cluster([emp1, emp2])
    cluster_b = _make_cluster([emp3, emp4])

    zones = await optimize_meeting_zones(
        clusters=[cluster_a, cluster_b],
        employees=[emp1, emp2, emp3, emp4],
        use_osrm=False,
    )

    assert len(zones) == 2

    # Collect all assigned employee IDs
    all_assigned = set()
    for zone in zones:
        for leg in zone.access_legs:
            assert leg.employee_id not in all_assigned, "Employee assigned twice!"
            all_assigned.add(leg.employee_id)

    # All employees should be assigned
    expected_ids = {emp1.employee_id, emp2.employee_id, emp3.employee_id, emp4.employee_id}
    assert all_assigned == expected_ids


@pytest.mark.asyncio
async def test_access_leg_calculation() -> None:
    """Access legs have correct distance and time."""
    emp = _make_point(33.570, -7.600)
    cluster = _make_cluster([emp])

    zones = await optimize_meeting_zones(
        clusters=[cluster],
        employees=[emp],
        use_osrm=False,
    )

    assert len(zones) == 1
    assert len(zones[0].access_legs) == 1

    leg = zones[0].access_legs[0]
    assert leg.employee_id == emp.employee_id
    assert leg.walking_distance_meters >= 0
    assert leg.walking_time_seconds >= 0
    assert leg.within_constraint is True


@pytest.mark.asyncio
async def test_osrm_nearest() -> None:
    """OSRM nearest mock returns snapped coordinates."""
    from unittest.mock import MagicMock

    with patch(
        "app.services.osrm_client.httpx.AsyncClient"
    ) as mock_client_cls:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "Ok",
            "waypoints": [
                {
                    "location": [-7.599, 33.571],
                    "distance": 15.5,
                    "name": "Avenue Hassan II",
                }
            ],
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        from app.services.osrm_client import osrm_nearest

        result = await osrm_nearest(33.570, -7.600)

    assert result.lat == 33.571
    assert result.lng == -7.599
    assert result.distance_meters == 15.5
    assert result.road_name == "Avenue Hassan II"


@pytest.mark.asyncio
async def test_osrm_route() -> None:
    """OSRM route mock returns distance and duration."""
    from unittest.mock import MagicMock

    with patch(
        "app.services.osrm_client.httpx.AsyncClient"
    ) as mock_client_cls:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": "Ok",
            "routes": [
                {
                    "distance": 450.0,
                    "duration": 360.0,
                    "geometry": "encodedPolyline",
                }
            ],
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        from app.services.osrm_client import osrm_route

        result = await osrm_route(33.570, -7.600, 33.575, -7.595)

    assert result.distance_meters == 450.0
    assert result.duration_seconds == 360.0
    assert result.geometry == "encodedPolyline"
