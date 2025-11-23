"""Call model for tracking phone calls."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.core.database import Base

if TYPE_CHECKING:
    from apps.models.conversation import Conversation


class CallStatus(str, enum.Enum):
    """Call status enumeration."""

    INITIATED = "initiated"
    RINGING = "ringing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_ANSWER = "no_answer"
    BUSY = "busy"
    CANCELED = "canceled"


class Call(Base):
    """Call model for tracking phone calls."""

    __tablename__ = "calls"

    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Call identification
    external_id: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(String(20), index=True)
    agent_phone_number: Mapped[str] = mapped_column(String(20))

    # Call status
    status: Mapped[CallStatus] = mapped_column(
        Enum(CallStatus), default=CallStatus.INITIATED, index=True
    )
    direction: Mapped[str] = mapped_column(String(20))  # inbound, outbound

    # Timing
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[int | None] = mapped_column(Integer)

    # Call details
    language: Mapped[str] = mapped_column(String(10), default="en-US")
    recording_url: Mapped[str | None] = mapped_column(Text)
    recording_enabled: Mapped[bool] = mapped_column(default=True)

    # Metadata
    provider: Mapped[str] = mapped_column(String(50))  # twilio, vonage, etc.
    call_metadata: Mapped[dict | None] = mapped_column(JSON, default=dict)

    # Quality metrics
    audio_quality_score: Mapped[float | None] = mapped_column(Float)
    latency_ms: Mapped[int | None] = mapped_column(Integer)

    # Error tracking
    error_message: Mapped[str | None] = mapped_column(Text)
    error_code: Mapped[str | None] = mapped_column(String(50))

    # Relationships
    conversation: Mapped["Conversation | None"] = relationship(
        "Conversation", back_populates="call", uselist=False
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Call {self.id} {self.phone_number} {self.status}>"

