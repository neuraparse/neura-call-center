"""Conversation and message models."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.core.database import Base

if TYPE_CHECKING:
    from apps.models.call import Call
    from apps.models.claim import Claim


class MessageRole(str, enum.Enum):
    """Message role enumeration."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class Conversation(Base):
    """Conversation model for tracking call conversations."""

    __tablename__ = "conversations"

    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Foreign keys
    call_id: Mapped[UUID] = mapped_column(ForeignKey("calls.id"), unique=True, index=True)

    # Conversation metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Summary
    summary: Mapped[str | None] = mapped_column(Text)
    sentiment: Mapped[str | None] = mapped_column(Text)  # positive, negative, neutral
    satisfaction_score: Mapped[int | None] = mapped_column(Integer)  # 1-5

    # Relationships
    call: Mapped["Call"] = relationship("Call", back_populates="conversation")
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
    claim: Mapped["Claim | None"] = relationship(
        "Claim", back_populates="conversation", uselist=False
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Conversation {self.id} for Call {self.call_id}>"


class Message(Base):
    """Message model for individual conversation messages."""

    __tablename__ = "messages"

    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Foreign keys
    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversations.id"), index=True
    )

    # Message content
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole))
    content: Mapped[str] = mapped_column(Text)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    # Metadata
    message_metadata: Mapped[dict | None] = mapped_column(JSON, default=dict)

    # Tool calls (for function calling)
    tool_calls: Mapped[list | None] = mapped_column(JSON, default=list)
    tool_call_id: Mapped[str | None] = mapped_column(Text)

    # Audio metadata
    audio_duration_ms: Mapped[int | None] = mapped_column(Integer)
    audio_url: Mapped[str | None] = mapped_column(Text)

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Message {self.id} {self.role} in {self.conversation_id}>"

