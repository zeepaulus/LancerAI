# `infra/` — Triển khai

Ghi chép và (tuỳ dự án) **Dockerfile** / manifest. File **`docker-compose.yml`**
nằm ở **gốc** repository cùng `app/`, `pyproject.toml` — bật **PostgreSQL**,
**Redis**, **Chroma**, **Neo4j** tùy môi trường.

```bash
docker compose up -d
docker compose ps
docker compose down
```

Biến môi trường backend phải khớp host/cổng dịch vụ. Không commit secret; dùng
`.env` (đã **gitignore**), mẫu tại `.env.example`.
