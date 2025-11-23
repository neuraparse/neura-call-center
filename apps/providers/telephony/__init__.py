"""Telephony provider abstraction."""

from apps.providers.telephony.base import Call, CallStatus, TelephonyProvider
from apps.providers.telephony.factory import get_telephony_provider

__all__ = ["TelephonyProvider", "Call", "CallStatus", "get_telephony_provider"]

