"""Deepgram Speech-to-Text provider implementation.

Uses Deepgram SDK v5.x (2025 latest version).
Documentation: https://developers.deepgram.com/docs/
"""

import asyncio
from typing import AsyncIterator

from deepgram import DeepgramClient
from deepgram.core.api_error import ApiError

from apps.core.logging import get_logger
from apps.providers.base import ProviderError
from apps.providers.stt.base import STTProvider, STTResult

logger = get_logger(__name__)


class DeepgramSTTProvider(STTProvider):
    """Deepgram Speech-to-Text provider."""

    def __init__(self, name: str, api_key: str):
        """Initialize Deepgram provider."""
        super().__init__(name, api_key=api_key)
        self.api_key = api_key
        self.client: DeepgramClient | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the Deepgram client."""
        if self._initialized:
            return

        try:
            # Initialize with just API key (newer SDK version)
            self.client = DeepgramClient(api_key=self.api_key)
            self._initialized = True
            logger.info("Deepgram STT provider initialized")
        except Exception as e:
            raise ProviderError(
                f"Failed to initialize Deepgram: {e}",
                provider=self.name,
                original_error=e,
            )

    async def health_check(self) -> bool:
        """Check if Deepgram is available."""
        if not self._initialized:
            return False
        try:
            # Simple check - if client is initialized, assume healthy
            return self.client is not None
        except Exception as e:
            logger.error("Deepgram health check failed", error=str(e))
            return False

    async def cleanup(self) -> None:
        """Cleanup Deepgram resources."""
        self.client = None
        self._initialized = False
        logger.info("Deepgram STT provider cleaned up")

    async def transcribe(
        self,
        audio_data: bytes,
        language: str | None = None,
        sample_rate: int = 16000,
        encoding: str = "linear16",
    ) -> STTResult:
        """Transcribe audio data using Deepgram.

        Uses Deepgram SDK v5.x API:
        client.listen.v1.media.transcribe_file()
        """
        if not self._initialized or not self.client:
            await self.initialize()

        try:
            # Transcribe using v5 SDK
            # Reference: https://developers.deepgram.com/docs/pre-recorded-audio
            response = await asyncio.to_thread(
                self.client.listen.v1.media.transcribe_file,
                request=audio_data,
                model="nova-3",  # Latest model (2025)
                smart_format=True,
                punctuate=True,
                language=language or "en-US",
            )

            # Extract result
            if not response or not response.results:
                raise ProviderError("No transcription results", provider=self.name)

            channel = response.results.channels[0]
            alternative = channel.alternatives[0]

            return STTResult(
                text=alternative.transcript,
                confidence=alternative.confidence,
                language=language,
                is_final=True,
                metadata={
                    "model": "nova-3",
                    "provider": "deepgram",
                },
            )

        except ApiError as e:
            raise ProviderError(
                f"Deepgram API error: {e.status_code} - {e.body}",
                provider=self.name,
                original_error=e,
            )
        except Exception as e:
            raise ProviderError(
                f"Transcription failed: {e}",
                provider=self.name,
                original_error=e,
            )

    async def transcribe_stream(
        self,
        audio_stream: AsyncIterator[bytes],
        language: str | None = None,
        sample_rate: int = 16000,
        encoding: str = "linear16",
    ) -> AsyncIterator[STTResult]:
        """Transcribe streaming audio using Deepgram.

        Uses Deepgram SDK v5.x WebSocket API (Listen v2):
        client.listen.v2.connect()

        Reference: https://developers.deepgram.com/docs/live-streaming-audio
        """
        if not self._initialized or not self.client:
            await self.initialize()

        try:
            from deepgram.core.events import EventType

            # Results queue
            results_queue: asyncio.Queue[STTResult | None] = asyncio.Queue()

            # Create WebSocket connection using v2 API (flux model)
            async with self.client.listen.v2.connect(
                model="flux-general-en",  # Latest streaming model (2025)
                encoding=encoding,
                sample_rate=str(sample_rate),
                language=language or "en-US",
                smart_format=True,
                punctuate=True,
            ) as connection:

                # Event handlers
                def on_message(message):
                    """Handle transcription results."""
                    try:
                        if hasattr(message, 'channel') and message.channel:
                            if hasattr(message.channel, 'alternatives') and message.channel.alternatives:
                                alternative = message.channel.alternatives[0]
                                if alternative.transcript:
                                    asyncio.create_task(
                                        results_queue.put(
                                            STTResult(
                                                text=alternative.transcript,
                                                confidence=getattr(alternative, 'confidence', 0.0),
                                                language=language,
                                                is_final=getattr(message, 'is_final', False),
                                                metadata={"provider": "deepgram", "model": "flux-general-en"},
                                            )
                                        )
                                    )
                    except Exception as e:
                        logger.error("Error processing Deepgram message", error=str(e))

                def on_error(error):
                    """Handle errors."""
                    logger.error("Deepgram streaming error", error=str(error))
                    asyncio.create_task(results_queue.put(None))

                def on_close(_):
                    """Handle connection close."""
                    logger.info("Deepgram connection closed")
                    asyncio.create_task(results_queue.put(None))

                # Register event handlers
                connection.on(EventType.MESSAGE, on_message)
                connection.on(EventType.ERROR, on_error)
                connection.on(EventType.CLOSE, on_close)

                # Start listening
                await connection.start_listening()

                # Stream audio
                async def stream_audio():
                    """Stream audio to Deepgram."""
                    try:
                        async for chunk in audio_stream:
                            connection.send(chunk)
                    except Exception as e:
                        logger.error("Error streaming audio to Deepgram", error=str(e))
                    finally:
                        await results_queue.put(None)

                # Start streaming task
                stream_task = asyncio.create_task(stream_audio())

                # Yield results
                try:
                    while True:
                        result = await results_queue.get()
                        if result is None:
                            break
                        yield result
                finally:
                    stream_task.cancel()
                    try:
                        await stream_task
                    except asyncio.CancelledError:
                        pass

        except ApiError as e:
            raise ProviderError(
                f"Deepgram API error: {e.status_code} - {e.body}",
                provider=self.name,
                original_error=e,
            )
        except Exception as e:
            raise ProviderError(
                f"Streaming transcription failed: {e}",
                provider=self.name,
                original_error=e,
            )

    async def get_supported_languages(self) -> list[str]:
        """Get supported languages."""
        return [
            "en-US", "en-GB", "en-AU", "en-NZ", "en-IN",
            "es-ES", "es-419", "fr-FR", "fr-CA", "de-DE",
            "it-IT", "pt-BR", "pt-PT", "nl-NL", "tr-TR",
            "ja-JP", "ko-KR", "zh-CN", "zh-TW", "ru-RU",
        ]

