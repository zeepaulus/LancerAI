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

EXPOSE 8000

CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# =============================================================================
# Stage: frontend — React + Vite (port 3000)
# Build: docker build --target frontend -t lancerai-frontend .
# =============================================================================
FROM node:18-alpine AS frontend

WORKDIR /app

COPY frontend/package*.json ./

# Use Docker BuildKit cache for npm
RUN --mount=type=cache,target=/app/.npm \
    npm set cache /app/.npm && \
    npm install

COPY frontend/ .

EXPOSE 3000

CMD ["npm", "run", "dev"]
