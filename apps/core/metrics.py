"""Custom business metrics for Neura Call Center.

This module provides custom metrics for monitoring:
- Call metrics (total, active, completed, failed)
- Conversation metrics (messages, turns, duration)
- Agent performance (response time, success rate)
- Provider metrics (STT, TTS, LLM usage)
"""

from opentelemetry import metrics
from opentelemetry.metrics import Counter, Histogram, UpDownCounter

from apps.core.logging import get_logger

logger = get_logger(__name__)

# Get meter
meter = metrics.get_meter("neura.call_center")

# ============================================================================
# Call Metrics
# ============================================================================

calls_total = meter.create_counter(
    name="calls.total",
    description="Total number of calls",
    unit="1",
)

calls_active = meter.create_up_down_counter(
    name="calls.active",
    description="Number of currently active calls",
    unit="1",
)

calls_completed = meter.create_counter(
    name="calls.completed",
    description="Total number of completed calls",
    unit="1",
)

calls_failed = meter.create_counter(
    name="calls.failed",
    description="Total number of failed calls",
    unit="1",
)

call_duration = meter.create_histogram(
    name="calls.duration",
    description="Call duration in seconds",
    unit="s",
)

# ============================================================================
# Conversation Metrics
# ============================================================================

conversations_total = meter.create_counter(
    name="conversations.total",
    description="Total number of conversations",
    unit="1",
)

messages_total = meter.create_counter(
    name="messages.total",
    description="Total number of messages",
    unit="1",
)

conversation_turns = meter.create_histogram(
    name="conversations.turns",
    description="Number of turns in a conversation",
    unit="1",
)

# ============================================================================
# Agent Performance Metrics
# ============================================================================

agent_response_time = meter.create_histogram(
    name="agent.response_time",
    description="Agent response time in seconds",
    unit="s",
)

agent_tool_calls = meter.create_counter(
    name="agent.tool_calls",
    description="Total number of agent tool calls",
    unit="1",
)

agent_errors = meter.create_counter(
    name="agent.errors",
    description="Total number of agent errors",
    unit="1",
)

# ============================================================================
# Provider Metrics
# ============================================================================

stt_requests = meter.create_counter(
    name="stt.requests",
    description="Total number of STT requests",
    unit="1",
)

stt_duration = meter.create_histogram(
    name="stt.duration",
    description="STT processing duration in seconds",
    unit="s",
)

tts_requests = meter.create_counter(
    name="tts.requests",
    description="Total number of TTS requests",
    unit="1",
)

tts_duration = meter.create_histogram(
    name="tts.duration",
    description="TTS processing duration in seconds",
    unit="s",
)

llm_requests = meter.create_counter(
    name="llm.requests",
    description="Total number of LLM requests",
    unit="1",
)

llm_tokens = meter.create_counter(
    name="llm.tokens",
    description="Total number of LLM tokens used",
    unit="1",
)

llm_duration = meter.create_histogram(
    name="llm.duration",
    description="LLM request duration in seconds",
    unit="s",
)

# ============================================================================
# WebSocket Metrics
# ============================================================================

websocket_connections = meter.create_up_down_counter(
    name="websocket.connections",
    description="Number of active WebSocket connections",
    unit="1",
)

websocket_messages = meter.create_counter(
    name="websocket.messages",
    description="Total number of WebSocket messages",
    unit="1",
)

# ============================================================================
# Helper Functions
# ============================================================================

def record_call_started(direction: str = "inbound", language: str = "en-US") -> None:
    """Record a new call started."""
    calls_total.add(1, {"direction": direction, "language": language})
    calls_active.add(1, {"direction": direction})
    logger.debug("Call started metric recorded", direction=direction, language=language)


def record_call_ended(
    direction: str = "inbound",
    status: str = "completed",
    duration_seconds: float = 0.0,
) -> None:
    """Record a call ended."""
    calls_active.add(-1, {"direction": direction})

    if status == "completed":
        calls_completed.add(1, {"direction": direction})
    else:
        calls_failed.add(1, {"direction": direction, "status": status})

    call_duration.record(duration_seconds, {"direction": direction, "status": status})
    logger.debug("Call ended metric recorded", direction=direction, status=status, duration=duration_seconds)


def record_message(role: str = "user", language: str = "en-US") -> None:
    """Record a message in a conversation."""
    messages_total.add(1, {"role": role, "language": language})
    logger.debug("Message metric recorded", role=role, language=language)


def record_agent_response(duration_seconds: float, tool_used: bool = False) -> None:
    """Record agent response time."""
    agent_response_time.record(duration_seconds)
    if tool_used:
        agent_tool_calls.add(1)
    logger.debug("Agent response metric recorded", duration=duration_seconds, tool_used=tool_used)


def record_stt_request(provider: str, duration_seconds: float) -> None:
    """Record STT request."""
    stt_requests.add(1, {"provider": provider})
    stt_duration.record(duration_seconds, {"provider": provider})
    logger.debug("STT metric recorded", provider=provider, duration=duration_seconds)


def record_tts_request(provider: str, duration_seconds: float) -> None:
    """Record TTS request."""
    tts_requests.add(1, {"provider": provider})
    tts_duration.record(duration_seconds, {"provider": provider})
    logger.debug("TTS metric recorded", provider=provider, duration=duration_seconds)


def record_llm_request(
    provider: str,
    duration_seconds: float,
    tokens_used: int = 0,
) -> None:
    """Record LLM request."""
    llm_requests.add(1, {"provider": provider})
    llm_duration.record(duration_seconds, {"provider": provider})
    if tokens_used > 0:
        llm_tokens.add(tokens_used, {"provider": provider})
    logger.debug("LLM metric recorded", provider=provider, duration=duration_seconds, tokens=tokens_used)


def record_websocket_connection(connected: bool = True) -> None:
    """Record WebSocket connection change."""
    websocket_connections.add(1 if connected else -1)
    logger.debug("WebSocket connection metric recorded", connected=connected)


def record_websocket_message(direction: str = "inbound") -> None:
    """Record WebSocket message."""
    websocket_messages.add(1, {"direction": direction})
    logger.debug("WebSocket message metric recorded", direction=direction)


