"""
STT microservice using Faster-Whisper.

Expose a simple HTTP API (FastAPI) for audio transcription.
Optimized for Vietnamese realtime transcription (short chunks).
"""

import os
import warnings
from contextlib import asynccontextmanager
from typing import Optional

# Suppress known warnings BEFORE importing faster_whisper (which imports ctranslate2)
warnings.filterwarnings("ignore", message=".*pkg_resources is deprecated.*")
warnings.filterwarnings("ignore", category=UserWarning, module="ctranslate2")

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel

from utils.logger import get_logger
from config import settings

logger = get_logger(__name__)


def load_whisper_model() -> WhisperModel:
    """Load Faster-Whisper model with config from settings."""
    model_size = settings.STT_MODEL_NAME
    device = settings.STT_DEVICE
    compute_type = settings.STT_COMPUTE_TYPE

    logger.info(
        f"Loading Faster-Whisper model: size={model_size}, device={device}, compute_type={compute_type}"
    )
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    return model


whisper_model: Optional[WhisperModel] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI startup/shutdown."""
    # Startup
    global whisper_model
    whisper_model = load_whisper_model()
    logger.info("STT service is ready.")
    yield
    # Shutdown (if needed)
    whisper_model = None


app = FastAPI(
    title="BrainV2 STT Service",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe an uploaded audio file (e.g., wav, mp3).
    This is designed for short audio chunks to keep latency low.
    """
    if whisper_model is None:
        return {"error": "Model is not loaded yet"}

    # Save to temp file
    tmp_dir = settings.AUDIO_TEMP_DIR
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, file.filename)

    with open(tmp_path, "wb") as f:
        content = await file.read()
        f.write(content)

    logger.info(f"Received audio file for STT: {tmp_path}")

    segments, _ = whisper_model.transcribe(
        tmp_path,
        language="vi",
        beam_size=1,
        vad_filter=True,
        condition_on_previous_text=False,
    )

    text_parts = [segment.text.strip() for segment in segments]
    text = " ".join(text_parts).strip()

    logger.info(f"Transcription result: {text}")

    # Optionally delete temp file to keep disk clean
    try:
        os.remove(tmp_path)
    except Exception:
        pass

    return {"text": text}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "servers.stt_service:app",
        host=settings.STT_HOST,
        port=settings.STT_PORT,
        reload=False,
    )


