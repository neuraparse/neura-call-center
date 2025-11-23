"""WebSocket client examples for testing streaming endpoints.

This script demonstrates how to connect to the WebSocket endpoints
and stream audio/text in real-time.

Run with:
    python examples/websocket_client.py
"""

import asyncio
import base64
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import websockets


async def test_direct_stream_text():
    """Test direct WebSocket with text messages."""
    print("\n" + "="*80)
    print("TEST: Direct WebSocket - Text Streaming")
    print("="*80 + "\n")
    
    uri = "ws://localhost:8000/stream/direct"
    
    try:
        async with websockets.connect(uri) as websocket:
            # Initialize session
            await websocket.send(json.dumps({
                "type": "init",
                "session_id": "test-session-123",
            }))
            
            # Wait for ready
            response = await websocket.recv()
            data = json.loads(response)
            print(f"✅ Session initialized: {data}\n")
            
            # Send text message
            print("User: Hello, I need help with my order\n")
            await websocket.send(json.dumps({
                "type": "text",
                "text": "Hello, I need help with my order",
            }))
            
            # Receive streaming responses
            print("Agent: ", end="", flush=True)
            
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    
                    if data["type"] == "text_chunk":
                        print(data["content"], end="", flush=True)
                    
                    elif data["type"] == "tool_start":
                        print(f"\n[Tool: {data['tool']}]", end="", flush=True)
                    
                    elif data["type"] == "tool_end":
                        print(f" ✓", end="", flush=True)
                    
                    elif data["type"] == "response_complete":
                        print("\n\n✅ Response complete")
                        break
                    
                    elif data["type"] == "error":
                        print(f"\n❌ Error: {data['error']}")
                        break
                        
                except asyncio.TimeoutError:
                    print("\n⏱️ Timeout waiting for response")
                    break
                    
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_direct_stream_audio():
    """Test direct WebSocket with audio (simulated)."""
    print("\n" + "="*80)
    print("TEST: Direct WebSocket - Audio Streaming (Simulated)")
    print("="*80 + "\n")
    
    uri = "ws://localhost:8000/stream/direct"
    
    try:
        async with websockets.connect(uri) as websocket:
            # Initialize session
            await websocket.send(json.dumps({
                "type": "init",
                "session_id": "test-audio-session",
            }))
            
            # Wait for ready
            response = await websocket.recv()
            print(f"✅ Session initialized\n")
            
            # Simulate audio data (in real app, this would be from microphone)
            fake_audio = b"fake audio data for testing"
            audio_b64 = base64.b64encode(fake_audio).decode("utf-8")
            
            print("📤 Sending audio data...\n")
            await websocket.send(json.dumps({
                "type": "audio",
                "data": audio_b64,
                "format": "webm",
            }))
            
            # Receive responses
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    
                    if data["type"] == "transcription":
                        print(f"📝 Transcription: {data['text']}")
                        print(f"   Confidence: {data['confidence']}\n")
                    
                    elif data["type"] == "text_chunk":
                        print(data["content"], end="", flush=True)
                    
                    elif data["type"] == "response_complete":
                        print("\n\n✅ Response complete")
                        break
                    
                    elif data["type"] == "error":
                        print(f"❌ Error: {data['error']}")
                        break
                        
                except asyncio.TimeoutError:
                    print("⏱️ Timeout - no more responses")
                    break
                    
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_twilio_stream():
    """Test Twilio Media Stream endpoint (simulated)."""
    print("\n" + "="*80)
    print("TEST: Twilio Media Stream (Simulated)")
    print("="*80 + "\n")
    
    uri = "ws://localhost:8000/stream/twilio"
    
    try:
        async with websockets.connect(uri) as websocket:
            # Send start event (like Twilio does)
            await websocket.send(json.dumps({
                "event": "start",
                "start": {
                    "streamSid": "MZ1234567890",
                    "callSid": "CA1234567890",
                },
            }))
            
            print("✅ Stream started\n")
            
            # Simulate sending audio (mulaw format)
            fake_audio = b"\x00" * 160  # 20ms of silence in mulaw
            audio_b64 = base64.b64encode(fake_audio).decode("utf-8")
            
            print("📤 Sending audio frames...\n")
            for i in range(5):
                await websocket.send(json.dumps({
                    "event": "media",
                    "media": {
                        "payload": audio_b64,
                    },
                }))
                await asyncio.sleep(0.02)  # 20ms
            
            print("✅ Audio sent\n")
            
            # In real scenario, we'd receive audio back from the server
            # For now, just close gracefully
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all WebSocket tests."""
    print("\n🔌 WebSocket Client Tests - 2025")
    print("="*80)
    print("Make sure the API server is running on http://localhost:8000")
    print("="*80)
    
    # Test direct stream with text
    await test_direct_stream_text()
    
    # Test direct stream with audio
    await test_direct_stream_audio()
    
    # Test Twilio stream
    await test_twilio_stream()
    
    print("\n" + "="*80)
    print("✅ All WebSocket tests completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

