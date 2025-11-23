"""ElevenLabs Text-to-Speech provider implementation."""

from typing import AsyncIterator

from elevenlabs import VoiceSettings
from elevenlabs.client import AsyncElevenLabs

from apps.core.logging import get_logger
from apps.providers.base import ProviderError
from apps.providers.tts.base import TTSProvider, TTSResult

logger = get_logger(__name__)


class ElevenLabsTTSProvider(TTSProvider):
    """ElevenLabs Text-to-Speech provider."""

    def __init__(self, name: str, api_key: str, voice_id: str):
        """Initialize ElevenLabs provider."""
        super().__init__(name, api_key=api_key, voice_id=voice_id)
        self.api_key = api_key
        self.default_voice_id = voice_id
        self.client: AsyncElevenLabs | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the ElevenLabs client."""
        if self._initialized:
            return

        try:
            self.client = AsyncElevenLabs(api_key=self.api_key)
            self._initialized = True
            logger.info("ElevenLabs TTS provider initialized")
        except Exception as e:
            raise ProviderError(
                f"Failed to initialize ElevenLabs: {e}",
                provider=self.name,
                original_error=e,
            )

    async def health_check(self) -> bool:
        """Check if ElevenLabs is available."""
        if not self._initialized or not self.client:
            return False
        try:
            # Try to get voices as a health check
            await self.client.voices.get_all()
            return True
        except Exception as e:
            logger.error("ElevenLabs health check failed", error=str(e))
            return False

    async def cleanup(self) -> None:
        """Cleanup ElevenLabs resources."""
        self.client = None
        self._initialized = False
        logger.info("ElevenLabs TTS provider cleaned up")

    async def synthesize(
        self,
        text: str,
        voice_id: str | None = None,
        language: str | None = None,
        speed: float = 1.0,
        output_format: str = "mp3",
    ) -> TTSResult:
        """Synthesize text to speech using ElevenLabs."""
        if not self._initialized or not self.client:
            await self.initialize()

        try:
            voice_id = voice_id or self.default_voice_id

            # Generate audio
            audio_generator = await self.client.generate(
                text=text,
                voice=voice_id,
                model="eleven_turbo_v2_5",  # Fastest model
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.0,
                    use_speaker_boost=True,
                ),
            )

            # Collect all audio chunks
            audio_chunks = []
            async for chunk in audio_generator:
                if chunk:
                    audio_chunks.append(chunk)

            audio_data = b"".join(audio_chunks)

            return TTSResult(
                audio_data=audio_data,
                format=output_format,
                sample_rate=44100,  # ElevenLabs default
                metadata={
                    "provider": "elevenlabs",
                    "voice_id": voice_id,
                    "model": "eleven_turbo_v2_5",
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
            voice_id = voice_id or self.default_voice_id

            # Generate audio stream
            audio_generator = await self.client.generate(
                text=text,
                voice=voice_id,
                model="eleven_turbo_v2_5",
                stream=True,
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.0,
                    use_speaker_boost=True,
                ),
            )

            async for chunk in audio_generator:
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
        if not self._initialized or not self.client:
            await self.initialize()

        try:
            voices_response = await self.client.voices.get_all()
            voices = []

            for voice in voices_response.voices:
                voice_info = {
                    "id": voice.voice_id,
                    "name": voice.name,
                    "category": voice.category,
                    "labels": voice.labels,
                }
                voices.append(voice_info)

            return voices

        except Exception as e:
            raise ProviderError(
                f"Failed to get voices: {e}",
                provider=self.name,
                original_error=e,
            )

    async def get_supported_languages(self) -> list[str]:
        """Get supported languages."""
        # ElevenLabs supports 29+ languages
        return [
            "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl",
            "cs", "ar", "zh", "ja", "ko", "hi", "sv", "da", "fi", "no",
        ]

