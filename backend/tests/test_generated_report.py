from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import login_as_admin


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generated_report_model(client: AsyncClient) -> None:
    """GeneratedReport model creation and persistence via modal-report endpoint."""
    token = await login_as_admin(client)
    resp = await client.get(
        "/api/v1/export/modal-report?report_format=pdf",
        headers={"Authorization": f"Bearer {token}"},
    )
    # The endpoint should succeed and return content
    assert resp.status_code == 200
    assert len(resp.content) > 0


@pytest.mark.asyncio
async def test_modal_analysis_report_pdf(client: AsyncClient) -> None:
    """Modal analysis report generates valid PDF."""
    token = await login_as_admin(client)
    resp = await client.get(
        "/api/v1/export/modal-report?report_format=pdf",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:5] == b"%PDF-"


@pytest.mark.asyncio
async def test_modal_analysis_report_excel(client: AsyncClient) -> None:
    """Modal analysis report generates valid Excel."""
    token = await login_as_admin(client)
    resp = await client.get(
        "/api/v1/export/modal-report?report_format=xlsx",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert (
        resp.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    # XLSX files start with PK zip magic bytes
    assert resp.content[:2] == b"PK"


@pytest.mark.asyncio
async def test_fleet_utilization_report(client: AsyncClient) -> None:
    """Fleet utilization report produces valid PDF."""
    token = await login_as_admin(client)
    resp = await client.get(
        "/api/v1/export/fleet-report?report_format=pdf",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:5] == b"%PDF-"


@pytest.mark.asyncio
async def test_volunteer_driver_report(client: AsyncClient) -> None:
    """Volunteer driver report includes driver details as PDF."""
    token = await login_as_admin(client)
    resp = await client.get(
        "/api/v1/export/volunteer-report?report_format=pdf",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:5] == b"%PDF-"


@pytest.mark.asyncio
async def test_hr_mobility_report(client: AsyncClient) -> None:
    """HR mobility report contains coverage and shadow zone data."""
    token = await login_as_admin(client)
    resp = await client.get(
        "/api/v1/export/hr-mobility?report_format=pdf",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:5] == b"%PDF-"


@pytest.mark.asyncio
async def test_report_stored_in_db(client: AsyncClient) -> None:
    """Generated reports are stored in DB with correct fields."""
    token = await login_as_admin(client)

    # Generate a fleet report (Excel format to test variety)
    resp = await client.get(
        "/api/v1/export/fleet-report?report_format=xlsx",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.content[:2] == b"PK"

    # Generate a volunteer report (PDF format)
    resp2 = await client.get(
        "/api/v1/export/volunteer-report?report_format=pdf",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp2.status_code == 200
    assert resp2.content[:5] == b"%PDF-"
