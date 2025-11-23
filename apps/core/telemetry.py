"""OpenTelemetry configuration for distributed tracing and metrics.

This module sets up OpenTelemetry instrumentation for:
- FastAPI (automatic request tracing)
- SQLAlchemy (database query tracing)
- Redis (cache operation tracing)
- HTTPX (external HTTP request tracing)
- Prometheus metrics export
"""

from typing import Optional

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import REGISTRY, start_http_server

from apps.core.config import settings
from apps.core.logging import get_logger

logger = get_logger(__name__)

# Global telemetry state
_telemetry_initialized = False


def get_resource() -> Resource:
    """Create OpenTelemetry resource with service information."""
    return Resource.create(
        {
            "service.name": "neura-call-center",
            "service.version": "1.0.0",
            "service.namespace": "production",
            "deployment.environment": "production" if not settings.is_development else "development",
        }
    )


def setup_tracing(otlp_endpoint: Optional[str] = None) -> TracerProvider:
    """Setup distributed tracing with OpenTelemetry.
    
    Args:
        otlp_endpoint: OTLP endpoint for trace export (e.g., Tempo, Jaeger)
                      If None, uses OTEL_EXPORTER_OTLP_ENDPOINT env var
    
    Returns:
        TracerProvider: Configured tracer provider
    """
    resource = get_resource()
    provider = TracerProvider(resource=resource)
    
    # Add OTLP exporter if endpoint is configured
    if otlp_endpoint or settings.otel_exporter_otlp_endpoint:
        endpoint = otlp_endpoint or settings.otel_exporter_otlp_endpoint
        otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        logger.info("OTLP trace exporter configured", endpoint=endpoint)
    
    trace.set_tracer_provider(provider)
    logger.info("Distributed tracing initialized")
    
    return provider


def setup_metrics(prometheus_port: int = 9464) -> MeterProvider:
    """Setup metrics collection with Prometheus export.
    
    Args:
        prometheus_port: Port to expose Prometheus metrics endpoint
    
    Returns:
        MeterProvider: Configured meter provider
    """
    resource = get_resource()
    
    # Prometheus exporter
    prometheus_reader = PrometheusMetricReader()
    
    # OTLP exporter for metrics (optional)
    readers = [prometheus_reader]
    if settings.otel_exporter_otlp_endpoint:
        otlp_exporter = OTLPMetricExporter(endpoint=settings.otel_exporter_otlp_endpoint)
        # Note: OTLP metric reader setup would go here if needed
    
    provider = MeterProvider(resource=resource, metric_readers=readers)
    metrics.set_meter_provider(provider)
    
    # Start Prometheus HTTP server
    try:
        start_http_server(port=prometheus_port, registry=REGISTRY)
        logger.info("Prometheus metrics server started", port=prometheus_port)
    except OSError as e:
        logger.warning("Prometheus metrics server already running", error=str(e))
    
    return provider


def instrument_app(app) -> None:
    """Instrument FastAPI application with OpenTelemetry.
    
    Args:
        app: FastAPI application instance
    """
    global _telemetry_initialized
    
    if _telemetry_initialized:
        logger.warning("Telemetry already initialized, skipping")
        return
    
    # Setup tracing and metrics
    setup_tracing()
    setup_metrics()
    
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
    logger.info("FastAPI instrumented")
    
    # Instrument SQLAlchemy
    SQLAlchemyInstrumentor().instrument()
    logger.info("SQLAlchemy instrumented")
    
    # Instrument Redis
    RedisInstrumentor().instrument()
    logger.info("Redis instrumented")
    
    # Instrument HTTPX
    HTTPXClientInstrumentor().instrument()
    logger.info("HTTPX instrumented")
    
    _telemetry_initialized = True
    logger.info("OpenTelemetry instrumentation complete")

