import asyncio
import os
import sys
from dotenv import load_dotenv

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv(".env.production")

from app.core.voice_stt_connector import VoiceSTTConnector
import numpy as np

async def main():
    print("=== Testing STT Connector Only ===")
    connector = VoiceSTTConnector()
    
    # We generate a 2-second sine wave (audio frequency 440Hz, sample rate 16000Hz)
    t = np.linspace(0, 2.0, 32000, False)
    sine_wave = np.sin(t * 2 * np.pi * 440) * 10000
    audio_data = sine_wave.astype(np.int16).tobytes()
    
    print("Calling transcribe...")
    result = await connector.transcribe(audio_data, sample_rate=16000)
    print(f"Transcribed Text: '{result}'")

if __name__ == "__main__":
    asyncio.run(main())
