"""API Key management endpoints."""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.core.database import get_db
from apps.core.logging import get_logger
from apps.models.api_key import APIKey

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/api-keys")


# Pydantic models
class APIKeyCreate(BaseModel):
    """API Key creation request."""
    
    name: str = Field(..., min_length=1, max_length=255, description="API key name")
    description: Optional[str] = Field(None, description="API key description")
    owner: str = Field(..., min_length=1, max_length=255, description="Owner name")
    owner_email: Optional[str] = Field(None, description="Owner email")
    rate_limit_per_minute: Optional[int] = Field(None, ge=1, description="Rate limit per minute")
    rate_limit_per_hour: Optional[int] = Field(None, ge=1, description="Rate limit per hour")
    rate_limit_per_day: Optional[int] = Field(None, ge=1, description="Rate limit per day")
    expires_at: Optional[datetime] = Field(None, description="Expiration datetime")


class APIKeyResponse(BaseModel):
    """API Key response."""
    
    id: int
    name: str
    description: Optional[str]
    owner: str
    owner_email: Optional[str]
    is_active: bool
    rate_limit_per_minute: Optional[int]
    rate_limit_per_hour: Optional[int]
    rate_limit_per_day: Optional[int]
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class APIKeyWithSecret(APIKeyResponse):
    """API Key response with secret key (only shown once)."""
    
    key: str


@router.post("/", response_model=APIKeyWithSecret, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: APIKeyCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new API key.
    
    **Note**: The API key secret is only shown once. Store it securely!
    """
    # Generate new API key
    key = APIKey.generate_key()
    
    # Create API key object
    api_key = APIKey(
        key=key,
        name=api_key_data.name,
        description=api_key_data.description,
        owner=api_key_data.owner,
        owner_email=api_key_data.owner_email,
        rate_limit_per_minute=api_key_data.rate_limit_per_minute,
        rate_limit_per_hour=api_key_data.rate_limit_per_hour,
        rate_limit_per_day=api_key_data.rate_limit_per_day,
        expires_at=api_key_data.expires_at,
    )
    
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    
    logger.info(
        "API key created",
        key_id=api_key.id,
        key_name=api_key.name,
        owner=api_key.owner,
    )
    
    return api_key


@router.get("/", response_model=List[APIKeyResponse])
async def list_api_keys(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List all API keys (without secrets)."""
    result = await db.execute(
        select(APIKey).offset(skip).limit(limit).order_by(APIKey.created_at.desc())
    )
    api_keys = result.scalars().all()
    
    return api_keys


@router.get("/{key_id}", response_model=APIKeyResponse)
async def get_api_key(
    key_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get API key details by ID (without secret)."""
    result = await db.execute(
        select(APIKey).where(APIKey.id == key_id)
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    
    return api_key


@router.patch("/{key_id}/deactivate", response_model=APIKeyResponse)
async def deactivate_api_key(
    key_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Deactivate an API key."""
    result = await db.execute(
        select(APIKey).where(APIKey.id == key_id)
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    
    api_key.is_active = False
    await db.commit()
    await db.refresh(api_key)
    
    logger.info("API key deactivated", key_id=key_id, key_name=api_key.name)
    
    return api_key

