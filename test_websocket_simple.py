"""Simple WebSocket test to verify endpoints work."""

import asyncio
import json
import websockets


async def test_direct():
    """Test direct WebSocket endpoint."""
    print("Testing /stream/direct...")
    
    try:
        async with websockets.connect("ws://localhost:8000/stream/direct") as ws:
            print("✅ Connected!")
            
            # Send init
            await ws.send(json.dumps({"type": "init", "session_id": "test-123"}))
            print("📤 Sent init message")
            
            # Receive response
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(response)
            print(f"📥 Received: {data}")
            
            if data.get("type") == "ready":
                print("✅ Direct WebSocket works!")
            else:
                print(f"❌ Unexpected response: {data}")
                
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_twilio():
    """Test Twilio WebSocket endpoint."""
    print("\nTesting /stream/twilio...")
    
    try:
        async with websockets.connect("ws://localhost:8000/stream/twilio") as ws:
            print("✅ Connected!")
            
            # Send start event
            await ws.send(json.dumps({
                "event": "start",
                "start": {
                    "streamSid": "MZ123",
                    "callSid": "CA123",
                }
            }))
            print("📤 Sent start event")
            
            # Wait a bit
            await asyncio.sleep(0.5)
            
            print("✅ Twilio WebSocket works!")
                
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run tests."""
    print("🔌 Simple WebSocket Test\n")
    print("Make sure server is running: python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000\n")
    
    await test_direct()
    await test_twilio()
    
    print("\n✅ Tests complete!")


if __name__ == "__main__":
    asyncio.run(main())

