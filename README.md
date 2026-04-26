<div align="center">

# LancerAI

**Hệ trợ lý sự nghiệp bằng AI — trích xuất & tối ưu CV, gợi ý việc làm, phỏng vấn giọng nói**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)

[Tổng quan](#tổng-quan) · [Tech stack](#tech-stack) · [Phạm vi](#phạm-vi-sản-phẩm) · [Thiết lập](#thiết-lập) · [Mô hình & biến môi trường](#mô-hình-asset--biến-môi-trường) · [Cấu trúc repo](#cấu-trúc-thư-mục)

</div>

---

## Tổng quan

**LancerAI** là nền tảng hỗ trợ ứng viên, có thể phục vụ nhiều tổ chức trên cùng
một hệ thống và tách dữ liệu theo tài khoản. Ứng viên có thể tải **CV**
(PDF/ảnh), trích xuất cấu trúc, chạy pipeline **LangGraph** (tìm dữ liệu liên
quan → góp ý thẳng → viết lại → kiểm tra), so khớp với mô tả công việc (**JD**),
và mô phỏng phỏng vấn realtime qua **WebSocket** (luồng **PCM** → **STT** →
**LLM** → **TTS**).

**Backend** FastAPI tách tầng **router** → **service** → **repository**; phần
gắn kết phụ thuộc nằm tại `app/core/dependencies.py`. **Frontend** Next.js phục
vụ giao diện và tích hợp **API**/**WS**. Chi tiết kiến trúc, cách tách dữ liệu
theo tổ chức và pipeline:  
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## Tech stack

| Tầng | Công nghệ |
|------|-----------|
| **API** | **FastAPI**, **Pydantic v2**, **Uvicorn** — OpenAPI tại `/docs` |
| **CSDL** | **PostgreSQL**, **SQLAlchemy 2.0** (async), **asyncpg** |
| **Schema** | **Alembic** — `alembic.ini` (gốc repo) + `migration/alembic/` |
| **Hàng đợi** | **Redis**, **Celery** — `app/workers/` |
| **Vector / RAG** | **ChromaDB** (có thể thay Qdrant) — `VectorRepository` |
| **Graph** | **Neo4j** — `GraphRepository` |
| **AI orchestration** | **LangGraph**, **langchain-core** — tối ưu **CV** (`app/service/agents/`) |
| **LLM** | **Ollama** (local), tùy chọn **Groq** (OpenAI-compatible) |
| **OCR** | **PaddleOCR** |
| **STT** | **vinai/PhoWhisper-base** — **Transformers** |
| **TTS** | **edge-tts** / **Piper** / **VieNeu** |
| **Tài liệu** | **PyMuPDF**, **WeasyPrint**, **python-docx** |
| **UI** | **Next.js 16** (App Router), **React 19** |
| **Python** | **uv** — `pyproject.toml`, `uv.lock` |
| **Test** | **pytest** |

---

## Phạm vi sản phẩm

| Mã | Chức năng | API (prefix `/api/v1`) |
|----|------------|-------------------------|
| **M0** | Xác thực, tách dữ liệu theo tổ chức/tài khoản, **JWT** | `/auth/...` |
| **M1** | Trích xuất **CV** (PDF/ảnh → cấu trúc) | `/extraction/...` |
| **M2** | Tối ưu **CV** (LangGraph), template, xuất **PDF** | `/optimization/...` |
| **M3** | So khớp **CV**–**JD**, gợi ý vị trí | `/jobs/...` |
| **M4** | Phỏng vấn **voice** (**STT** / **TTS** / chấm **STAR**) | `/interview/...` + **WS** |
| **M5** | **Worker** nền (crawl **JD**, xuất tài liệu) | Tích hợp từ service / lịch |

Kế hoạch chi tiết theo từng tầng: [`TODO.md`](TODO.md). Phân công: cập nhật bảng
trong [`CONTRIBUTING.md`](CONTRIBUTING.md). Mô tả từng thư mục: `README.md` con
dưới `app/`, `frontend/`, v.v.

---

## Thiết lập

**Yêu cầu:** Python 3.11+, **Node.js** 20+, **uv**, Docker (khuyến nghị cho
PostgreSQL / Redis / Chroma / Neo4j), **Ollama** khi dùng **LLM** local theo
`LLM_LOCAL_MODEL` (mặc định: `qwen2.5:3b`).

**Backend** (từ thư mục gốc repository — tên thư mục có thể đặt `lancerai`):

```bash
uv sync
cp .env.example .env
# Thiết lập .env: DATABASE_URL, STT, TTS, Ollama, LLM, ...
uv run uvicorn app.main:app --reload --port 8000
```

- Tài liệu **API:** http://localhost:8000/docs  
- **Health:** http://localhost:8000/health  

Phụ thuộc Python: `uv sync`. Cần file **pip** tương đương:  
`uv export --format requirements-txt -o requirements.txt`

**CSDL & dịch vụ nền:**

```bash
docker compose up -d
# Chỉ chạy sau khi đã có file migration trong migration/alembic/versions/
uv run alembic upgrade head
```

**Frontend:**

```bash
cd frontend && npm install && npm run dev
```

URL **API** cho browser: `NEXT_PUBLIC_API_BASE_URL` trong `frontend/.env.local`.

**Test:**

```bash
uv run pytest
```

---

## Mô hình, asset & biến môi trường

| Thành phần | Gợi ý | Biến (tham chiếu) |
|-------------|--------|-------------------|
| **LLM** (Ollama) | Cài Ollama, kéo model | `LLM_LOCAL_BASE_URL`, `LLM_LOCAL_MODEL` |
| **STT** (PhoWhisper) | Tải từ HuggingFace lần đầu chạy | `STT_MODEL_ID`, `STT_DEVICE` |
| **TTS** (VieNeu) | File GGUF / asset theo SDK; thư mục `models/` thường ngoài **git** | `TTS_ENGINE`, `TTS_MODEL_PATH`, `TTS_VOICE` |
| **TTS** (Edge) | Dịch vụ Microsoft, cần mạng | `TTS_ENGINE=edge`, `TTS_VOICE` |
| **LLM** cloud | **Groq** / OpenAI-compatible | `LLM_CLOUD_API_KEY`, … |

Chi tiết: [`.env.example`](.env.example). Trọng số mẫu lớn nằm ngoài repo (xem
`.gitignore`).

---

## Cấu trúc thư mục

```
lancerai/                  
├── app/                   # Backend FastAPI
├── docs/                  # Kiến trúc
├── frontend/              # Next.js
├── migration/             # Alembic
├── tests/
├── docker-compose.yml
├── infra/
├── pyproject.toml
├── TODO.md
├── CONTRIBUTING.md
└── uv.lock
```

**Quy ước dữ liệu:** mọi truy vấn tài nguyên theo người dùng phải lọc `user_id`
và lọc thêm `tenant_id` khi dữ liệu được tách theo tổ chức. Chi tiết:
`app/repository/README.md`.

---

## Tài liệu

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — kiến trúc, tách dữ liệu theo tổ chức, pipeline
- [`TODO.md`](TODO.md) — hạng mục triển khai
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — branch, **commit**, chuẩn mã

## License

License khai báo trong `pyproject.toml` là **MIT**. Khi phát hành chính thức,
nên bổ sung file `LICENSE` ở gốc repo.
