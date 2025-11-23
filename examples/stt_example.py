"""Example: Speech-to-Text provider usage."""
import asyncio
import os
from pathlib import Path

from apps.core.logging import logger
from apps.providers.stt.factory import get_stt_provider


async def test_whisper_stt():
    """Test Whisper STT provider with a sample audio file."""
    logger.info("Testing Whisper STT Provider")
    
    # Get Whisper provider (self-hosted, no API key needed)
    provider = get_stt_provider("whisper")
    
    try:
        # Initialize
        await provider.initialize()
        logger.info("Whisper provider initialized")
        
        # Check health
        is_healthy = await provider.health_check()
        logger.info(f"Provider health: {is_healthy}")
        
        # For demo purposes, create fake audio data
        # In real usage, you would load actual audio file
        fake_audio = b"\x00" * 16000  # 1 second of silence at 16kHz
        
        logger.info("Transcribing audio...")
        result = await provider.transcribe(
            audio_data=fake_audio,
            language="en",
            sample_rate=16000,
        )
        
        logger.info(f"Transcription result:")
        logger.info(f"  Text: {result.text}")
        logger.info(f"  Confidence: {result.confidence}")
        logger.info(f"  Language: {result.language}")
        logger.info(f"  Duration: {result.duration_ms}ms")
        
    except Exception as e:
        logger.error(f"Error testing Whisper: {e}")
    finally:
        await provider.cleanup()
        logger.info("Provider cleaned up")


async def test_deepgram_stt():
    """Test Deepgram STT provider."""
    logger.info("Testing Deepgram STT Provider")
    
    # Check if API key is set
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        logger.warning("DEEPGRAM_API_KEY not set, skipping Deepgram test")
        return
    
    provider = get_stt_provider("deepgram")
    
    try:
        await provider.initialize()
        logger.info("Deepgram provider initialized")
        
        # Check health
        is_healthy = await provider.health_check()
        logger.info(f"Provider health: {is_healthy}")
        
        # Create fake audio
        fake_audio = b"\x00" * 16000
        
        logger.info("Transcribing audio...")
        result = await provider.transcribe(
            audio_data=fake_audio,
            language="en-US",
            sample_rate=16000,
        )
        
        logger.info(f"Transcription result:")
        logger.info(f"  Text: {result.text}")
        logger.info(f"  Confidence: {result.confidence}")
        
    except Exception as e:
        logger.error(f"Error testing Deepgram: {e}")
    finally:
        await provider.cleanup()


async def test_stt_streaming():
    """Test STT streaming."""
    logger.info("Testing STT Streaming")
    
    provider = get_stt_provider("whisper")
    
    try:
        await provider.initialize()
        
        # Simulate audio stream
        async def audio_stream():
            for i in range(3):
                # Send 1 second chunks
                yield b"\x00" * 16000
                await asyncio.sleep(0.1)
        
        logger.info("Starting streaming transcription...")
        async for result in provider.transcribe_stream(audio_stream()):
            logger.info(f"Stream result: {result.text} (final: {result.is_final})")
        
    except Exception as e:
        logger.error(f"Error in streaming: {e}")
    finally:
        await provider.cleanup()


async def main():
    """Run all STT examples."""
    logger.info("=" * 60)
    logger.info("STT Provider Examples")
    logger.info("=" * 60)
    
    # Test Whisper (always available)
    await test_whisper_stt()
    
    logger.info("\n" + "=" * 60 + "\n")
    
    # Test Deepgram (if API key available)
    await test_deepgram_stt()
    
    logger.info("\n" + "=" * 60 + "\n")
    
    # Test streaming
    await test_stt_streaming()
    
    logger.info("\n" + "=" * 60)
    logger.info("All STT examples completed!")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

