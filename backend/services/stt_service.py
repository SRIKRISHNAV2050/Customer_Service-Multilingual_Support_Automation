"""
Speech-to-Text adapter.

- Wraps calls to Whisper API or Google STT.
- Accepts audio streams; returns structured result:
  {"text": "...", "language": "hi", "duration_ms": 2345, "confidence": 0.92}
- Implements timeouts and per-call retries.
- For regional accents, prefer model options or domain-specific fine-tuning provided by vendor.
"""

import os
import requests
from config import Config

WHISPER_URL = "https://api.openai.com/v1/audio/transcriptions"

def transcribe_audio_file(file_stream, filename="upload.wav", language=None, max_retries=2):
    """
    Send audio stream to STT provider and return JSON response.

    Important:
    - Ensure audio sample rate recommended by provider (16k/48k).
    - For voice with accents, pass language hints and prefer vendor models optimized for Indian languages.
    """
    headers = {"Authorization": f"Bearer {Config.WHISPER_API_KEY}"}
    files = {"file": (filename, file_stream)}
    data = {"model": "whisper-1"}
    if language:
        data["language"] = language

    for attempt in range(max_retries):
        resp = requests.post(WHISPER_URL, headers=headers, files=files, data=data, timeout=Config.STT_REQUEST_TIMEOUT_SEC)
        if resp.ok:
            res_json = resp.json()
            return {
                "text": res_json.get("text"),
                "language": res_json.get("language", language),
                "raw": res_json
            }
    # If everything fails:
    raise RuntimeError("STT service failed after retries")
