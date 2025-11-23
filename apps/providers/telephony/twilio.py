"""Twilio Telephony provider implementation."""

from datetime import datetime
from typing import Any, Callable

from twilio.rest import Client

from apps.core.logging import get_logger
from apps.providers.base import ProviderError
from apps.providers.telephony.base import Call, CallStatus, TelephonyProvider

logger = get_logger(__name__)


class TwilioTelephonyProvider(TelephonyProvider):
    """Twilio Telephony provider."""

    def __init__(
        self,
        name: str,
        account_sid: str,
        auth_token: str,
        phone_number: str | None = None,
    ):
        """Initialize Twilio provider."""
        super().__init__(name, account_sid=account_sid, auth_token=auth_token)
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.phone_number = phone_number
        self.client: Client | None = None
        self._initialized = False
        self._webhooks: dict[str, list[Callable]] = {}

    async def initialize(self) -> None:
        """Initialize the Twilio client."""
        if self._initialized:
            return

        try:
            self.client = Client(self.account_sid, self.auth_token)
            self._initialized = True
            logger.info("Twilio telephony provider initialized")
        except Exception as e:
            raise ProviderError(
                f"Failed to initialize Twilio: {e}",
                provider=self.name,
                original_error=e,
            )

    async def health_check(self) -> bool:
        """Check if Twilio is available."""
        if not self._initialized or not self.client:
            return False
        try:
            # Try to fetch account info
            self.client.api.accounts(self.account_sid).fetch()
            return True
        except Exception as e:
            logger.error("Twilio health check failed", error=str(e))
            return False

    async def cleanup(self) -> None:
        """Cleanup Twilio resources."""
        self.client = None
        self._initialized = False
        self._webhooks.clear()
        logger.info("Twilio telephony provider cleaned up")

    def _map_twilio_status(self, twilio_status: str) -> CallStatus:
        """Map Twilio call status to our CallStatus enum."""
        status_map = {
            "queued": CallStatus.INITIATED,
            "ringing": CallStatus.RINGING,
            "in-progress": CallStatus.IN_PROGRESS,
            "completed": CallStatus.COMPLETED,
            "failed": CallStatus.FAILED,
            "busy": CallStatus.BUSY,
            "no-answer": CallStatus.NO_ANSWER,
            "canceled": CallStatus.CANCELED,
        }
        return status_map.get(twilio_status, CallStatus.FAILED)

    def _twilio_call_to_call(self, twilio_call: Any) -> Call:
        """Convert Twilio call object to our Call object."""
        return Call(
            id=twilio_call.sid,
            from_number=twilio_call.from_formatted or twilio_call.from_,
            to_number=twilio_call.to_formatted or twilio_call.to,
            status=self._map_twilio_status(twilio_call.status),
            direction=twilio_call.direction,
            started_at=twilio_call.start_time,
            ended_at=twilio_call.end_time,
            duration_seconds=int(twilio_call.duration) if twilio_call.duration else None,
            recording_url=None,  # Will be populated separately
            metadata={
                "price": twilio_call.price,
                "price_unit": twilio_call.price_unit,
            },
        )

    async def make_call(
        self,
        to_number: str,
        from_number: str,
        webhook_url: str,
        recording_enabled: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> Call:
        """Initiate an outbound call using Twilio."""
        if not self._initialized or not self.client:
            await self.initialize()

        try:
            # Create call
            twilio_call = self.client.calls.create(
                to=to_number,
                from_=from_number,
                url=webhook_url,
                record=recording_enabled,
                status_callback=f"{webhook_url}/status",
                status_callback_event=["initiated", "ringing", "answered", "completed"],
            )

            logger.info(
                "Outbound call initiated",
                call_id=twilio_call.sid,
                to=to_number,
                from_=from_number,
            )

            return self._twilio_call_to_call(twilio_call)

        except Exception as e:
            raise ProviderError(
                f"Failed to make call: {e}",
                provider=self.name,
                original_error=e,
            )

    async def answer_call(self, call_id: str) -> Call:
        """Answer an incoming call."""
        # Twilio handles answering automatically via TwiML
        return await self.get_call(call_id)

    async def hangup_call(self, call_id: str) -> Call:
        """Hang up a call."""
        if not self._initialized or not self.client:
            await self.initialize()

        try:
            twilio_call = self.client.calls(call_id).update(status="completed")
            logger.info("Call hung up", call_id=call_id)
            return self._twilio_call_to_call(twilio_call)

        except Exception as e:
            raise ProviderError(
                f"Failed to hang up call: {e}",
                provider=self.name,
                original_error=e,
            )

    async def get_call(self, call_id: str) -> Call:
        """Get call information."""
        if not self._initialized or not self.client:
            await self.initialize()

        try:
            twilio_call = self.client.calls(call_id).fetch()
            return self._twilio_call_to_call(twilio_call)

        except Exception as e:
            raise ProviderError(
                f"Failed to get call: {e}",
                provider=self.name,
                original_error=e,
            )

    async def send_audio(self, call_id: str, audio_data: bytes) -> None:
        """Send audio to an active call."""
        # Twilio uses Media Streams for real-time audio
        # This would require WebSocket connection
        raise NotImplementedError("Real-time audio streaming requires WebSocket implementation")

    async def receive_audio(self, call_id: str) -> bytes:
        """Receive audio from an active call."""
        # Twilio uses Media Streams for real-time audio
        raise NotImplementedError("Real-time audio streaming requires WebSocket implementation")

    async def register_webhook(
        self,
        event_type: str,
        callback: Callable[[dict[str, Any]], None],
    ) -> None:
        """Register a webhook callback."""
        if event_type not in self._webhooks:
            self._webhooks[event_type] = []
        self._webhooks[event_type].append(callback)
        logger.info("Webhook registered", event_type=event_type)

    async def get_recording(self, call_id: str) -> bytes | None:
        """Get call recording."""
        if not self._initialized or not self.client:
            await self.initialize()

        try:
            recordings = self.client.recordings.list(call_sid=call_id, limit=1)
            if not recordings:
                return None

            recording = recordings[0]
            # Download recording
            recording_url = f"https://api.twilio.com{recording.uri.replace('.json', '.mp3')}"
            # TODO: Download the recording
            logger.info("Recording found", call_id=call_id, recording_id=recording.sid)
            return None  # Placeholder

        except Exception as e:
            logger.error("Failed to get recording", call_id=call_id, error=str(e))
            return None

