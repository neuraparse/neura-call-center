"""Factory for creating STT providers."""

from apps.core.config import STTProvider as STTProviderEnum
from apps.core.config import settings
from apps.core.logging import get_logger
from apps.providers.base import ProviderNotAvailableError
from apps.providers.stt.base import STTProvider
from apps.providers.stt.deepgram import DeepgramSTTProvider
from apps.providers.stt.whisper import WhisperSTTProvider

logger = get_logger(__name__)


def get_stt_provider(provider_name: STTProviderEnum | None = None) -> STTProvider:
    """
    Get STT provider instance.

    Args:
        provider_name: Provider to use (defaults to primary from settings)

    Returns:
        STTProvider instance

    Raises:
        ProviderNotAvailableError: If provider is not available
    """
    provider_name = provider_name or settings.stt_primary_provider

    try:
        if provider_name == STTProviderEnum.DEEPGRAM:
            if not settings.deepgram_api_key:
                raise ProviderNotAvailableError(
                    "Deepgram API key not configured",
                    provider="deepgram",
                )
            return DeepgramSTTProvider(
                name="deepgram",
                api_key=settings.deepgram_api_key,
            )

        elif provider_name == STTProviderEnum.WHISPER:
            return WhisperSTTProvider(
                name="whisper",
                model=settings.whisper_model,
                device=settings.whisper_device,
            )

        elif provider_name == STTProviderEnum.ASSEMBLYAI:
            if not settings.assemblyai_api_key:
                raise ProviderNotAvailableError(
                    "AssemblyAI API key not configured",
                    provider="assemblyai",
                )
            # TODO: Implement AssemblyAI provider
            raise NotImplementedError("AssemblyAI provider not yet implemented")

        elif provider_name == STTProviderEnum.AZURE:
            if not settings.azure_speech_key or not settings.azure_speech_region:
                raise ProviderNotAvailableError(
                    "Azure Speech credentials not configured",
                    provider="azure",
                )
            # TODO: Implement Azure Speech provider
            raise NotImplementedError("Azure Speech provider not yet implemented")

        else:
            raise ProviderNotAvailableError(
                f"Unknown STT provider: {provider_name}",
                provider=str(provider_name),
            )

    except Exception as e:
        logger.error(
            "Failed to initialize STT provider",
            provider=provider_name,
            error=str(e),
        )
        raise


async def get_stt_provider_with_fallback() -> STTProvider:
    """
    Get STT provider with automatic fallback.

    Returns:
        STTProvider instance

    Raises:
        ProviderNotAvailableError: If no provider is available
    """
    # Try primary provider
    try:
        provider = get_stt_provider(settings.stt_primary_provider)
        await provider.initialize()
        if await provider.health_check():
            logger.info("Using primary STT provider", provider=settings.stt_primary_provider)
            return provider
    except Exception as e:
        logger.warning(
            "Primary STT provider failed",
            provider=settings.stt_primary_provider,
            error=str(e),
        )

    # Try fallback providers
    for fallback in settings.stt_fallback_providers:
        try:
            provider = get_stt_provider(fallback)
            await provider.initialize()
            if await provider.health_check():
                logger.info("Using fallback STT provider", provider=fallback)
                return provider
        except Exception as e:
            logger.warning(
                "Fallback STT provider failed",
                provider=fallback,
                error=str(e),
            )

    raise ProviderNotAvailableError(
        "No STT provider available",
        provider="all",
    )

