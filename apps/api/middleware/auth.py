"""Authentication middleware for FastAPI."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.core.database import get_db
from apps.core.logging import get_logger
from apps.models.api_key import APIKey

logger = get_logger(__name__)

# API Key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(
    api_key: Optional[str] = Security(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> APIKey:
    """Validate API key from request header.

    Args:
        api_key: API key from X-API-Key header
        db: Database session

    Returns:
        APIKey: Valid API key object if found

    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Please provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Query API key from database
    try:
        result = await db.execute(
            select(APIKey).where(APIKey.key == api_key)
        )
        api_key_obj = result.scalar_one_or_none()

        if not api_key_obj:
            logger.warning("Invalid API key attempted", key_prefix=api_key[:8])
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        # Check if key is valid (active and not expired)
        if not api_key_obj.is_valid():
            logger.warning(
                "Expired or inactive API key attempted",
                key_name=api_key_obj.name,
                is_active=api_key_obj.is_active,
                expires_at=api_key_obj.expires_at,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key is expired or inactive",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        # Update last used timestamp
        api_key_obj.last_used_at = datetime.now(timezone.utc)
        await db.commit()

        logger.info(
            "API key authenticated",
            key_name=api_key_obj.name,
            owner=api_key_obj.owner,
        )

        return api_key_obj

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error validating API key", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validating API key",
        )


# Alias for easier use
require_api_key = get_api_key


def get_current_api_key(request: Request) -> Optional[APIKey]:
    """Get current API key from request state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        APIKey: Current API key if authenticated, None otherwise
    """
    return getattr(request.state, "api_key", None)

