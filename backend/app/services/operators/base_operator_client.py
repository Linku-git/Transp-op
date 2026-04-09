"""Base class for external transport operator API clients."""
from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
INITIAL_BACKOFF = 1.0
BACKOFF_MULTIPLIER = 2.0


@dataclass
class SizingPlanPayload:
    """Standardized sizing plan data for operator transmission."""
    plan_id: str
    version: int
    vehicles: list[dict] = field(default_factory=list)
    routes: list[dict] = field(default_factory=list)
    schedules: list[dict] = field(default_factory=list)
    passenger_counts: dict = field(default_factory=dict)
    pmr_requirements: dict = field(default_factory=dict)
    rti_targets: dict = field(default_factory=dict)


@dataclass
class OperatorResponse:
    """Standardized response from operator API."""
    success: bool
    reference_id: str | None = None
    message: str = ""
    data: dict | None = None


class OperatorAPIError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class BaseOperatorClient(ABC):
    """Abstract base for transport operator API integrations."""

    def __init__(self, config: dict) -> None:
        self.config = config
        self.provider_name: str = "base"
        self._authenticated: bool = False

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the operator API."""

    @abstractmethod
    async def send_sizing_plan(self, payload: SizingPlanPayload) -> OperatorResponse:
        """Transmit a sizing plan to the operator."""

    @abstractmethod
    async def get_schedules(self) -> list[dict]:
        """Fetch current schedules from the operator."""

    @abstractmethod
    async def get_capacity(self) -> dict:
        """Fetch capacity data from the operator."""

    @abstractmethod
    async def get_routes(self) -> list[dict]:
        """Fetch route data from the operator."""

    @abstractmethod
    def format_sizing_plan(self, payload: SizingPlanPayload) -> dict:
        """Convert sizing plan to operator-specific format."""

    @abstractmethod
    def validate_format(self, data: dict) -> list[str]:
        """Validate data format before transmission. Returns list of errors."""

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated

    async def _request_with_retry(self, operation: str, func, *args, **kwargs) -> any:
        """Execute with retry and exponential backoff."""
        backoff = INITIAL_BACKOFF
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return await func(*args, **kwargs)
            except OperatorAPIError as e:
                if attempt == MAX_RETRIES:
                    raise
                if e.status_code and e.status_code < 500 and e.status_code != 429:
                    raise
                logger.warning(
                    "%s: %s attempt %d/%d failed: %s",
                    self.provider_name, operation, attempt, MAX_RETRIES, e,
                )
                await asyncio.sleep(backoff)
                backoff *= BACKOFF_MULTIPLIER
        return None
