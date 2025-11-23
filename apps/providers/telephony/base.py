"""Base Telephony provider interface."""

from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable

from apps.providers.base import BaseProvider


class CallStatus(str, Enum):
    """Call status enumeration."""

    INITIATED = "initiated"
    RINGING = "ringing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_ANSWER = "no_answer"
    BUSY = "busy"
    CANCELED = "canceled"


@dataclass
class Call:
    """Call information."""

    id: str
    from_number: str
    to_number: str
    status: CallStatus
    direction: str  # inbound, outbound
    started_at: datetime | None = None
    ended_at: datetime | None = None
    duration_seconds: int | None = None
    recording_url: str | None = None
    metadata: dict[str, Any] | None = None


class TelephonyProvider(BaseProvider):
    """Base class for Telephony providers."""

    @abstractmethod
    async def make_call(
        self,
        to_number: str,
        from_number: str,
        webhook_url: str,
        recording_enabled: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> Call:
        """
        Initiate an outbound call.

        Args:
            to_number: Destination phone number
            from_number: Source phone number
            webhook_url: URL for call events
            recording_enabled: Whether to record the call
            metadata: Additional metadata

        Returns:
            Call object
        """
        pass

    @abstractmethod
    async def answer_call(self, call_id: str) -> Call:
        """
        Answer an incoming call.

        Args:
            call_id: Call identifier

        Returns:
            Updated Call object
        """
        pass

    @abstractmethod
    async def hangup_call(self, call_id: str) -> Call:
        """
        Hang up a call.

        Args:
            call_id: Call identifier

        Returns:
            Updated Call object
        """
        pass

    @abstractmethod
    async def get_call(self, call_id: str) -> Call:
        """
        Get call information.

        Args:
            call_id: Call identifier

        Returns:
            Call object
        """
        pass

    @abstractmethod
    async def send_audio(self, call_id: str, audio_data: bytes) -> None:
        """
        Send audio to an active call.

        Args:
            call_id: Call identifier
            audio_data: Audio data to send
        """
        pass

    @abstractmethod
    async def receive_audio(self, call_id: str) -> bytes:
        """
        Receive audio from an active call.

        Args:
            call_id: Call identifier

        Returns:
            Audio data
        """
        pass

    @abstractmethod
    async def register_webhook(
        self,
        event_type: str,
        callback: Callable[[dict[str, Any]], None],
    ) -> None:
        """
        Register a webhook callback for events.

        Args:
            event_type: Type of event (call_started, call_ended, etc.)
            callback: Callback function
        """
        pass

    @abstractmethod
    async def get_recording(self, call_id: str) -> bytes | None:
        """
        Get call recording.

        Args:
            call_id: Call identifier

        Returns:
            Recording audio data or None
        """
        pass

