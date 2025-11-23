"""Application configuration using Pydantic Settings."""

from enum import Enum
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Application environment."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure-openai"
    OLLAMA = "ollama"


class STTProvider(str, Enum):
    """Supported Speech-to-Text providers."""

    DEEPGRAM = "deepgram"
    WHISPER = "whisper"
    ASSEMBLYAI = "assemblyai"
    AZURE = "azure"


class TTSProvider(str, Enum):
    """Supported Text-to-Speech providers."""

    ELEVENLABS = "elevenlabs"
    OPENAI = "openai"
    AZURE = "azure"


class TelephonyProvider(str, Enum):
    """Supported telephony providers."""

    TWILIO = "twilio"
    VONAGE = "vonage"
    BANDWIDTH = "bandwidth"
    TELNYX = "telnyx"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="neura-call-center")
    app_env: Environment = Field(default=Environment.DEVELOPMENT)
    app_debug: bool = Field(default=False)
    app_log_level: str = Field(default="INFO")
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8080)

    # Database
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/neura_call_center"
    )
    database_pool_size: int = Field(default=20)
    database_max_overflow: int = Field(default=10)
    database_echo: bool = Field(default=False)

    # Cache
    cache_url: RedisDsn = Field(default="redis://localhost:6379/0")
    cache_ttl: int = Field(default=3600)
    cache_enabled: bool = Field(default=True)

    # LLM
    llm_provider: LLMProvider = Field(default=LLMProvider.OPENAI)
    llm_model: str = Field(default="gpt-4o")
    llm_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    llm_max_tokens: int = Field(default=2000, gt=0)
    llm_streaming: bool = Field(default=True)

    # OpenAI
    openai_api_key: str | None = Field(default=None)
    openai_org_id: str | None = Field(default=None)

    # Anthropic
    anthropic_api_key: str | None = Field(default=None)

    # Azure OpenAI
    azure_openai_endpoint: str | None = Field(default=None)
    azure_openai_api_key: str | None = Field(default=None)
    azure_openai_api_version: str = Field(default="2024-02-15-preview")
    azure_openai_deployment_name: str | None = Field(default=None)

    # STT
    stt_primary_provider: STTProvider = Field(default=STTProvider.DEEPGRAM)
    stt_fallback_providers: list[STTProvider] = Field(
        default_factory=lambda: [STTProvider.WHISPER]
    )

    # Deepgram
    deepgram_api_key: str | None = Field(default=None)

    # Whisper
    whisper_model: Literal["tiny", "base", "small", "medium", "large"] = Field(default="base")
    whisper_device: Literal["cpu", "cuda"] = Field(default="cpu")

    # AssemblyAI
    assemblyai_api_key: str | None = Field(default=None)

    # Azure Speech
    azure_speech_key: str | None = Field(default=None)
    azure_speech_region: str | None = Field(default=None)

    # TTS
    tts_primary_provider: TTSProvider = Field(default=TTSProvider.ELEVENLABS)
    tts_fallback_providers: list[TTSProvider] = Field(
        default_factory=lambda: [TTSProvider.OPENAI]
    )

    # ElevenLabs
    elevenlabs_api_key: str | None = Field(default=None)
    elevenlabs_voice_id: str = Field(default="21m00Tcm4TlvDq8ikWAM")

    # OpenAI TTS
    openai_tts_model: str = Field(default="tts-1-hd")
    openai_tts_voice: str = Field(default="alloy")

    # Azure TTS
    azure_tts_voice: str = Field(default="en-US-JennyNeural")

    # Telephony
    telephony_provider: TelephonyProvider = Field(default=TelephonyProvider.TWILIO)

    # Twilio
    twilio_account_sid: str | None = Field(default=None)
    twilio_auth_token: str | None = Field(default=None)
    twilio_phone_number: str | None = Field(default=None)
    twilio_webhook_url: str | None = Field(default=None)

    # Security
    secret_key: str = Field(default="change-this-in-production")
    api_key_header: str = Field(default="X-API-Key")
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8080"]
    )
    cors_enabled: bool = Field(default=True)

    # Observability & Monitoring
    otel_exporter_otlp_endpoint: str | None = Field(
        default=None,
        description="OpenTelemetry OTLP endpoint (e.g., http://tempo:4317 or http://jaeger:4317)"
    )
    prometheus_metrics_port: int = Field(
        default=9464,
        description="Port for Prometheus metrics endpoint"
    )
    enable_tracing: bool = Field(default=True, description="Enable distributed tracing")
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")

    # Call Center
    default_language: str = Field(default="en-US")
    supported_languages: list[str] = Field(
        default_factory=lambda: ["en-US", "tr-TR", "fr-FR", "de-DE", "es-ES"]
    )
    max_call_duration_minutes: int = Field(default=30)
    call_recording_enabled: bool = Field(default=True)
    agent_name: str = Field(default="Neura")
    agent_company: str = Field(default="Your Company")
    silence_timeout_seconds: int = Field(default=10)
    response_timeout_seconds: int = Field(default=30)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env == Environment.PRODUCTION


# Global settings instance
settings = Settings()

