# =============================================================================
# Stage: backend — Python / FastAPI (port 8000)
# Build: docker build --target backend -t lancerai-backend .
# =============================================================================
FROM python:3.11-slim AS backend

WORKDIR /opt/app

ENV UV_LINK_MODE=copy

# System deps: runtime-only libs needed by active packages.
# Including libraries for OCR (PaddleOCR/OpenCV, Poppler for PDF, Tesseract)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl ffmpeg \
    libffi-dev shared-mime-info \
    libgl1 libglib2.0-0 libgomp1 \
    libsm6 libxext6 libxrender-dev \
    poppler-utils tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy configuration files and README (required by pyproject.toml)
COPY pyproject.toml uv.lock README.md ./

# Use Docker BuildKit cache to speed up subsequent downloads if dependencies change
# First, install dependencies without the project itself to maximize layer caching
RUN --mount=type=cache,target=/root/.cache/uv \
    pip install --no-cache-dir uv && \
    uv sync --frozen --no-dev --no-install-project

# Copy the actual application code, migrations, and alembic.ini
COPY app/ ./app/
COPY alembic.ini ./
COPY migration/ ./migration/

# Sync the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Replace CUDA torch with CPU-only build (saves ~3-4 GB on CPU-only servers).
# uv does not install pip into .venv by default — use 'uv pip' instead.
RUN uv pip install --no-cache-dir \
    --python .venv \
    torch==2.5.1+cpu torchaudio==2.5.1+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Remove PaddlePaddle/PaddleOCR — CV OCR is MVP mock (uses pymupdf), not needed in prod.
# Saves ~700 MB from the final image.
RUN uv pip uninstall --python .venv paddlepaddle paddleocr paddle2onnx 2>/dev/null || true

EXPOSE 8000

CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# =============================================================================
# Stage: frontend — React + Vite (port 3000)
# Build: docker build --target frontend -t lancerai-frontend .
# =============================================================================
FROM node:22-alpine AS frontend

WORKDIR /app

COPY frontend/package*.json ./

# Use Docker BuildKit cache for npm
RUN --mount=type=cache,target=/app/.npm \
    npm set cache /app/.npm && \
    npm ci

COPY frontend/ .

EXPOSE 3000

CMD ["npm", "run", "dev"]

# =============================================================================
# Stage: frontend-prod — Build static assets, serve via nginx (port 3000)
# Dùng cho production: VITE_API_BASE_URL="" để gọi API relative qua Nginx proxy
# =============================================================================
FROM node:22-alpine AS frontend-builder

WORKDIR /app

COPY frontend/package*.json ./
RUN --mount=type=cache,target=/app/.npm \
    npm set cache /app/.npm && \
    npm ci

COPY frontend/ .

# Build-time arg: để rỗng để frontend gọi /api/ dạng relative URL qua Nginx
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# Serve static files via lightweight nginx
FROM nginx:1.27-alpine AS frontend-prod

COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# SPA fallback: mọi 404 trả về index.html (react-router)
RUN printf 'server {\n\
    listen 3000;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
    location /health {\n\
        access_log off;\n\
        return 200 "ok";\n\
    }\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
