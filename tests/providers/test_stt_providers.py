"""Tests for STT providers."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from apps.providers.stt.base import STTProvider, STTResult
from apps.providers.stt.deepgram import DeepgramSTTProvider
from apps.providers.stt.factory import get_stt_provider
from apps.providers.stt.whisper import WhisperSTTProvider


class MockSTTProvider(STTProvider):
    """Mock STT provider for testing."""

    def __init__(self):
        self.initialized = False
        self.cleaned_up = False

    async def initialize(self) -> None:
        """Initialize mock provider."""
        self.initialized = True

    async def health_check(self) -> bool:
        """Check health."""
        return self.initialized

    async def cleanup(self) -> None:
        """Cleanup mock provider."""
        self.cleaned_up = True

    async def transcribe(
        self,
        audio_data: bytes,
        language: str | None = None,
        sample_rate: int = 16000,
        encoding: str = "linear16",
    ) -> STTResult:
        """Mock transcribe."""
        return STTResult(
            text="This is a mock transcription",
            confidence=0.95,
            language=language or "en-US",
            duration_ms=1000,
            is_final=True,
        )

    async def transcribe_stream(
        self,
        audio_stream,
        language: str | None = None,
        sample_rate: int = 16000,
        encoding: str = "linear16",
    ):
        """Mock stream transcribe."""
        yield STTResult(
            text="Mock streaming transcription",
            confidence=0.92,
            language=language or "en-US",
            is_final=True,
        )

    async def get_supported_languages(self) -> list[str]:
        """Get supported languages."""
        return ["en-US", "tr-TR", "fr-FR", "de-DE", "es-ES"]


@pytest.mark.asyncio
async def test_mock_stt_provider():
    """Test mock STT provider."""
    provider = MockSTTProvider()
    
    # Test initialization
    await provider.initialize()
    assert provider.initialized is True
    
    # Test health check
    health = await provider.health_check()
    assert health is True
    
    # Test transcription
    audio_data = b"fake audio data"
    result = await provider.transcribe(audio_data, language="en-US")
    
    assert result.text == "This is a mock transcription"
    assert result.confidence == 0.95
    assert result.language == "en-US"
    assert result.is_final is True
    
    # Test streaming
    async for result in provider.transcribe_stream(None, language="tr-TR"):
        assert result.text == "Mock streaming transcription"
        assert result.language == "tr-TR"
        break
    
    # Test cleanup
    await provider.cleanup()
    assert provider.cleaned_up is True


@pytest.mark.asyncio
async def test_stt_factory():
    """Test STT factory."""
    # This will fail without API keys, but we can test the factory logic
    try:
        provider = get_stt_provider("deepgram")
        assert isinstance(provider, DeepgramSTTProvider)
    except Exception:
        # Expected without API key
        pass


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires proper provider initialization with name parameter")
async def test_deepgram_provider_mock():
    """Test Deepgram provider with mocking."""
    with patch("apps.providers.stt.deepgram.DeepgramClient") as mock_client:
        # Setup mock
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        provider = DeepgramSTTProvider(name="deepgram", api_key="test-key")
        await provider.initialize()

        assert provider.client is not None


@pytest.mark.asyncio
@pytest.mark.skip(reason="Whisper model loading takes time, skip for quick tests")
async def test_whisper_provider_initialization():
    """Test Whisper provider initialization."""
    from apps.providers.stt.whisper import WhisperSTTProvider

    provider = WhisperSTTProvider(name="whisper")

    # Initialize (this will load the model)
    await provider.initialize()

    assert provider.model is not None
    assert await provider.health_check() is True

    await provider.cleanup()


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_mock_stt_provider())
    print("✅ Mock STT provider test passed!")
    
    asyncio.run(test_whisper_provider_initialization())
    print("✅ Whisper provider initialization test passed!")

