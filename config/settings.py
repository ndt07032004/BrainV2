from dotenv import load_dotenv
import os

load_dotenv()

# --- API Keys & Cloud ---
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# If GOOGLE_API_KEY không có thì vẫn cho chạy (fallback Ollama)
if not GOOGLE_API_KEY:
    print("CẢNH BÁO: Không tìm thấy GOOGLE_API_KEY. Hệ thống sẽ dùng Ollama làm mặc định.")

USE_GEMINI_PRIMARY = os.environ.get("USE_GEMINI_PRIMARY", "true").lower() == "true"

# --- LLM Config ---

# Embedding tiếng Việt mạnh (768-d)
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

# Gemini model (nếu có internet + API key)
LLM_MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "gemini-2.5-flash")

# Ollama local model (cài ngoài ổ D:, nhưng API mặc định 11434)
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL_NAME = os.environ.get("OLLAMA_MODEL_NAME", "qwen2.5:7b")

# --- Paths (phải định nghĩa trước khi dùng) ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# --- Vector DB ---
# Mặc định: data/vector_db (cấu trúc mới)
# Nếu muốn dùng chroma_db_csv cũ, set PERSIST_DIRECTORY=chroma_db_csv trong .env
PERSIST_DIRECTORY = os.environ.get("PERSIST_DIRECTORY", os.path.join(DATA_DIR, "vector_db"))

# --- STT (Faster-Whisper) ---
STT_MODEL_NAME = os.environ.get("STT_MODEL_NAME", "medium")
STT_DEVICE = os.environ.get("STT_DEVICE", "cuda" if os.environ.get("USE_CUDA", "false").lower() == "true" else "cpu")
STT_COMPUTE_TYPE = os.environ.get("STT_COMPUTE_TYPE", "float16" if STT_DEVICE == "cuda" else "int8")
STT_HOST = os.environ.get("STT_HOST", "0.0.0.0")
STT_PORT = int(os.environ.get("STT_PORT", "8001"))

# --- TTS (Edge-TTS) ---
TTS_HOST = os.environ.get("TTS_HOST", "0.0.0.0")
TTS_PORT = int(os.environ.get("TTS_PORT", "8002"))
TTS_VI_VOICE = os.environ.get("TTS_VI_VOICE", "vi-VN-HoaiMyNeural")

# --- Web (Flask) ---
WEB_HOST = os.environ.get("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.environ.get("WEB_PORT", "8080"))

AUDIO_TEMP_DIR = os.environ.get("AUDIO_TEMP_DIR", os.path.join(DATA_DIR, "audio_temp"))
TTS_OUTPUT_DIR = os.environ.get("TTS_OUTPUT_DIR", os.path.join("web", "static", "audio_cache"))
