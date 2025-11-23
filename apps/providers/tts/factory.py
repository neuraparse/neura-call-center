"""Factory for creating TTS providers."""

from apps.core.config import TTSProvider as TTSProviderEnum
from apps.core.config import settings
from apps.core.logging import get_logger
from apps.providers.base import ProviderNotAvailableError
from apps.providers.tts.base import TTSProvider
from apps.providers.tts.elevenlabs import ElevenLabsTTSProvider
from apps.providers.tts.openai import OpenAITTSProvider

logger = get_logger(__name__)


def get_tts_provider(provider_name: TTSProviderEnum | None = None) -> TTSProvider:
    """
    Get TTS provider instance.

    Args:
        provider_name: Provider to use (defaults to primary from settings)

    Returns:
        TTSProvider instance

    Raises:
        ProviderNotAvailableError: If provider is not available
    """
    provider_name = provider_name or settings.tts_primary_provider

    try:
        if provider_name == TTSProviderEnum.ELEVENLABS:
            if not settings.elevenlabs_api_key:
                raise ProviderNotAvailableError(
                    "ElevenLabs API key not configured",
                    provider="elevenlabs",
                )
            return ElevenLabsTTSProvider(
                name="elevenlabs",
                api_key=settings.elevenlabs_api_key,
                voice_id=settings.elevenlabs_voice_id,
            )

        elif provider_name == TTSProviderEnum.OPENAI:
            if not settings.openai_api_key:
                raise ProviderNotAvailableError(
                    "OpenAI API key not configured",
                    provider="openai",
                )
            return OpenAITTSProvider(
                name="openai",
                api_key=settings.openai_api_key,
                model=settings.openai_tts_model,
                voice=settings.openai_tts_voice,
            )

        elif provider_name == TTSProviderEnum.AZURE:
            if not settings.azure_speech_key or not settings.azure_speech_region:
                raise ProviderNotAvailableError(
                    "Azure Speech credentials not configured",
                    provider="azure",
                )
            # TODO: Implement Azure TTS provider
            raise NotImplementedError("Azure TTS provider not yet implemented")

        else:
            raise ProviderNotAvailableError(
                f"Unknown TTS provider: {provider_name}",
                provider=str(provider_name),
            )

    except Exception as e:
        logger.error(
            "Failed to initialize TTS provider",
            provider=provider_name,
            error=str(e),
        )
        raise


async def get_tts_provider_with_fallback() -> TTSProvider:
    """
    Get TTS provider with automatic fallback.

    Returns:
        TTSProvider instance

    Raises:
        ProviderNotAvailableError: If no provider is available
    """
    # Try primary provider
    try:
        provider = get_tts_provider(settings.tts_primary_provider)
        await provider.initialize()
        if await provider.health_check():
            logger.info("Using primary TTS provider", provider=settings.tts_primary_provider)
            return provider
    except Exception as e:
        logger.warning(
            "Primary TTS provider failed",
            provider=settings.tts_primary_provider,
            error=str(e),
        )

    # Try fallback providers
    for fallback in settings.tts_fallback_providers:
        try:
            provider = get_tts_provider(fallback)
            await provider.initialize()
            if await provider.health_check():
                logger.info("Using fallback TTS provider", provider=fallback)
                return provider
        except Exception as e:
            logger.warning(
                "Fallback TTS provider failed",
                provider=fallback,
                error=str(e),
            )

    raise ProviderNotAvailableError(
        "No TTS provider available",
        provider="all",
    )

