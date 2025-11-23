"""WebSocket streaming endpoints for real-time audio.

This module implements WebSocket endpoints for:
1. Twilio Media Streams - Bidirectional audio streaming with Twilio
2. Direct WebSocket - Direct client connections for web/mobile apps
3. Real-time STT/TTS - Integration with Deepgram and ElevenLabs

Based on 2025 latest best practices:
- FastAPI WebSocket support
- Twilio Media Streams API
- Deepgram WebSocket v2 API
- ElevenLabs WebSocket API
"""

import asyncio
import base64
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import Response

from apps.agents.call_agent import CallCenterAgent
from apps.core.logging import get_logger
from apps.providers.stt.factory import get_stt_provider
from apps.providers.tts.factory import get_tts_provider

logger = get_logger(__name__)
router = APIRouter(prefix="/stream", tags=["streaming"])


class TwilioMediaStreamHandler:
    """Handler for Twilio Media Streams WebSocket connections.
    
    Twilio Media Streams sends audio in mulaw format at 8kHz.
    We need to:
    1. Receive audio from Twilio
    2. Send to STT provider (Deepgram)
    3. Process with AI agent
    4. Generate response with TTS
    5. Send audio back to Twilio
    
    Reference: https://www.twilio.com/docs/voice/media-streams
    """
    
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.stream_sid: str | None = None
        self.call_sid: str | None = None
        self.agent: CallCenterAgent | None = None
        self.stt_provider = None
        self.tts_provider = None
        self.audio_buffer: list[bytes] = []
        
    async def initialize(self):
        """Initialize providers and agent."""
        try:
            # Create providers
            self.stt_provider = get_stt_provider()
            self.tts_provider = get_tts_provider()
            
            # Create agent
            self.agent = CallCenterAgent(streaming=True)
            
            logger.info(
                "TwilioMediaStreamHandler initialized",
                stream_sid=self.stream_sid,
                call_sid=self.call_sid,
            )
        except Exception as e:
            logger.error("Failed to initialize handler", error=str(e))
            raise
    
    async def handle_start(self, data: dict):
        """Handle stream start event from Twilio."""
        self.stream_sid = data.get("streamSid")
        self.call_sid = data.get("callSid")
        
        logger.info(
            "Media stream started",
            stream_sid=self.stream_sid,
            call_sid=self.call_sid,
        )
        
        await self.initialize()
    
    async def handle_media(self, data: dict):
        """Handle media (audio) event from Twilio.
        
        Twilio sends audio as base64-encoded mulaw at 8kHz.
        """
        try:
            # Get audio payload
            payload = data.get("media", {}).get("payload", "")
            
            # Decode base64
            audio_data = base64.b64decode(payload)
            
            # Add to buffer
            self.audio_buffer.append(audio_data)
            
            # Process when we have enough audio (e.g., 1 second = 8000 bytes)
            if len(self.audio_buffer) >= 10:  # ~1 second of audio
                await self.process_audio()
                
        except Exception as e:
            logger.error("Error handling media", error=str(e))
    
    async def process_audio(self):
        """Process buffered audio through STT -> Agent -> TTS pipeline."""
        try:
            # Combine audio buffer
            audio_data = b"".join(self.audio_buffer)
            self.audio_buffer.clear()
            
            # Transcribe with STT
            if self.stt_provider:
                stt_result = await self.stt_provider.transcribe(
                    audio_data=audio_data,
                    sample_rate=8000,
                    encoding="mulaw",
                )
                
                if stt_result.text and stt_result.is_final:
                    logger.info("Transcribed", text=stt_result.text)
                    
                    # Process with agent
                    if self.agent:
                        response = await self.agent.invoke(
                            message=stt_result.text,
                            call_id=self.call_sid,
                        )
                        
                        # Get agent response
                        agent_text = response["messages"][-1].content
                        logger.info("Agent response", text=agent_text)
                        
                        # Generate audio with TTS
                        if self.tts_provider:
                            tts_result = await self.tts_provider.synthesize(
                                text=agent_text
                            )
                            
                            # Send audio back to Twilio
                            await self.send_audio(tts_result.audio_data)
                            
        except Exception as e:
            logger.error("Error processing audio", error=str(e))

    async def send_audio(self, audio_data: bytes):
        """Send audio back to Twilio.

        Twilio expects audio as base64-encoded mulaw at 8kHz.
        """
        try:
            # Convert audio to mulaw if needed
            # (TTS providers usually return different formats)
            # For now, we'll send as-is and handle conversion later

            # Encode to base64
            payload = base64.b64encode(audio_data).decode("utf-8")

            # Send media message to Twilio
            message = {
                "event": "media",
                "streamSid": self.stream_sid,
                "media": {
                    "payload": payload,
                },
            }

            await self.websocket.send_json(message)
            logger.debug("Sent audio to Twilio", bytes=len(audio_data))

        except Exception as e:
            logger.error("Error sending audio", error=str(e))

    async def handle_stop(self, data: dict):
        """Handle stream stop event from Twilio."""
        logger.info(
            "Media stream stopped",
            stream_sid=self.stream_sid,
            call_sid=self.call_sid,
        )

    async def handle_mark(self, data: dict):
        """Handle mark event from Twilio."""
        # Marks are used for synchronization
        pass


@router.websocket("/twilio")
async def twilio_media_stream(websocket: WebSocket):
    """WebSocket endpoint for Twilio Media Streams.

    This endpoint handles bidirectional audio streaming with Twilio.

    Twilio sends events:
    - start: Stream started
    - media: Audio data (base64-encoded mulaw, 8kHz)
    - stop: Stream stopped
    - mark: Synchronization marker

    We send events:
    - media: Audio data to play
    - mark: Request synchronization marker
    - clear: Clear audio buffer

    Example usage:
    ```xml
    <Response>
        <Connect>
            <Stream url="wss://your-domain.com/stream/twilio" />
        </Connect>
    </Response>
    ```
    """
    await websocket.accept()
    handler = TwilioMediaStreamHandler(websocket)

    logger.info("Twilio WebSocket connection established")

    try:
        while True:
            # Receive message from Twilio
            message = await websocket.receive_text()
            data = json.loads(message)

            event = data.get("event")

            # Handle different event types
            if event == "start":
                await handler.handle_start(data.get("start", {}))
            elif event == "media":
                await handler.handle_media(data.get("media", {}))
            elif event == "stop":
                await handler.handle_stop(data.get("stop", {}))
            elif event == "mark":
                await handler.handle_mark(data.get("mark", {}))
            else:
                logger.warning("Unknown event type", event=event)

    except WebSocketDisconnect:
        logger.info("Twilio WebSocket disconnected")
    except Exception as e:
        logger.error("Error in Twilio WebSocket", error=str(e))
    finally:
        logger.info("Twilio WebSocket connection closed")


class DirectStreamHandler:
    """Handler for direct WebSocket connections from web/mobile clients.

    This handler supports:
    1. Real-time audio streaming from browser/mobile
    2. Text-based chat with voice synthesis
    3. Streaming responses (both text and audio)
    """

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.session_id: str | None = None
        self.agent: CallCenterAgent | None = None
        self.stt_provider = None
        self.tts_provider = None

    async def initialize(self, session_id: str):
        """Initialize session."""
        self.session_id = session_id

        # Create providers
        self.stt_provider = get_stt_provider()
        self.tts_provider = get_tts_provider()

        # Create agent
        self.agent = CallCenterAgent(streaming=True)

        logger.info("DirectStreamHandler initialized", session_id=session_id)

    async def handle_audio(self, audio_data: bytes, format: str = "webm"):
        """Handle audio data from client."""
        try:
            # Transcribe
            stt_result = await self.stt_provider.transcribe(
                audio_data=audio_data,
                sample_rate=16000,  # WebRTC typically uses 16kHz
                encoding="linear16",
            )

            if stt_result.text and stt_result.is_final:
                # Send transcription to client
                await self.websocket.send_json({
                    "type": "transcription",
                    "text": stt_result.text,
                    "confidence": stt_result.confidence,
                })

                # Process with agent
                await self.handle_text(stt_result.text)

        except Exception as e:
            logger.error("Error handling audio", error=str(e))
            await self.send_error(str(e))

    async def handle_text(self, text: str):
        """Handle text message from client."""
        try:
            # Send to agent with streaming
            async for chunk in self.agent.stream_events(
                message=text,
                call_id=self.session_id,
            ):
                # Stream LLM tokens
                if chunk["event"] == "on_chat_model_stream":
                    content = chunk["data"]["chunk"].content
                    if content:
                        await self.websocket.send_json({
                            "type": "text_chunk",
                            "content": content,
                        })

                # Tool calls
                elif chunk["event"] == "on_tool_start":
                    await self.websocket.send_json({
                        "type": "tool_start",
                        "tool": chunk["name"],
                    })

                elif chunk["event"] == "on_tool_end":
                    await self.websocket.send_json({
                        "type": "tool_end",
                        "tool": chunk["name"],
                        "output": chunk["data"].get("output"),
                    })

            # Get final response
            # (already streamed above, but we can send a completion event)
            await self.websocket.send_json({
                "type": "response_complete",
            })

        except Exception as e:
            logger.error("Error handling text", error=str(e))
            await self.send_error(str(e))

    async def send_error(self, error: str):
        """Send error message to client."""
        await self.websocket.send_json({
            "type": "error",
            "error": error,
        })


@router.websocket("/direct")
async def direct_stream(websocket: WebSocket):
    """Direct WebSocket endpoint for web/mobile clients.

    This endpoint supports:
    - Audio streaming (WebRTC, WebM, etc.)
    - Text chat with streaming responses
    - Real-time transcription
    - Tool calling visibility

    Message format (client -> server):
    ```json
    {
        "type": "init",
        "session_id": "unique-session-id"
    }
    {
        "type": "audio",
        "data": "base64-encoded-audio",
        "format": "webm"
    }
    {
        "type": "text",
        "text": "Hello, I need help"
    }
    ```

    Message format (server -> client):
    ```json
    {
        "type": "transcription",
        "text": "transcribed text",
        "confidence": 0.95
    }
    {
        "type": "text_chunk",
        "content": "streaming response chunk"
    }
    {
        "type": "tool_start",
        "tool": "get_customer_info"
    }
    {
        "type": "error",
        "error": "error message"
    }
    ```
    """
    await websocket.accept()
    handler = DirectStreamHandler(websocket)

    logger.info("Direct WebSocket connection established")

    try:
        while True:
            # Receive message
            message = await websocket.receive_json()
            msg_type = message.get("type")

            if msg_type == "init":
                session_id = message.get("session_id", "unknown")
                await handler.initialize(session_id)
                await websocket.send_json({
                    "type": "ready",
                    "session_id": session_id,
                })

            elif msg_type == "audio":
                audio_b64 = message.get("data", "")
                audio_format = message.get("format", "webm")
                audio_data = base64.b64decode(audio_b64)
                await handler.handle_audio(audio_data, audio_format)

            elif msg_type == "text":
                text = message.get("text", "")
                await handler.handle_text(text)

            else:
                logger.warning("Unknown message type", type=msg_type)

    except WebSocketDisconnect:
        logger.info("Direct WebSocket disconnected")
    except Exception as e:
        logger.error("Error in Direct WebSocket", error=str(e))
    finally:
        logger.info("Direct WebSocket connection closed")

