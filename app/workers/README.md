# `workers/` — Celery

Tác vụ nền: crawl tin **JD**, xuất **PDF**/**DOCX** từ dữ liệu CV, không chạy trong
một request **HTTP** dài.

**Thiết lập:** `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` (`.env`). Entrypoint
**Celery** gắn với ứng dụng khi tích hợp (module chứa `Celery` app).

Công nghệ: `celery[redis]`, tuỳ tác vụ: **Scrapy** / **Playwright**, **WeasyPrint**,
**python-docx**.
