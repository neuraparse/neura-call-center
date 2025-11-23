"""Rate limiting middleware using SlowAPI."""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.requests import Request

from apps.core.config import settings
from apps.core.logging import get_logger

logger = get_logger(__name__)


def get_identifier(request: Request) -> str:
    """Get identifier for rate limiting.
    
    Uses API key if available, otherwise falls back to IP address.
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: Identifier for rate limiting
    """
    # Try to get API key from request state
    api_key = getattr(request.state, "api_key", None)
    if api_key:
        identifier = f"apikey:{api_key.name}"
        logger.debug("Rate limit identifier from API key", identifier=identifier)
        return identifier
    
    # Fall back to IP address
    ip_address = get_remote_address(request)
    identifier = f"ip:{ip_address}"
    logger.debug("Rate limit identifier from IP", identifier=identifier)
    return identifier


# Create limiter instance
limiter = Limiter(
    key_func=get_identifier,
    default_limits=["100/minute", "1000/hour"],
    storage_uri=str(settings.cache_url) if settings.cache_url else "memory://",
    strategy="fixed-window",
    headers_enabled=True,
)


def setup_rate_limiting(app):
    """Setup rate limiting for FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    logger.info(
        "Rate limiting configured",
        storage=str(settings.cache_url) if settings.cache_url else "memory",
        default_limits=["100/minute", "1000/hour"],
    )

