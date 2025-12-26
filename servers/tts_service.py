"""
TTS microservice using Edge-TTS.

Expose a simple HTTP API (FastAPI) for text-to-speech.
Optimized for Vietnamese voice, saving audio into web static/audio_cache.
"""

import os
import uuid
import asyncio
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import edge_tts
import aiohttp

from utils.logger import get_logger
from config import settings

logger = get_logger(__name__)

app = FastAPI(title="BrainV2 TTS Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def generate_tts_with_retry(text: str, voice: str, file_path: str, max_retries: int = 3) -> bool:
    """
    Generate TTS with retry mechanism to handle Edge-TTS API errors.
    Returns True if successful, False otherwise.
    """
    for attempt in range(max_retries):
        try:
            communicate = edge_tts.Communicate(text=text, voice=voice)
            await communicate.save(file_path)
            return True
        except aiohttp.client_exceptions.WSServerHandshakeError as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # Exponential backoff: 2s, 4s, 6s
                logger.warning(f"Edge-TTS API error (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"Edge-TTS API failed after {max_retries} attempts: {e}")
                return False
        except Exception as e:
            logger.error(f"Unexpected error in TTS generation: {e}", exc_info=True)
            return False
    return False


@app.get("/speak")
async def speak(text: str):
    """
    Convert text to speech using Edge-TTS.
    Returns path (relative) to generated audio file.
    """
    if not text:
        return {"error": "text is required"}

    logger.info(f"TTS request: {text[:100]}...")  # Log only first 100 chars

    output_dir = settings.TTS_OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    file_id = uuid.uuid4().hex
    file_name = f"{file_id}.mp3"
    file_path = os.path.join(output_dir, file_name)

    # Edge-TTS voice for Vietnamese
    voice = settings.TTS_VI_VOICE

    # Try to generate TTS with retry
    success = await generate_tts_with_retry(text, voice, file_path)
    
    if not success:
        # Return error but don't crash - let frontend handle it
        logger.error(f"Failed to generate TTS for text: {text[:50]}...")
        raise HTTPException(
            status_code=503,
            detail="TTS service temporarily unavailable. Please try again later."
        )

    logger.info(f"TTS audio saved to: {file_path}")

    # Return web-accessible path (relative)
    rel_path = f"audio_cache/{file_name}"
    return {"audio_path": rel_path}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "servers.tts_service:app",
        host=settings.TTS_HOST,
        port=settings.TTS_PORT,
        reload=False,
    )


