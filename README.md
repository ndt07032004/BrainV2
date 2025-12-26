BrainV2 - Trợ lý AI RAG tiếng Việt (STT → LLM → RAG → 3D Human → TTS)
========================================================================

### Tổng quan

**BrainV2** là một dự án trợ lý AI tiếng Việt, chạy **backend local-first**, tối ưu cho:

- **STT (Speech-to-Text)**: nghe giọng nói tiếng Việt (Faster-Whisper).
- **LLM (Gemini / Ollama)**: suy nghĩ, hiểu ngôn ngữ tự nhiên (NLU).
- **RAG (Retrieval-Augmented Generation)**: tìm kiến thức từ dữ liệu riêng (CSV → ChromaDB).
- **3D Human**: giao diện nhân vật 3D (GLB/GLTF) có thể gắn lip-sync / biểu cảm sau.
- **TTS (Text-to-Speech)**: trả lời bằng giọng nói tiếng Việt (Edge-TTS, miễn phí).

Hệ thống được chia thành **microservices**: `stt_service`, `tts_service`, `web(app_server)`, phần não RAG trong `src/core`.

---

### Kiến trúc thư mục

- **config/**
  - `settings.py`: cấu hình API keys, model, ports, paths.
- **data/**
  - `raw/`: dữ liệu gốc (ví dụ `dataset.csv`).
  - `vector_db/`: nơi lưu ChromaDB (hoặc bạn dùng lại `chroma_db_csv` hiện tại).
  - `prompts/system_prompt.txt`: prompt hệ thống cho trợ lý.
- **logs/**
  - `app.log`: file log chung.
- **servers/**
  - `stt_service.py`: server STT (FastAPI + Faster-Whisper).
  - `tts_service.py`: server TTS (FastAPI + Edge-TTS).
- **src/**
  - `core/llm_manager.py`: quản lý Gemini ↔ Ollama (qwen2.5:7b).
  - `core/rag_engine.py`: engine RAG dùng Chroma + LangChain.
  - `utils/audio_handler.py`: helper cho đường dẫn audio.
  - `ingestion/load_csv.py`: gọi script nạp CSV vào Chroma.
- **web/**
  - `app_server.py`: Flask web (UI + API `/api/chat`).
  - `static/css`, `static/js`, `static/models`, `static/audio_cache`.
  - `templates/index.html`: UI chat, chỗ sẵn cho 3D human.
- **run_system.py**: script 1-click chạy tất cả services.

---

### Yêu cầu hệ thống

- Python 3.10+ (khuyến nghị).
- Đã cài **Ollama** (ví dụ ở ổ `D:\Ollama`) và chạy service:
  - Mặc định API: `http://localhost:11434`.
  - Đã pull model: `ollama pull qwen2.5:7b`.
- GPU (nếu muốn STT nhanh với Faster-Whisper) hoặc CPU vẫn chạy được (chậm hơn).

---

### Cài đặt

```bash
pip install -r requirements.txt
```

Tạo file `.env` ở root:

```bash
GOOGLE_API_KEY=your_google_key_or_leave_empty
USE_GEMINI_PRIMARY=true

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_NAME=qwen2.5:7b

STT_MODEL_NAME=medium
STT_DEVICE=cuda  # hoặc cpu
STT_COMPUTE_TYPE=float16  # nếu GPU, nếu CPU có thể để int8

PERSIST_DIRECTORY=chroma_db_csv  # hoặc data/vector_db
```

---

### Chuẩn bị dữ liệu RAG

1. Đặt file CSV vào root (ví dụ `dataset.csv`) hoặc trong `data/raw/`.
2. Nạp dữ liệu vào Chroma (dùng script cũ thông qua wrapper mới):

```bash
python -m src.ingestion.load_csv
```

Sau khi chạy, vector DB sẽ nằm ở thư mục `PERSIST_DIRECTORY` (mặc định `chroma_db_csv` như project ban đầu).

---

### Chạy toàn hệ thống (1-click)

```bash
python run_system.py
```

Script này sẽ lần lượt khởi động:

- `servers.stt_service` (STT, cổng mặc định `8001`).
- `servers.tts_service` (TTS, cổng mặc định `8002`).
- `web.app_server` (Flask, cổng mặc định `8000`).

Sau khi chạy, mở trình duyệt:

```text
http://localhost:8000
```

Bạn có thể chat bằng text, hệ thống sẽ:

1. Gửi câu hỏi vào `RAG Engine`.
2. Lấy câu trả lời từ LLM (Gemini nếu có, fallback Ollama).
3. Gửi text sang `TTS Service` để tạo file audio.
4. UI phát lại audio tiếng Việt (Edge-TTS, giọng `vi-VN-HoaiMyNeural`).

---

### Ghi chú về 3D Human & Realtime

- File `web/templates/index.html` đã có **placeholder** cho khu vực nhân vật 3D.
- Bạn có thể:
  - Thêm Three.js hoặc Babylon.js vào `web/static/js`.
  - Load model `.glb/.gltf` từ `web/static/models`.
  - Gắn sự kiện khi có audio mới để điều khiển:
    - Chuyển động môi (lip-sync basic).
    - Biểu cảm dựa trên sentiment câu trả lời.
- Thiết kế hiện tại ưu tiên:
  - **Realtime**: STT và TTS là microservices độc lập.
  - **Local-first**: nếu mất mạng, Ollama vẫn trả lời được.

---

### Hướng mở rộng

- Thêm WebSocket để stream STT realtime thay vì upload file.
- Dùng pipeline:
  - Audio chunk → STT → NLU → Intent/Slot → LLM → TTS.
- Tối ưu latency:
  - Giảm kích thước model STT (`small`, `medium`).
  - Dùng GPU cho Faster-Whisper.
  - Dùng context window hợp lý cho LLM.

---

### Tóm tắt nhanh

- **Mục tiêu**: Trợ lý AI tiếng Việt RAG, realtime, free, chạy local (kết hợp Gemini/Ollama).
- **Luồng**: STT (Faster-Whisper) → LLM+RAG → TTS (Edge-TTS) → 3D Human.
- **Run**: `python run_system.py` rồi truy cập `http://localhost:8000`.


