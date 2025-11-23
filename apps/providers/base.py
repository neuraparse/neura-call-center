"""Base classes for provider abstraction."""

from abc import ABC, abstractmethod
from typing import Any


class ProviderError(Exception):
    """Base exception for provider errors."""

    def __init__(self, message: str, provider: str, original_error: Exception | None = None):
        """Initialize provider error."""
        self.message = message
        self.provider = provider
        self.original_error = original_error
        super().__init__(f"[{provider}] {message}")


class ProviderNotAvailableError(ProviderError):
    """Exception raised when a provider is not available."""

    pass


class BaseProvider(ABC):
    """Base class for all providers."""

    def __init__(self, name: str, **kwargs: Any):
        """Initialize provider."""
        self.name = name
        self.config = kwargs

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy and available."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup provider resources."""
        pass

    def __repr__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__} {self.name}>"

