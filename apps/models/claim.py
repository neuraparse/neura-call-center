"""Claim model for tracking customer claims/tickets."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSON, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.core.database import Base

if TYPE_CHECKING:
    from apps.models.conversation import Conversation


class Claim(Base):
    """Claim model for tracking customer claims and tickets."""

    __tablename__ = "claims"

    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Foreign keys
    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversations.id"), unique=True, index=True
    )

    # Claim data (flexible JSON structure)
    data: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Status
    status: Mapped[str] = mapped_column(Text, default="open")  # open, in_progress, resolved, closed

    # Timing
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Reminders and follow-ups
    reminders: Mapped[list] = mapped_column(JSON, default=list)
    next_action: Mapped[str | None] = mapped_column(Text)
    next_action_due: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="claim")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Claim {self.id} {self.status}>"

