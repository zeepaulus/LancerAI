import asyncio
import os
import sys
from dotenv import load_dotenv

# Reconfigure stdout to support UTF-8 on Windows command line
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add app to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load env variables from .env.production
load_dotenv(".env.production")

from app.core.llm_connector import LLMConnector
from app.core.voice_stt_connector import VoiceSTTConnector
from app.core.settings import get_settings

async def test_llm():
    print("=== Testing LLM Connector ===")
    settings = get_settings()
    print(f"Groq API Key: {settings.llm_cloud_api_key[:15]}...")
    print(f"Nvidia API Key: {settings.llm_nvidia_api_key[:15]}...")
    
    connector = LLMConnector(
        local_base_url=settings.llm_local_base_url,
        local_model=settings.llm_local_model,
        cloud_base_url=settings.llm_cloud_base_url,
        cloud_api_key=settings.llm_cloud_api_key,
        cloud_model=settings.llm_cloud_model,
        nvidia_base_url=settings.llm_nvidia_base_url,
        nvidia_api_key=settings.llm_nvidia_api_key,
        nvidia_model=settings.llm_nvidia_model,
    )
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Chào bạn, hãy trả lời ngắn gọn trong 5 từ."}
    ]
    
    # Test Groq first
    print("\n1. Testing with use_cloud=True (should prioritize Groq)...")
    try:
        response = await connector.generate_chat(messages, use_cloud=True)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Groq failed: {e}")

    # Test Nvidia specifically
    print("\n2. Testing with use_nvidia=True (should prioritize Nvidia)...")
    try:
        response = await connector.generate_chat(messages, use_nvidia=True)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Nvidia failed: {e}")

    # Test Fallback (invalid key for Groq to trigger Nvidia fallback)
    print("\n3. Testing Fallback (breaking Groq Key)...")
    broken_connector = LLMConnector(
        local_base_url=settings.llm_local_base_url,
        local_model=settings.llm_local_model,
        cloud_base_url=settings.llm_cloud_base_url,
        cloud_api_key="gsk_broken_placeholder_key_invalid",
        cloud_model=settings.llm_cloud_model,
        nvidia_base_url=settings.llm_nvidia_base_url,
        nvidia_api_key=settings.llm_nvidia_api_key,
        nvidia_model=settings.llm_nvidia_model,
    )
    try:
        response = await broken_connector.generate_chat(messages, use_cloud=True)
        print(f"Response (should fallback to Nvidia NIM): {response}")
    except Exception as e:
        print(f"Fallback failed: {e}")

async def test_stt():
    print("\n=== Testing STT Connector ===")
    connector = VoiceSTTConnector()
    
    # We create 1 second of silent PCM 16kHz audio
    # 1 second * 16000 samples/sec * 2 bytes/sample = 32000 bytes
    silent_audio = b"\x00" * 32000
    
    print("Testing transcription with dummy sine audio...")
    try:
        import numpy as np
        t = np.linspace(0, 1.0, 16000, False)
        # Generate a sine wave of 440 Hz
        sine_wave = np.sin(t * 2 * np.pi * 440) * 10000
        audio_data = sine_wave.astype(np.int16).tobytes()
        
        # Test Groq STT
        result = await connector.transcribe(audio_data, sample_rate=16000)
        print(f"Transcribed Text (Groq): '{result}'")
    except Exception as e:
        print(f"STT failed: {e}")

async def main():
    await test_llm()
    await test_stt()

if __name__ == "__main__":
    asyncio.run(main())
