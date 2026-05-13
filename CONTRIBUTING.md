# Hướng dẫn đóng góp — LancerAI

Tài liệu này mô tả quy trình phát triển, quy ước đặt tên branch và commit, nguyên tắc kiến trúc, tiêu chuẩn code, và cách submit thay đổi vào codebase.

---

## Thiết lập môi trường

### Yêu cầu

- Python 3.11+, Node.js 18+, [uv](https://docs.astral.sh/uv/), Docker

### Lần đầu thiết lập

```bash
git clone https://github.com/<org>/lancerai.git
cd lancerai

# Python environment
uv sync
cp .env.example .env
# Điền DATABASE_URL, AUTH_SECRET_KEY, cấu hình LLM vào .env

docker compose up -d

# Migration
uv run alembic upgrade head

# Khởi động backend
uv run uvicorn app.main:app --reload --port 8000

# Khởi động frontend (terminal khác)
cd frontend && npm install && npm run dev
```

---

## Quy trình làm việc

### Đặt tên branch

| Mục đích | Pattern | Ví dụ |
|---|---|---|
| Tính năng mới | `feat/<scope>-<mô-tả-ngắn>` | `feat/extraction-paddleocr` |
| Sửa lỗi | `fix/<scope>-<mô-tả-ngắn>` | `fix/auth-token-expiry` |
| Tài liệu | `docs/<chủ-đề>` | `docs/interview-pipeline` |
| Refactor | `refactor/<scope>` | `refactor/matching-service` |
| Hạ tầng | `infra/<chủ-đề>` | `infra/docker-compose-neo4j` |

Branch mới được tách từ `dev`. Merge vào `dev`, không merge thẳng vào `main`.

- **`main`** — ổn định, chỉ nhận release
- **`dev`** — integration branch; tất cả feature branch merge vào đây

### Commit message

Theo [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <mô tả ngắn>

[phần thân tùy chọn]
[footer: BREAKING CHANGE, closes #issue]
```

Các type được dùng: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`

Ví dụ:
```
feat(extraction): implement PDF text extraction với PyMuPDF
fix(auth): trả về 401 thay vì 500 khi thiếu Authorization header
docs(agents): bổ sung tài liệu LangGraph state schema
test(matching): thêm unit test cho Hybrid Scoring weights
```

### Pull Requests

1. Đảm bảo `uv run pytest` pass trên máy local trước khi mở PR.
2. Giữ PR tập trung — mỗi PR chỉ liên quan đến một module hoặc một vấn đề cụ thể.
3. Cập nhật `README.md` của module tương ứng nếu thay đổi behavior.
4. Cập nhật mục tương ứng trong `TODO.md` khi hoàn thành.
5. PR cần được review trước khi merge (theo quy ước nhóm).

---

## Kiến trúc — Mỗi thứ đặt ở đâu

Backend tuân theo kiến trúc phân tầng nghiêm ngặt. Mọi request đi qua các tầng theo thứ tự:

```
router/ → service/ → repository/ → models/
```

### Quy tắc từng tầng

| Tầng | Trách nhiệm | Không được phép |
|---|---|---|
| `router/` | Validate input, gọi service, trả về HTTP/WebSocket response | Chứa business logic, gọi repository trực tiếp |
| `service/` | Điều phối logic nghiệp vụ, gọi connector và repository | Gọi SQLAlchemy trực tiếp; biết về chi tiết HTTP |
| `repository/` | Đọc/ghi dữ liệu; luôn filter theo `user_id` hoặc `tenant_id` | Gọi LLM hoặc thực hiện tính toán nghiệp vụ |
| `models/` | Định nghĩa ORM schema và relationship | Chứa method vượt ra ngoài schema helper đơn giản |

### Dependency injection

Connector và repository singleton nằm trong `app/core/providers/` (thread-safe lazy init). `app/core/providers/services.py` khai báo `get_*_service`, `get_template_renderer`, và `get_interview_pipeline_factory` với `Depends(...)`. `app/core/providers/auth.py` cung cấp `get_current_user`. Không tạo connector/repo nặng trực tiếp trong router hay trong method service.

### Thêm tính năng mới

1. Định nghĩa Pydantic schema trong `app/schema/request.py` và `response.py`.
2. Thêm endpoint vào file `app/router/v1/*.py` tương ứng.
3. Implement logic trong `app/service/<module>/service.py` (hoặc package tương ứng).
4. Truy cập DB qua `RelationalRepository` / repository đã có — không SQL thô trong router.
5. Thêm provider trong `app/core/providers/services.py` nếu cần factory đặc biệt (ví dụ: `get_interview_pipeline_factory`).
6. Viết test trong `tests/`.

---

## Phân công module

| Module | File chính | Phạm vi |
|---|---|---|
| Auth | `app/service/auth/service.py`, `app/core/security.py`, `app/core/providers/auth.py` | JWT, password hashing, `get_current_user` |
| CV Extraction (M1) | `app/service/extraction/service.py`, `app/core/ocr_processor.py` | PyMuPDF, OCR, LLM structured output |
| CV Optimization (M2) | `app/service/optimization/`, `app/service/optimization/template_renderer.py` | LangGraph agents, template render |
| Job Matching (M3) | `app/service/matching/service.py`, `app/repository/vector_repository.py` | Hybrid scoring, vector search |
| Voice Interview (M4) | `app/service/interview/`, `app/core/voice_*_connector.py` | STT, TTS, pipeline WebSocket, STAR |
| Frontend | `frontend/src/` | React + Vite pages, API integration, WebSocket audio |
| Hạ tầng | `docker-compose.yml`, `migration/` | Docker, Alembic, CI |

---

## Tiêu chuẩn code

### Python

- Formatter và linter: **ruff** — cấu hình trong `pyproject.toml`. Chạy `uv run ruff check .` trước khi commit.
- Type hints bắt buộc trên tất cả function và method công khai.
- Docstring: theo Google style, viết bằng tiếng Anh cho các API surface công khai.
- Async: dùng `async def` nhất quán cho các thao tác I/O-bound. Không gọi blocking code bên trong async function.
- Connector method mới nên theo pattern stub (raise `NotImplementedError` kèm message mô tả) cho đến khi có implementation đầy đủ.

### JavaScript / React

- Chưa có script `lint` / ESLint trong `frontend/package.json`; khi bổ sung cấu hình thì thêm script và ghi vào README module frontend.
- Ưu tiên kiểu rõ ràng, tránh `any` ngầm định.

### Testing

Chạy test:
```bash
uv run pytest
```

Kèm báo cáo coverage:
```bash
uv run pytest --cov=app --cov-report=html
```

- Unit test nằm trong `tests/` và phản ánh cấu trúc của `app/`.
- Với service hoặc repository mới, viết ít nhất một test cho happy path và một test cho edge case / lỗi.
- `tests/conftest.py` cung cấp fixture SQLite async; integration test full stack Compose có thể bổ sung sau.

---

## Quy tắc bảo mật

- Không commit `.env`, API key, hay secret. Các thông tin nhạy cảm thuộc về `.env` (đã git-ignore) hoặc secrets manager.
- Không để lộ full stack trace ra client trong production (`APP_DEBUG=false`).
- Mọi input từ bên ngoài phải đi qua Pydantic schema trước khi đến service code.
- Đường dẫn model/asset phải được cấu hình qua environment variable, không hardcode trong source.
- Mọi database query đọc dữ liệu của user phải filter theo `user_id` (và `tenant_id` khi multi-tenancy được bật).

---

## Các lệnh thường dùng

```bash
# Chạy linter
uv run ruff check app tests

# Chạy type checker
uv run mypy app tests

# Chạy tests
uv run pytest

# Xuất requirements.txt từ uv lock
uv export --frozen --no-dev --no-hashes --format requirements.txt -o requirements.txt

# Tạo Alembic migration mới
uv run alembic revision --autogenerate -m "mô tả thay đổi"
uv run alembic upgrade head
```
