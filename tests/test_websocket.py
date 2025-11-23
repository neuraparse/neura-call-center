"""Tests for WebSocket streaming endpoints."""

import base64
import json

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from apps.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.mark.skip(reason="WebSocket testing requires running server")
def test_direct_websocket_connection(client):
    """Test direct WebSocket connection.

    Note: This test is skipped because TestClient WebSocket support
    can be unreliable. Use the websocket_client.py example instead.
    """
    with client.websocket_connect("/stream/direct") as websocket:
        # Send init message
        websocket.send_json({
            "type": "init",
            "session_id": "test-123",
        })

        # Receive ready message
        data = websocket.receive_json()
        assert data["type"] == "ready"
        assert data["session_id"] == "test-123"


@pytest.mark.skip(reason="WebSocket testing requires running server")
def test_direct_websocket_text_message(client):
    """Test sending text message through WebSocket."""
    with client.websocket_connect("/stream/direct") as websocket:
        # Initialize
        websocket.send_json({
            "type": "init",
            "session_id": "test-123",
        })
        websocket.receive_json()  # ready
        
        # Send text
        websocket.send_json({
            "type": "text",
            "text": "Hello",
        })
        
        # Should receive streaming responses
        responses = []
        while True:
            data = websocket.receive_json(timeout=5)
            responses.append(data)
            
            if data["type"] == "response_complete":
                break
        
        # Should have received some text chunks
        text_chunks = [r for r in responses if r["type"] == "text_chunk"]
        assert len(text_chunks) > 0


@pytest.mark.skip(reason="WebSocket testing requires running server")
def test_twilio_websocket_connection(client):
    """Test Twilio WebSocket connection."""
    with client.websocket_connect("/stream/twilio") as websocket:
        # Send start event
        websocket.send_json({
            "event": "start",
            "start": {
                "streamSid": "MZ123",
                "callSid": "CA123",
            },
        })

        # Connection should stay open
        # (In real scenario, we'd send media events)


@pytest.mark.skip(reason="WebSocket testing requires running server")
def test_twilio_websocket_media(client):
    """Test Twilio WebSocket media handling."""
    with client.websocket_connect("/stream/twilio") as websocket:
        # Start stream
        websocket.send_json({
            "event": "start",
            "start": {
                "streamSid": "MZ123",
                "callSid": "CA123",
            },
        })
        
        # Send audio data
        fake_audio = b"\x00" * 160  # mulaw silence
        audio_b64 = base64.b64encode(fake_audio).decode("utf-8")
        
        for _ in range(10):  # Send 10 frames
            websocket.send_json({
                "event": "media",
                "media": {
                    "payload": audio_b64,
                },
            })
        
        # Should process audio and potentially send responses
        # (depends on STT detecting speech)


@pytest.mark.skip(reason="WebSocket testing requires running server")
def test_websocket_invalid_message_type(client):
    """Test WebSocket with invalid message type."""
    with client.websocket_connect("/stream/direct") as websocket:
        # Send invalid message type
        websocket.send_json({
            "type": "invalid_type",
        })

        # Should not crash, just log warning
        # Connection should stay open


def test_api_imports_successfully(client):
    """Test that API with WebSocket routes imports successfully."""
    # If we got here, the API imported successfully
    # This tests that WebSocket routes don't break the app
    response = client.get("/")
    assert response.status_code == 200

