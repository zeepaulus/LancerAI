#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-lancerai}"
ENV_FILE="${ENV_FILE:-.env}"
DEPLOY_STATE_DIR="${DEPLOY_STATE_DIR:-.deploy}"
BACKUP_DIR="${BACKUP_DIR:-backups}"
HEALTH_URL="${HEALTH_URL:-http://localhost/health}"
READY_URL="${READY_URL:-http://localhost/ready}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost/}"

: "${BACKEND_IMAGE:?BACKEND_IMAGE is required}"
: "${FRONTEND_IMAGE:?FRONTEND_IMAGE is required}"

mkdir -p "$DEPLOY_STATE_DIR" "$BACKUP_DIR"

if [ ! -f "$ENV_FILE" ]; then
    echo "Missing env file: $ENV_FILE" >&2
    exit 1
fi

compose() {
    ENV_FILE="$ENV_FILE" \
    BACKEND_IMAGE="$BACKEND_IMAGE" \
    FRONTEND_IMAGE="$FRONTEND_IMAGE" \
    docker compose -f "$COMPOSE_FILE" --project-name "$COMPOSE_PROJECT_NAME" "$@"
}

wait_for_http() {
    local url="$1"
    local timeout_seconds="${2:-90}"
    local started_at
    started_at="$(date +%s)"

    until curl -fsS "$url" >/dev/null; do
        if [ $(( $(date +%s) - started_at )) -ge "$timeout_seconds" ]; then
            echo "Timed out waiting for $url" >&2
            return 1
        fi
        sleep 3
    done
}

wait_for_service() {
    local service="$1"
    local timeout_seconds="${2:-120}"
    local started_at
    started_at="$(date +%s)"

    while true; do
        local container_id status
        container_id="$(compose ps -q "$service" 2>/dev/null || true)"
        if [ -n "$container_id" ]; then
            status="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$container_id" 2>/dev/null || true)"
            if [ "$status" = "healthy" ] || [ "$status" = "running" ]; then
                return 0
            fi
            if [ "$status" = "unhealthy" ]; then
                compose logs --tail=120 "$service" || true
                echo "$service became unhealthy" >&2
                return 1
            fi
        fi
        if [ $(( $(date +%s) - started_at )) -ge "$timeout_seconds" ]; then
            compose logs --tail=120 "$service" || true
            echo "Timed out waiting for $service" >&2
            return 1
        fi
        sleep 3
    done
}

rollback_app_images() {
    if [ ! -f "$DEPLOY_STATE_DIR/previous.env" ]; then
        echo "No previous image record found; automatic app rollback skipped." >&2
        return 0
    fi

    # shellcheck disable=SC1090
    source "$DEPLOY_STATE_DIR/previous.env"
    : "${BACKEND_IMAGE:?previous BACKEND_IMAGE missing}"
    : "${FRONTEND_IMAGE:?previous FRONTEND_IMAGE missing}"

    echo "Rolling back application containers to previous images..."
    compose up -d backend celery_worker frontend nginx
    wait_for_service backend 180 || true
    wait_for_service frontend 90 || true
    wait_for_service nginx 90 || true
}

on_failure() {
    local status=$?
    if [ "$status" -ne 0 ]; then
        echo "Deployment failed. Attempting application image rollback." >&2
        rollback_app_images || true
        echo "If Alembic migrations already ran, review the database backup before assuming rollback is complete." >&2
    fi
    exit "$status"
}
trap on_failure EXIT

if [ -f "$DEPLOY_STATE_DIR/current.env" ]; then
    cp "$DEPLOY_STATE_DIR/current.env" "$DEPLOY_STATE_DIR/previous.env"
fi

cat > "$DEPLOY_STATE_DIR/next.env" <<EOF
BACKEND_IMAGE=$BACKEND_IMAGE
FRONTEND_IMAGE=$FRONTEND_IMAGE
DEPLOYED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
EOF

echo "Pulling immutable application images..."
compose pull backend celery_worker frontend

echo "Starting infrastructure services..."
compose up -d postgres redis chromadb neo4j
wait_for_service postgres 120
wait_for_service redis 90

if compose ps -q postgres >/dev/null 2>&1; then
    backup_file="$BACKUP_DIR/postgres-$(date -u +"%Y%m%dT%H%M%SZ").sql"
    echo "Creating PostgreSQL backup: $backup_file"
    compose exec -T postgres sh -c 'pg_dump -U "${POSTGRES_USER:-postgres}" "${POSTGRES_DB:-lancerai}"' > "$backup_file"
fi

echo "Running Alembic migrations..."
compose run --rm backend uv run --no-sync alembic upgrade head

echo "Starting application services..."
compose up -d backend celery_worker frontend nginx
wait_for_service backend 180
wait_for_service frontend 90
wait_for_service nginx 90

echo "Checking HTTP health endpoints..."
wait_for_http "$HEALTH_URL" 120
wait_for_http "$READY_URL" 120
wait_for_http "$FRONTEND_URL" 120

mv "$DEPLOY_STATE_DIR/next.env" "$DEPLOY_STATE_DIR/current.env"
trap - EXIT
echo "Deployment completed successfully."
