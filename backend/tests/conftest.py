from __future__ import annotations

import os
from collections.abc import AsyncGenerator

# Set TESTING before importing app
os.environ["TESTING"] = "1"

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def login_as_admin(client: AsyncClient) -> str:
    """Helper: login as admin and return the access token."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@transpop.dev", "password": "admin123"},
    )
    return response.json()["access_token"]
