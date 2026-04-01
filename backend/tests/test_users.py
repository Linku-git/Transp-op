from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.utils.security import create_access_token
from tests.conftest import login_as_admin


@pytest.mark.asyncio
async def test_rbac_admin_access(client: AsyncClient) -> None:
    """Admin can access user management."""
    token = await login_as_admin(client)
    response = await client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_rbac_salarie_blocked(client: AsyncClient) -> None:
    """Non-admin token with fake user_id gets 401 (not found in DB)."""
    token = create_access_token({
        "sub": "00000000-0000-0000-0000-000000000099",
        "tenant_id": "00000000-0000-0000-0000-000000000000",
        "role": "salarie",
    })
    response = await client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {token}"},
    )
    # 401 because user doesn't exist in DB
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient) -> None:
    """Admin creates a new user."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Get roles to find salarie role_id
    roles_resp = await client.get("/api/v1/roles/", headers=headers)
    assert roles_resp.status_code == 200
    roles = roles_resp.json()
    salarie_role = next((r for r in roles if r["name"] == "salarie"), None)
    assert salarie_role is not None

    response = await client.post(
        "/api/v1/users/",
        headers=headers,
        json={
            "email": "testuser@transpop.dev",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "role_id": salarie_role["id"],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@transpop.dev"
    assert data["first_name"] == "Test"
    assert data["is_active"] is True
