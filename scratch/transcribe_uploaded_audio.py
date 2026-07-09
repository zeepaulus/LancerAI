import asyncio
import os
import sys
import httpx
from dotenv import load_dotenv

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv(".env.production")

from app.core.settings import get_settings

async def main():
    settings = get_settings()
    api_key = settings.llm_cloud_api_key
    if not api_key or api_key == "your-groq-api-key":
        api_key = os.getenv("GROQ_API_KEY") or ""
        
    if not api_key:
        print("Error: Groq API Key is not configured.")
        return

    file_path = r"C:\Users\DUY\.gemini\antigravity-ide\brain\aabea429-362b-4476-a667-4e0a0fb7cdf5\uploaded_media_1783607534638.img"
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return

    # 1. Read file bytes
    with open(file_path, "rb") as f:
        audio_bytes = f.read()

    # 2. Detect format based on header magic bytes
    header = audio_bytes[:12]
    print(f"File Size: {len(audio_bytes)} bytes")
    print(f"Header hex: {header.hex().upper()}")

    ext = "wav"
    mime = "audio/wav"

    if header.startswith(b"RIFF"):
        print("Detected format: WAV")
        ext = "wav"
        mime = "audio/wav"
    elif header.startswith(b"OggS"):
        print("Detected format: OGG/Opus")
        ext = "ogg"
        mime = "audio/ogg"
    elif header.startswith(b"ID3") or (len(header) > 2 and header[0] == 0xFF and (header[1] & 0xE0) == 0xE0):
        print("Detected format: MP3")
        ext = "mp3"
        mime = "audio/mp3"
    elif b"ftyp" in header:
        print("Detected format: M4A/MP4")
        ext = "m4a"
        mime = "audio/m4a"
    elif header.startswith(b"\x1a\x45\xdf\xa3"):
        print("Detected format: WEBM")
        ext = "webm"
        mime = "audio/webm"
    else:
        print("Detected format: Unknown (defaulting to webm/ogg based on size)")
        ext = "webm"
        mime = "audio/webm"

    # 3. Send to Groq transcriptions API
    print("Sending audio file to Groq Whisper...")
    
    files = {
        "file": (f"audio.{ext}", audio_bytes, mime)
    }
    data = {
        "model": "whisper-large-v3-turbo",
        "language": "vi",
    }
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers=headers,
                files=files,
                data=data
            )
            if response.status_code == 200:
                res_json = response.json()
                text = res_json.get("text", "").strip()
                print(f"\nTranscription Result:\n'{text}'")
            else:
                print(f"Groq API returned status code {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Error calling Groq API: {e}")

if __name__ == "__main__":
    asyncio.run(main())
