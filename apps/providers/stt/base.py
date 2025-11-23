"""Base Speech-to-Text provider interface."""

from abc import abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator

from apps.providers.base import BaseProvider


@dataclass
class STTResult:
    """Speech-to-Text result."""

    text: str
    confidence: float
    language: str | None = None
    duration_ms: int | None = None
    is_final: bool = True
    metadata: dict | None = None


class STTProvider(BaseProvider):
    """Base class for Speech-to-Text providers."""

    @abstractmethod
    async def transcribe(
        self,
        audio_data: bytes,
        language: str | None = None,
        sample_rate: int = 16000,
        encoding: str = "linear16",
    ) -> STTResult:
        """
        Transcribe audio data to text.

        Args:
            audio_data: Raw audio bytes
            language: Language code (e.g., 'en-US')
            sample_rate: Audio sample rate in Hz
            encoding: Audio encoding format

        Returns:
            STTResult with transcription
        """
        pass

    @abstractmethod
    async def transcribe_stream(
        self,
        audio_stream: AsyncIterator[bytes],
        language: str | None = None,
        sample_rate: int = 16000,
        encoding: str = "linear16",
    ) -> AsyncIterator[STTResult]:
        """
        Transcribe streaming audio to text.

        Args:
            audio_stream: Async iterator of audio chunks
            language: Language code (e.g., 'en-US')
            sample_rate: Audio sample rate in Hz
            encoding: Audio encoding format

        Yields:
            STTResult objects as they become available
        """
        pass

    @abstractmethod
    async def get_supported_languages(self) -> list[str]:
        """Get list of supported language codes."""
        pass

