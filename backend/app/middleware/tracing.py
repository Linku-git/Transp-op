"""OpenTelemetry distributed tracing for Transpop API."""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Generator

logger = logging.getLogger(__name__)

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    HAS_OTEL = True
except ImportError:
    HAS_OTEL = False
    logger.warning("opentelemetry not installed — tracing disabled")

_tracer: Any = None


def setup_tracing(service_name: str = "transpop-api") -> None:
    """Initialize OpenTelemetry tracing."""
    global _tracer
    if not HAS_OTEL:
        logger.info("OpenTelemetry tracing disabled")
        return

    try:
        import os
        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)

        # OTLP exporter (Jaeger-compatible) if endpoint configured
        otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        if otlp_endpoint:
            try:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                    OTLPSpanExporter,
                )
                exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
                provider.add_span_processor(SimpleSpanProcessor(exporter))
                logger.info("OTLP trace exporter configured: %s", otlp_endpoint)
            except ImportError:
                logger.warning("OTLP exporter not available")

        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer(service_name)
        logger.info("OpenTelemetry tracing initialized for %s", service_name)
    except Exception as exc:
        logger.error("Failed to setup tracing: %s", exc)


def get_tracer() -> Any:
    """Get the configured tracer (or a no-op stub)."""
    if _tracer is not None:
        return _tracer
    if HAS_OTEL:
        return trace.get_tracer("transpop-api")
    # Return no-op
    return _NoOpTracer()


@contextmanager
def trace_span(
    name: str, attributes: dict[str, str] | None = None
) -> Generator[Any, None, None]:
    """Context manager to create a trace span."""
    tracer = get_tracer()
    if HAS_OTEL and not isinstance(tracer, _NoOpTracer):
        with tracer.start_as_current_span(name, attributes=attributes or {}) as span:
            yield span
    else:
        yield _NoOpSpan()


class _NoOpTracer:
    """No-op tracer when OpenTelemetry is not installed."""

    def start_as_current_span(self, name: str, **kw: Any) -> _NoOpSpanContext:
        return _NoOpSpanContext()


class _NoOpSpanContext:
    """No-op span context manager."""

    def __enter__(self) -> _NoOpSpan:
        return _NoOpSpan()

    def __exit__(self, *a: Any) -> None:
        pass


class _NoOpSpan:
    """No-op span that silently accepts all operations."""

    def set_attribute(self, key: str, value: Any) -> None:
        pass

    def set_status(self, status: Any) -> None:
        pass

    def add_event(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        pass
