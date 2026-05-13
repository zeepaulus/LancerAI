# `migration/` — Alembic

Lược đồ **PostgreSQL** sinh từ **ORM** `app/models/`. Thiết lập: **`alembic.ini`**
(ở gốc repo) — `script_location` trỏ `migration/alembic/`.

```bash
uv run alembic revision --autogenerate -m "mô tả ngắn"
uv run alembic upgrade head
uv run alembic history
```

Thư mục `migration/alembic/versions/` chứa revision Alembic; sau `autogenerate` cần rà diff (tên index, nullable, …).
