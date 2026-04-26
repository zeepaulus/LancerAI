# LancerAI — hướng dẫn đóng góp

Tài liệu này quy định môi trường dev, tên **branch**/**commit**, tầng kiến trúc
(router → service → repository) và cách tìm chi tiết trong từng `README.md` dưới
`app/`, `docs/`, v.v.

## Môi trường

```bash
git clone https://github.com/<org>/lancerai.git
cd lancerai

uv sync
cp .env.example .env

docker compose up -d
# Chỉ chạy sau khi đã có file migration trong migration/alembic/versions/
uv run alembic upgrade head

uv run uvicorn app.main:app --reload
```

Cửa sổ khác: `cd frontend && npm install && npm run dev`

## Branch & commit

- **main** — ổn định release; **dev** (tuỳ team) — tích hợp; nhánh tính năng:
  `feat/<phạm vi>-<mô tả>`, sửa lỗi: `fix/...`, tài liệu: `docs/...`
- [Conventional Commits](https://www.conventionalcommits.org), ví dụ:  
  `feat(extraction): thêm trích xuất PDF từ PyMuPDF`

## Phân tầng

```
Router  →  Service  →  Repository  →  Models (ORM)
```

- **Router:** validate đầu vào, gọi service, trả **HTTP**/**WebSocket**; không nhét
  logic nghiệp vụ dài
- **Service:** điều phối, gọi repository và connector **AI**
- **Repository:** thao tác dữ liệu; truy vấn luôn gắn người dùng / tổ chức khi áp
  dụng
- **Models:** chỉ schema **ORM**

## Chuẩn mã

- **Python:** ruff theo `pyproject.toml` — gợi ý: type hints, docstring (Google) tiếng
  Anh cho API công khai
- **TypeScript / Next.js:** eslint-config-next
- **Test:** `uv run pytest`; mở rộng: `uv run pytest --cov=app --cov-report=html`

## Gợi ý phân công module

| Phạm vi | Thư mục / tệp chính | Ghi chú |
|---------|----------------------|--------|
| Trích xuất **CV** | `app/service/extraction_service.py` | PyMuPDF, **OCR** |
| Tối ưu **CV** | `app/service/agents/`, `optimization_service.py` | **LangGraph** |
| Matching | `app/service/matching_service.py` | Vector, **JD** |
| **Voice** | `app/service/interview/` | **STT**/**TTS**/**LLM** stream |
| **UI** | `frontend/` | Next.js |
| Hạ tầng | `docker-compose.yml`, `infra/` | DevOps |

## Bảo mật

- Không commit `.env`, khoá **API**, hay secret
- Không lộ full traceback tới client production
- Đường dẫn model: qua `settings` / **env**, không hardcode trong mã
- Mọi input **API** đi qua Pydantic trước khi xử lý nghiệp vụ
