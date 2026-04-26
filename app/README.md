# `app/` — Backend LancerAI (FastAPI)

Gói Python chứa toàn bộ server: `main.py`, **router**, **service**, **repository**,
**models**, **core** (thiết lập, gắn kết phụ thuộc, connector **LLM** / **STT** /
**TTS** / **OCR**).

## Luồng chuẩn

```
HTTP / WebSocket
  → router/v1/*     (validate, Depends)
  → service/*       (nghiệp vụ, agent, pipeline)
  → repository/*    (truy cập dữ liệu)
  → models/*        (ORM)
```

## Thư mục

| Đường dẫn | Nội dung |
|-----------|----------|
| `core/` | Settings, DB, lifespan, logger, **security**, connector **AI**, gắn kết phụ thuộc |
| `models/` | Bảng **ORM** |
| `repository/` | CRUD generic, vector, graph |
| `schema/` | Pydantic **API** |
| `router/v1/` | **REST** + **WebSocket** |
| `service/` | Auth, extraction, optimization, matching, interview |
| `service/agents/` | LangGraph tối ưu CV |
| `service/interview/` | Pipeline phỏng vấn **voice** |
| `workers/` | Tác vụ **Celery** |

## Nguyên tắc tách dữ liệu

Mọi dữ liệu theo người dùng hoặc tổ chức phải lọc đúng phạm vi ở service +
repository.

Xem thêm: [`../TODO.md`](../TODO.md), từng `README.md` con.
