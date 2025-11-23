"""Whisper Speech-to-Text provider implementation (local)."""

import asyncio
import io
import tempfile
from typing import AsyncIterator, Literal

import whisper

from apps.core.logging import get_logger
from apps.providers.base import ProviderError
from apps.providers.stt.base import STTProvider, STTResult

logger = get_logger(__name__)


class WhisperSTTProvider(STTProvider):
    """Whisper Speech-to-Text provider (local/self-hosted)."""

    def __init__(
        self,
        name: str,
        model: Literal["tiny", "base", "small", "medium", "large"] = "base",
        device: Literal["cpu", "cuda"] = "cpu",
    ):
        """Initialize Whisper provider."""
        super().__init__(name, model=model, device=device)
        self.model_name = model
        self.device = device
        self.model: whisper.Whisper | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the Whisper model."""
        if self._initialized:
            return

        try:
            logger.info(
                "Loading Whisper model",
                model=self.model_name,
                device=self.device,
            )
            # Load model in thread to avoid blocking
            self.model = await asyncio.to_thread(
                whisper.load_model,
                self.model_name,
                device=self.device,
            )
            self._initialized = True
            logger.info("Whisper STT provider initialized")
        except Exception as e:
            raise ProviderError(
                f"Failed to initialize Whisper: {e}",
                provider=self.name,
                original_error=e,
            )

    async def health_check(self) -> bool:
        """Check if Whisper is available."""
        return self._initialized and self.model is not None

    async def cleanup(self) -> None:
        """Cleanup Whisper resources."""
        self.model = None
        self._initialized = False
        logger.info("Whisper STT provider cleaned up")

    async def transcribe(
        self,
        audio_data: bytes,
        language: str | None = None,
        sample_rate: int = 16000,
        encoding: str = "linear16",
    ) -> STTResult:
        """Transcribe audio data using Whisper."""
        if not self._initialized or not self.model:
            await self.initialize()

        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name

            # Transcribe
            result = await asyncio.to_thread(
                self.model.transcribe,
                temp_path,
                language=language[:2] if language else None,  # Whisper uses 2-letter codes
                fp16=False if self.device == "cpu" else True,
            )

            return STTResult(
                text=result["text"].strip(),
                confidence=1.0,  # Whisper doesn't provide confidence scores
                language=result.get("language"),
                is_final=True,
                metadata={
                    "model": self.model_name,
                    "provider": "whisper",
                },
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
        """
        Transcribe streaming audio using Whisper.
        
        Note: Whisper doesn't natively support streaming, so we buffer chunks
        and transcribe them in batches.
        """
        if not self._initialized or not self.model:
            await self.initialize()

        buffer = io.BytesIO()
        chunk_size = sample_rate * 2 * 5  # 5 seconds of audio (16-bit = 2 bytes per sample)

        try:
            async for chunk in audio_stream:
                buffer.write(chunk)

                # Process when we have enough data
                if buffer.tell() >= chunk_size:
                    audio_data = buffer.getvalue()
                    buffer = io.BytesIO()  # Reset buffer

                    # Transcribe chunk
                    result = await self.transcribe(
                        audio_data,
                        language=language,
                        sample_rate=sample_rate,
                        encoding=encoding,
                    )

                    if result.text:
                        yield result

            # Process remaining data
            if buffer.tell() > 0:
                audio_data = buffer.getvalue()
                result = await self.transcribe(
                    audio_data,
                    language=language,
                    sample_rate=sample_rate,
                    encoding=encoding,
                )
                if result.text:
                    yield result

        except Exception as e:
            raise ProviderError(
                f"Streaming transcription failed: {e}",
                provider=self.name,
                original_error=e,
            )

    async def get_supported_languages(self) -> list[str]:
        """Get supported languages."""
        # Whisper supports 99 languages
        return [
            "en", "zh", "de", "es", "ru", "ko", "fr", "ja", "pt", "tr",
            "pl", "ca", "nl", "ar", "sv", "it", "id", "hi", "fi", "vi",
            "he", "uk", "el", "ms", "cs", "ro", "da", "hu", "ta", "no",
        ]

