"""
Voice channel endpoints.

- POST /upload  -> Accept file multipart, transcribe via STT, forward to chat pipeline.
- Response can be returned as audio (TTS) or text depending on Accept header.

Performance notes:
- STT and LLM calls must be parallelized where possible.
- For longer audio, accept streaming or chunked uploads and return partial transcripts.
"""

from flask import Blueprint, request, jsonify, send_file
from services.stt_service import transcribe_audio_file
from services.tts_service import synthesize_speech
from routes.chat import _get_or_create_conversation, _fetch_recent_messages
from services.llm_service import call_llm
from extensions import db
from models import Message

voice_bp = Blueprint("voice", __name__)

@voice_bp.route("/upload", methods=["POST"])
def upload_audio():
    """
    Multipart form:
      - file: audio file (wav/mp3)
      - user_id
      - conversation_id (optional)
      - accept_audio: bool (if True return audio TTS)
    """
    if 'file' not in request.files:
        return jsonify({"error": "audio file required"}), 400
    file = request.files['file']
    user_id = request.form.get('user_id')
    conv_id = request.form.get('conversation_id')
    accept_audio = request.form.get('accept_audio', "true").lower() == "true"
    locale = request.form.get('locale', None)

    # Transcribe (blocking or async depending on SLA)
    stt_result = transcribe_audio_file(file.stream, language=locale)  # returns dict {'text':..., 'language':...}

    # Reuse text pipeline
    # ... create conversation, store user message, call LLM ...
    # final_reply_text = ...

    # Optionally synthesize TTS
    if accept_audio:
        audio_file_path = synthesize_speech(final_reply_text, voice="en-IN")
        return send_file(audio_file_path, mimetype="audio/mpeg")
    else:
        return jsonify({"reply": final_reply_text, "transcript": stt_result.get("text")})
