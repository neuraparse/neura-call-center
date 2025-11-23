"""Example: Text-to-Speech provider usage."""
import asyncio
import os
from pathlib import Path

from apps.core.logging import logger
from apps.providers.tts.factory import get_tts_provider


async def test_openai_tts():
    """Test OpenAI TTS provider."""
    logger.info("Testing OpenAI TTS Provider")
    
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sk-...":
        logger.warning("OPENAI_API_KEY not set, skipping OpenAI TTS test")
        return
    
    provider = get_tts_provider("openai")
    
    try:
        await provider.initialize()
        logger.info("OpenAI TTS provider initialized")
        
        # Check health
        is_healthy = await provider.health_check()
        logger.info(f"Provider health: {is_healthy}")
        
        # Synthesize speech
        text = "Hello! This is a test of the OpenAI text to speech system."
        logger.info(f"Synthesizing: '{text}'")
        
        result = await provider.synthesize(
            text=text,
            voice_id="alloy",  # OpenAI voices: alloy, echo, fable, onyx, nova, shimmer
        )
        
        logger.info(f"Synthesis result:")
        logger.info(f"  Format: {result.format}")
        logger.info(f"  Sample rate: {result.sample_rate}")
        logger.info(f"  Audio size: {len(result.audio_data)} bytes")
        
        # Save to file
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "openai_tts_output.mp3"
        
        with open(output_file, "wb") as f:
            f.write(result.audio_data)
        
        logger.info(f"Audio saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Error testing OpenAI TTS: {e}")
    finally:
        await provider.cleanup()


async def test_elevenlabs_tts():
    """Test ElevenLabs TTS provider."""
    logger.info("Testing ElevenLabs TTS Provider")
    
    # Check if API key is set
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        logger.warning("ELEVENLABS_API_KEY not set, skipping ElevenLabs test")
        return
    
    provider = get_tts_provider("elevenlabs")
    
    try:
        await provider.initialize()
        logger.info("ElevenLabs provider initialized")
        
        # Check health
        is_healthy = await provider.health_check()
        logger.info(f"Provider health: {is_healthy}")
        
        # Synthesize speech
        text = "Welcome to Neura Call Center. How can I help you today?"
        logger.info(f"Synthesizing: '{text}'")
        
        result = await provider.synthesize(
            text=text,
            voice_id=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
        )
        
        logger.info(f"Synthesis result:")
        logger.info(f"  Format: {result.format}")
        logger.info(f"  Sample rate: {result.sample_rate}")
        logger.info(f"  Audio size: {len(result.audio_data)} bytes")
        
        # Save to file
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "elevenlabs_tts_output.mp3"
        
        with open(output_file, "wb") as f:
            f.write(result.audio_data)
        
        logger.info(f"Audio saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Error testing ElevenLabs: {e}")
    finally:
        await provider.cleanup()


async def test_tts_streaming():
    """Test TTS streaming."""
    logger.info("Testing TTS Streaming")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sk-...":
        logger.warning("OPENAI_API_KEY not set, skipping streaming test")
        return
    
    provider = get_tts_provider("openai")
    
    try:
        await provider.initialize()
        
        text = "This is a streaming test. The audio will be generated in chunks."
        logger.info(f"Streaming synthesis: '{text}'")
        
        chunks = []
        async for result in provider.synthesize_stream(text=text, voice_id="nova"):
            logger.info(f"Received chunk: {len(result.audio_data)} bytes")
            chunks.append(result.audio_data)
        
        # Combine chunks
        full_audio = b"".join(chunks)
        logger.info(f"Total audio size: {len(full_audio)} bytes")
        
        # Save to file
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "streaming_tts_output.mp3"
        
        with open(output_file, "wb") as f:
            f.write(full_audio)
        
        logger.info(f"Streaming audio saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Error in streaming: {e}")
    finally:
        await provider.cleanup()


async def main():
    """Run all TTS examples."""
    logger.info("=" * 60)
    logger.info("TTS Provider Examples")
    logger.info("=" * 60)
    
    # Test OpenAI TTS
    await test_openai_tts()
    
    logger.info("\n" + "=" * 60 + "\n")
    
    # Test ElevenLabs
    await test_elevenlabs_tts()
    
    logger.info("\n" + "=" * 60 + "\n")
    
    # Test streaming
    await test_tts_streaming()
    
    logger.info("\n" + "=" * 60)
    logger.info("All TTS examples completed!")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

