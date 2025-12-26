"""
Audio helper utilities.

At this stage we keep this minimal: mainly path helpers for temp audio,
so the STT/TTS services and the web app can share the same conventions.
"""

import os
from config import settings


def get_temp_audio_dir() -> str:
    os.makedirs(settings.AUDIO_TEMP_DIR, exist_ok=True)
    return settings.AUDIO_TEMP_DIR


def get_tts_output_dir() -> str:
    os.makedirs(settings.TTS_OUTPUT_DIR, exist_ok=True)
    return settings.TTS_OUTPUT_DIR



