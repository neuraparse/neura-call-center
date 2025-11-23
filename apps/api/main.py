"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.api.middleware import setup_rate_limiting, setup_security_headers
from apps.api.routers import api_keys, calls, health, streaming, webhooks
from apps.core.config import settings
from apps.core.database import close_db, init_db
from apps.core.logging import get_logger, setup_logging
from apps.core.telemetry import instrument_app

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Neura Call Center API", env=settings.app_env.value)
    
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise

    yield

    # Shutdown
    logger.info("Shutting down Neura Call Center API")
    await close_db()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Modern, platform-agnostic AI-powered call center solution",
    version="0.1.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan,
)

# OpenTelemetry instrumentation (must be before other middleware)
if settings.enable_tracing or settings.enable_metrics:
    instrument_app(app)
    logger.info("OpenTelemetry instrumentation enabled")

# Security middleware
setup_security_headers(app)

# Rate limiting
setup_rate_limiting(app)

# CORS middleware
if settings.cors_enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(api_keys.router, tags=["API Keys"])
app.include_router(calls.router, prefix="/api/v1/calls", tags=["Calls"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(streaming.router, tags=["Streaming"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "environment": settings.app_env.value,
        "docs": "/docs" if settings.is_development else None,
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint (placeholder)."""
    # TODO: Implement Prometheus metrics with prometheus_client
    return {
        "status": "ok",
        "message": "Metrics endpoint - Prometheus integration pending"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.is_development else "An error occurred",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "apps.api.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.is_development,
        log_level=settings.app_log_level.lower(),
    )

