"""Text-to-Speech provider abstraction."""

from apps.providers.tts.base import TTSProvider, TTSResult
from apps.providers.tts.factory import get_tts_provider

__all__ = ["TTSProvider", "TTSResult", "get_tts_provider"]

