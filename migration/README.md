# `migration/` — Alembic

Lược đồ **PostgreSQL** sinh từ **ORM** `app/models/`. Thiết lập: **`alembic.ini`**
(ở gốc repo) — `script_location` trỏ `migration/alembic/`.

```bash
uv run alembic revision --autogenerate -m "mô tả ngắn"
uv run alembic upgrade head
uv run alembic history
```

Hiện thư mục `migration/alembic/versions/` chưa có revision gốc. Tạo revision
đầu tiên trước khi chạy `uv run alembic upgrade head`. Sau `autogenerate` luôn rà
soát diff (đổi tên cột, index, ...).
