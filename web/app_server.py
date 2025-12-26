"""
Main web server for BrainV2 (Flask).

Responsibilities:
- Serve index.html (3D human UI sẽ được thêm sau).
- Provide REST API endpoint to:
  - Receive text (from STT or keyboard).
  - Query RAG engine.
  - Call TTS service to generate voice.

This is designed to be lightweight and realtime-friendly.
"""

from __future__ import annotations

import os
import requests
from flask import Flask, render_template, request, jsonify

from src.core.rag_engine import rag_engine
from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static"),
)

# Tắt proxy cho requests (tránh lỗi ProxyError khi gọi localhost)
os.environ.setdefault("NO_PROXY", "localhost,127.0.0.1,0.0.0.0")
os.environ.setdefault("no_proxy", "localhost,127.0.0.1,0.0.0.0")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/test")
def test():
    """Test endpoint to verify server is running."""
    return jsonify({"status": "ok", "message": "Server is running"})


@app.route("/api/test-rag")
def test_rag():
    """Test endpoint to verify RAG engine is working."""
    try:
        test_question = "Xin chào"
        answer = rag_engine.get_answer(test_question)
        return jsonify({
            "status": "ok",
            "rag_engine": "connected",
            "test_question": test_question,
            "answer": answer[:100] if answer else "No answer"
        })
    except Exception as e:
        logger.error(f"RAG test error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "rag_engine": "error",
            "error": str(e)
        }), 500


@app.route("/ws")
def websocket_placeholder():
    """WebSocket endpoint placeholder."""
    return jsonify({
        "status": "not_implemented",
        "message": "WebSocket endpoint not implemented"
    }), 501


@app.route("/static/<path:filename>")
def serve_static(filename):
    """Serve static files including audio cache."""
    from flask import send_from_directory
    return send_from_directory(app.static_folder, filename)


@app.post("/api/chat")
def api_chat():
    """
    Main API:
    - input: { "text": "..." }
    - output: { "answer": "...", "audio_path": "audio_cache/xxx.mp3" }
    """
    data = request.get_json(force=True)
    user_text = (data or {}).get("text", "").strip()
    if not user_text:
        return jsonify({"error": "text is required"}), 400

    logger.info(f"Web chat request: {user_text}")
    answer = rag_engine.get_answer(user_text)

    # Call TTS service
    # Sử dụng localhost thay vì 0.0.0.0 để tránh lỗi proxy
    audio_path = None
    try:
        tts_host = "localhost" if settings.TTS_HOST == "0.0.0.0" else settings.TTS_HOST
        tts_url = f"http://{tts_host}:{settings.TTS_PORT}/speak"
        # Tắt proxy cho request này
        session = requests.Session()
        session.trust_env = False  # Không dùng proxy từ env
        r = session.get(tts_url, params={"text": answer}, timeout=60)
        r.raise_for_status()
        audio_path = r.json().get("audio_path")
        logger.info(f"TTS audio generated: {audio_path}")
    except requests.exceptions.HTTPError as e:
        # TTS service returned error (503, etc.)
        logger.warning(f"TTS service returned error: {e.response.status_code if hasattr(e, 'response') else 'unknown'}")
        audio_path = None
    except requests.exceptions.RequestException as e:
        # Network/connection error
        logger.warning(f"TTS service connection error: {e}")
        audio_path = None
    except Exception as e:
        # Other unexpected errors
        logger.error(f"TTS service call failed: {e}", exc_info=True)
        audio_path = None

    # Always return answer, even if TTS failed
    return jsonify({
        "answer": answer,
        "audio_path": audio_path,
        "tts_available": audio_path is not None
    })


if __name__ == "__main__":
    app.run(host=settings.WEB_HOST, port=settings.WEB_PORT, debug=False)


