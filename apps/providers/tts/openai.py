"""OpenAI Text-to-Speech provider implementation."""

from typing import AsyncIterator

from openai import AsyncOpenAI

from apps.core.logging import get_logger
from apps.providers.base import ProviderError
from apps.providers.tts.base import TTSProvider, TTSResult

logger = get_logger(__name__)


class OpenAITTSProvider(TTSProvider):
    """OpenAI Text-to-Speech provider."""

    def __init__(self, name: str, api_key: str, model: str = "tts-1-hd", voice: str = "alloy"):
        """Initialize OpenAI TTS provider."""
        super().__init__(name, api_key=api_key, model=model, voice=voice)
        self.api_key = api_key
        self.model = model
        self.default_voice = voice
        self.client: AsyncOpenAI | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the OpenAI client."""
        if self._initialized:
            return

        try:
            self.client = AsyncOpenAI(api_key=self.api_key)
            self._initialized = True
            logger.info("OpenAI TTS provider initialized")
        except Exception as e:
            raise ProviderError(
                f"Failed to initialize OpenAI TTS: {e}",
                provider=self.name,
                original_error=e,
            )

    async def health_check(self) -> bool:
        """Check if OpenAI TTS is available."""
        if not self._initialized or not self.client:
            return False
        try:
            # Simple check - if client is initialized, assume healthy
            return True
        except Exception as e:
            logger.error("OpenAI TTS health check failed", error=str(e))
            return False

    async def cleanup(self) -> None:
        """Cleanup OpenAI resources."""
        if self.client:
            await self.client.close()
        self.client = None
        self._initialized = False
        logger.info("OpenAI TTS provider cleaned up")

    async def synthesize(
        self,
        text: str,
        voice_id: str | None = None,
        language: str | None = None,
        speed: float = 1.0,
        output_format: str = "mp3",
    ) -> TTSResult:
        """Synthesize text to speech using OpenAI."""
        if not self._initialized or not self.client:
            await self.initialize()

        try:
            voice = voice_id or self.default_voice

            # Generate audio
            response = await self.client.audio.speech.create(
                model=self.model,
                voice=voice,
                input=text,
                speed=speed,
                response_format=output_format,
            )

            # Read audio data
            audio_data = response.content

            return TTSResult(
                audio_data=audio_data,
                format=output_format,
                sample_rate=24000,  # OpenAI default
                metadata={
                    "provider": "openai",
                    "model": self.model,
                    "voice": voice,
                },
            )

        except Exception as e:
            raise ProviderError(
                f"Speech synthesis failed: {e}",
                provider=self.name,
                original_error=e,
            )

    async def synthesize_stream(
        self,
        text: str,
        voice_id: str | None = None,
        language: str | None = None,
        speed: float = 1.0,
        output_format: str = "mp3",
    ) -> AsyncIterator[bytes]:
        """Synthesize text to speech with streaming."""
        if not self._initialized or not self.client:
            await self.initialize()

        try:
            voice = voice_id or self.default_voice

            # Generate audio stream
            response = await self.client.audio.speech.create(
                model=self.model,
                voice=voice,
                input=text,
                speed=speed,
                response_format=output_format,
            )

            # Stream audio chunks
            async for chunk in response.iter_bytes(chunk_size=4096):
                if chunk:
                    yield chunk

        except Exception as e:
            raise ProviderError(
                f"Streaming synthesis failed: {e}",
                provider=self.name,
                original_error=e,
            )

    async def get_available_voices(self, language: str | None = None) -> list[dict]:
        """Get available voices."""
        # OpenAI has 6 preset voices
        voices = [
            {"id": "alloy", "name": "Alloy", "gender": "neutral"},
            {"id": "echo", "name": "Echo", "gender": "male"},
            {"id": "fable", "name": "Fable", "gender": "neutral"},
            {"id": "onyx", "name": "Onyx", "gender": "male"},
            {"id": "nova", "name": "Nova", "gender": "female"},
            {"id": "shimmer", "name": "Shimmer", "gender": "female"},
        ]
        return voices

    async def get_supported_languages(self) -> list[str]:
        """Get supported languages."""
        # OpenAI TTS supports many languages
        return [
            "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl",
            "cs", "ar", "zh", "ja", "ko", "hi", "sv", "da", "fi", "no",
        ]

