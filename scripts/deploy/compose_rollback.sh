#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-lancerai}"
ENV_FILE="${ENV_FILE:-.env}"
DEPLOY_STATE_DIR="${DEPLOY_STATE_DIR:-.deploy}"
HEALTH_URL="${HEALTH_URL:-http://localhost/health}"
READY_URL="${READY_URL:-http://localhost/ready}"

if [ ! -f "$DEPLOY_STATE_DIR/previous.env" ]; then
    echo "No previous deployment state exists at $DEPLOY_STATE_DIR/previous.env" >&2
    exit 1
fi

# shellcheck disable=SC1090
source "$DEPLOY_STATE_DIR/previous.env"
: "${BACKEND_IMAGE:?previous BACKEND_IMAGE missing}"
: "${FRONTEND_IMAGE:?previous FRONTEND_IMAGE missing}"

compose() {
    ENV_FILE="$ENV_FILE" \
    BACKEND_IMAGE="$BACKEND_IMAGE" \
    FRONTEND_IMAGE="$FRONTEND_IMAGE" \
    docker compose -f "$COMPOSE_FILE" --project-name "$COMPOSE_PROJECT_NAME" "$@"
}

compose pull backend celery_worker frontend
compose up -d backend celery_worker frontend nginx

curl -fsS "$HEALTH_URL" >/dev/null
curl -fsS "$READY_URL" >/dev/null

cp "$DEPLOY_STATE_DIR/previous.env" "$DEPLOY_STATE_DIR/current.env"
echo "Rollback completed to $BACKEND_IMAGE and $FRONTEND_IMAGE"
