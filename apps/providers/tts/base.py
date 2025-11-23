"""Base Text-to-Speech provider interface."""

from abc import abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator

from apps.providers.base import BaseProvider


@dataclass
class TTSResult:
    """Text-to-Speech result."""

    audio_data: bytes
    format: str  # mp3, wav, ogg, etc.
    sample_rate: int
    duration_ms: int | None = None
    metadata: dict | None = None


class TTSProvider(BaseProvider):
    """Base class for Text-to-Speech providers."""

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice_id: str | None = None,
        language: str | None = None,
        speed: float = 1.0,
        output_format: str = "mp3",
    ) -> TTSResult:
        """
        Synthesize text to speech.

        Args:
            text: Text to synthesize
            voice_id: Voice identifier
            language: Language code (e.g., 'en-US')
            speed: Speech speed (0.5 to 2.0)
            output_format: Audio format (mp3, wav, ogg)

        Returns:
            TTSResult with audio data
        """
        pass

    @abstractmethod
    async def synthesize_stream(
        self,
        text: str,
        voice_id: str | None = None,
        language: str | None = None,
        speed: float = 1.0,
        output_format: str = "mp3",
    ) -> AsyncIterator[bytes]:
        """
        Synthesize text to speech with streaming.

        Args:
            text: Text to synthesize
            voice_id: Voice identifier
            language: Language code (e.g., 'en-US')
            speed: Speech speed (0.5 to 2.0)
            output_format: Audio format (mp3, wav, ogg)

        Yields:
            Audio chunks as they become available
        """
        pass

    @abstractmethod
    async def get_available_voices(self, language: str | None = None) -> list[dict]:
        """
        Get available voices.

        Args:
            language: Filter by language code

        Returns:
            List of voice information dictionaries
        """
        pass

    @abstractmethod
    async def get_supported_languages(self) -> list[str]:
        """Get list of supported language codes."""
        pass

