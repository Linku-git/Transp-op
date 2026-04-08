from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DeviceRegisterRequest(BaseModel):
    token: str = Field(..., min_length=1, max_length=512)
    platform: str = Field(default="android", pattern="^(android|ios)$")


class DeviceRegistrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    device_token: str
    platform: str
    last_seen: datetime | None = None
    created_at: datetime
