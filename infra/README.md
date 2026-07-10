# `infra/` - Deployment Notes

This directory stores deployment notes. The main Docker files live at the repository root:

- `docker-compose.yml`
- `docker-compose.prod.yml`
- `Dockerfile`
- `nginx/`

## Local Development

Use root `docker-compose.yml` for local infrastructure only:

```bash
docker compose up -d
docker compose ps
docker compose down
```

Services:

- PostgreSQL
- Redis
- ChromaDB
- Neo4j

Run backend/frontend from local shells:

```bash
uv run uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```

## Production Compose

Use root `docker-compose.prod.yml`:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Services:

- `postgres`
- `redis`
- `chromadb`
- `neo4j`
- `backend`
- `celery_worker`
- `frontend`
- `nginx`

## Required Production Checks

- `.env` exists and contains real secrets.
- `APP_ENV=production`.
- `APP_DEBUG=false`.
- `AUTH_SECRET_KEY` is strong.
- `AUTH_ALLOW_WEAK_SECRET=false`.
- `ALLOWED_ORIGINS` contains deployed frontend origins.
- `FRONTEND_BASE_URL` points to deployed frontend.
- `DATABASE_URL`, Redis URLs, vector DB and Neo4j values match Docker service names.
- Nginx supports WebSocket upgrade for interview voice.
- Browser media is served over HTTPS, except localhost testing.

## Useful Health Checks

- Backend: `GET /health`, `GET /ready`
- Frontend container: `GET /health`
- Nginx: `GET /health`

## Notes

- Production backend image intentionally avoids large PaddleOCR/PaddlePaddle packages. OCR for scanned images may require a separate image/profile if needed.
- If `VITE_API_BASE_URL` is empty in production, frontend calls `/api/...` same-origin through Nginx.
