from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, EmailStr

# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role_id: uuid.UUID


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    role_id: uuid.UUID | None = None
    is_active: bool | None = None


class RoleCreate(BaseModel):
    name: str
    permissions: list[str] = []


class RoleUpdate(BaseModel):
    name: str | None = None
    permissions: list[str] | None = None


class TenantCreate(BaseModel):
    name: str
    code: str


class TenantUpdate(BaseModel):
    name: str | None = None
    config: dict | None = None
    is_active: bool | None = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    first_name: str | None
    last_name: str | None
    role_id: uuid.UUID
    tenant_id: uuid.UUID
    mfa_enabled: bool
    is_active: bool


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    permissions: list
    is_system_role: bool


class TenantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    code: str
    config: dict
    is_active: bool
