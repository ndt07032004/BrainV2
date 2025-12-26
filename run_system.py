"""
One-click runner for BrainV2.

This script will:
- Start STT service (FastAPI + Faster-Whisper)
- Start TTS service (FastAPI + Edge-TTS)
- Start Web server (Flask)

All services run on local machine, optimized for Vietnamese realtime.
"""

import subprocess
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent

    cmds = [
        [sys.executable, "-m", "servers.stt_service"],
        [sys.executable, "-m", "servers.tts_service"],
        [sys.executable, "-m", "web.app_server"],
    ]

    processes = []
    try:
        for cmd in cmds:
            print("Starting:", " ".join(cmd))
            p = subprocess.Popen(cmd, cwd=str(root))
            processes.append(p)

        print("All services started. Press Ctrl+C to stop.")
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        print("Stopping all services...")
        for p in processes:
            try:
                p.terminate()
            except Exception:
                pass


if __name__ == "__main__":
    main()


