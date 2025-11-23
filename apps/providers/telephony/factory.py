"""Factory for creating Telephony providers."""

from apps.core.config import TelephonyProvider as TelephonyProviderEnum
from apps.core.config import settings
from apps.core.logging import get_logger
from apps.providers.base import ProviderNotAvailableError
from apps.providers.telephony.base import TelephonyProvider
from apps.providers.telephony.twilio import TwilioTelephonyProvider

logger = get_logger(__name__)


def get_telephony_provider(
    provider_name: TelephonyProviderEnum | None = None,
) -> TelephonyProvider:
    """
    Get Telephony provider instance.

    Args:
        provider_name: Provider to use (defaults to primary from settings)

    Returns:
        TelephonyProvider instance

    Raises:
        ProviderNotAvailableError: If provider is not available
    """
    provider_name = provider_name or settings.telephony_provider

    try:
        if provider_name == TelephonyProviderEnum.TWILIO:
            if not settings.twilio_account_sid or not settings.twilio_auth_token:
                raise ProviderNotAvailableError(
                    "Twilio credentials not configured",
                    provider="twilio",
                )
            return TwilioTelephonyProvider(
                name="twilio",
                account_sid=settings.twilio_account_sid,
                auth_token=settings.twilio_auth_token,
                phone_number=settings.twilio_phone_number,
            )

        elif provider_name == TelephonyProviderEnum.VONAGE:
            # TODO: Implement Vonage provider
            raise NotImplementedError("Vonage provider not yet implemented")

        elif provider_name == TelephonyProviderEnum.BANDWIDTH:
            # TODO: Implement Bandwidth provider
            raise NotImplementedError("Bandwidth provider not yet implemented")

        elif provider_name == TelephonyProviderEnum.TELNYX:
            # TODO: Implement Telnyx provider
            raise NotImplementedError("Telnyx provider not yet implemented")

        else:
            raise ProviderNotAvailableError(
                f"Unknown telephony provider: {provider_name}",
                provider=str(provider_name),
            )

    except Exception as e:
        logger.error(
            "Failed to initialize telephony provider",
            provider=provider_name,
            error=str(e),
        )
        raise

