"""API Key model for authentication."""

import secrets
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.core.database import Base


class APIKey(Base):
    """API Key model for authentication.
    
    Stores API keys for external service authentication.
    Each key can have specific permissions and rate limits.
    """

    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Key information
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Owner information
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Rate limiting
    rate_limit_per_minute: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rate_limit_per_hour: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rate_limit_per_day: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Permissions (JSON array of allowed endpoints/actions)
    permissions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    @staticmethod
    def generate_key() -> str:
        """Generate a secure random API key.
        
        Returns:
            str: A 64-character hexadecimal API key
        """
        return secrets.token_hex(32)

    def is_valid(self) -> bool:
        """Check if the API key is valid.
        
        Returns:
            bool: True if the key is active and not expired
        """
        if not self.is_active:
            return False
        
        if self.expires_at and datetime.now(timezone.utc) > self.expires_at:
            return False
        
        return True

    def __repr__(self) -> str:
        """String representation."""
        return f"<APIKey(name='{self.name}', owner='{self.owner}', active={self.is_active})>"

