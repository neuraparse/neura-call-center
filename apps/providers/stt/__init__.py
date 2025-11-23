"""Speech-to-Text provider abstraction."""

from apps.providers.stt.base import STTProvider, STTResult
from apps.providers.stt.factory import get_stt_provider

__all__ = ["STTProvider", "STTResult", "get_stt_provider"]

