# Hướng Dẫn Đóng Góp - LancerAI

Tài liệu này mô tả cách thiết lập môi trường, quy trình làm việc, tiêu chuẩn code và quality gates khi đóng góp vào LancerAI.

## Thiết Lập Môi Trường

### Yêu cầu

- Python 3.11+
- uv
- Node.js 22 khuyến nghị
- Docker và Docker Compose
- Ollama hoặc API key LLM nếu chạy flow AI thật

### Cài đặt lần đầu

```bash
git clone https://github.com/zeepaulus/LancerAI.git
cd LancerAI

cp .env.example .env
cp frontend/.env.example frontend/.env

docker compose up -d

uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000
```

Terminal frontend:

```bash
cd frontend
npm install
npm run dev
```

Backend: http://localhost:8000

Frontend: http://localhost:3000

## Quy Trình Làm Việc

### Branch

| Mục đích | Pattern | Ví dụ |
|---|---|---|
| Feature | `feat/<scope>-<short-desc>` | `feat/interview-events` |
| Fix | `fix/<scope>-<short-desc>` | `fix/cv-upload-timeout` |
| Docs | `docs/<topic>` | `docs/project-readme-refresh` |
| Refactor | `refactor/<scope>` | `refactor/matching-service` |
| Test | `test/<scope>` | `test/topcv-crawler` |
| Infra | `infra/<topic>` | `infra/prod-compose-nginx` |

Nếu team đang dùng branch integration riêng, feature branch nên tách từ branch đó. Nếu project làm trực tiếp trên `main`, hãy giữ PR nhỏ và có test rõ ràng.

### Commit Message

Dùng Conventional Commits:

```text
<type>(<scope>): <short summary>
```

Types thường dùng:

- `feat`
- `fix`
- `docs`
- `refactor`
- `test`
- `chore`
- `ci`
- `infra`

Ví dụ:

```text
feat(extraction): add unreadable CV validation
fix(interview): persist transcript on disconnect
docs(readme): refresh setup and API reference
test(matching): cover semantic-score fallback
```

## Kiến Trúc Và Quy Tắc Lớp

Backend đi theo luồng:

```text
router -> service -> repository / connector -> external system
```

| Layer | Được làm | Không nên làm |
|---|---|---|
| `router/` | Validate request, auth, rate limit, gọi service | Business logic dài, SQL trực tiếp |
| `service/` | Điều phối nghiệp vụ, gọi repository/connector | Phụ thuộc FastAPI `Depends`, biết chi tiết HTTP |
| `repository/` | Truy cập DB/vector/graph/cache | Gọi LLM hoặc xử lý nghiệp vụ |
| `models/` | ORM schema và relationships | Logic nghiệp vụ phức tạp |
| `schema/` | API contracts | Logic xử lý |
| `core/` | Settings, providers, security, connectors | Product workflow |

## Thêm Tính Năng Mới

1. Cập nhật schema trong `app/schema/request.py` và `app/schema/response.py` nếu API contract thay đổi.
2. Thêm hoặc sửa route trong `app/router/v1/`.
3. Implement logic trong `app/service/<module>/`.
4. Dùng repository/provider hiện có thay vì tự tạo connection trong route.
5. Thêm migration nếu model/schema DB thay đổi.
6. Thêm hoặc cập nhật tests.
7. Cập nhật README/docs liên quan.

## Quality Gates

Backend:

```bash
uv run pytest
uv run ruff check app tests
uv run mypy app tests
```

Frontend:

```bash
cd frontend
npm run build
```

Migration:

```bash
uv run alembic upgrade head
```

Integration tests, khi có hạ tầng cần thiết:

```bash
uv run pytest -m integration
```

## Testing Guidelines

Thêm test cho:

- Happy path.
- Validation/error path.
- Ownership checks cho resource theo user.
- Fallback khi LLM/vector/graph/STT/TTS unavailable.
- Worker result payload và retry behavior.
- Pydantic schema validation khi thêm field.

Test suite hiện dùng SQLite in-memory cho nhiều unit tests; các test cần Docker services nên đánh dấu `@pytest.mark.integration`.

## Security Guidelines

- Không commit `.env`, API keys hoặc secret.
- Production không được bật `AUTH_ALLOW_WEAK_SECRET`.
- Không expose stack trace ra client khi `APP_DEBUG=false`.
- Mọi endpoint dùng `cv_id`, `session_id`, `job_id` cần ownership check.
- URL do user cung cấp phải kiểm tra SSRF/private IP nếu backend fetch.
- Upload file cần size/type validation; ưu tiên thêm magic-byte validation cho flow mới.
- Không log raw secret, token hoặc password.

## Documentation Guidelines

Khi thay đổi behavior, cập nhật ít nhất một tài liệu tương ứng:

- Root [README.md](README.md) nếu thay đổi setup/API/feature status.
- `docs/SYSTEM_OVERVIEW.md` nếu thay đổi kiến trúc.
- `docs/FLOW_STUDY_CASES.md` nếu thay đổi flow hoặc failure mode.
- `app/*/README.md` nếu thay đổi module internals.
- `TODO.md` nếu hoàn thành hoặc thêm backlog.

## Pull Request Checklist

- Tests liên quan đã chạy.
- Lint/type check đã chạy hoặc nêu rõ chưa chạy.
- Migration được kiểm tra thủ công nếu có.
- README/docs được cập nhật khi behavior thay đổi.
- Không có secret hoặc file local-only trong diff.
- PR tập trung vào một mục tiêu rõ ràng.
