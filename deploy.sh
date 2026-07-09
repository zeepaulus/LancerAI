#!/usr/bin/env bash
# Deploy LancerAI on a Docker host.
#
# Defaults target the Bao-version branch:
#   bash deploy.sh
#
# Override when needed:
#   BRANCH=main APP_DIR=/opt/lancerai bash deploy.sh

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/zeepaulus/LancerAI.git}"
APP_DIR="${APP_DIR:-/opt/lancerai}"
BRANCH="${BRANCH:-Bao-version}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-lancerai}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[+]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
err() { echo -e "${RED}[x]${NC} $*" >&2; exit 1; }

require_cmd() {
    command -v "$1" >/dev/null 2>&1 || err "Missing required command: $1"
}

compose() {
    docker compose -f "$COMPOSE_FILE" --project-name "$COMPOSE_PROJECT_NAME" "$@"
}

wait_for_container_healthy() {
    local container_name="$1"
    local timeout_seconds="${2:-120}"
    local started_at
    started_at="$(date +%s)"

    while true; do
        local status
        status="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$container_name" 2>/dev/null || true)"
        if [ "$status" = "healthy" ] || [ "$status" = "running" ]; then
            log "$container_name is $status"
            return 0
        fi
        if [ "$status" = "unhealthy" ]; then
            docker logs --tail=80 "$container_name" || true
            err "$container_name became unhealthy"
        fi
        if [ $(( $(date +%s) - started_at )) -ge "$timeout_seconds" ]; then
            docker logs --tail=80 "$container_name" || true
            err "Timed out waiting for $container_name to become healthy"
        fi
        sleep 3
    done
}

wait_for_http() {
    local url="$1"
    local timeout_seconds="${2:-90}"
    local started_at
    started_at="$(date +%s)"

    until curl -fsS "$url" >/dev/null; do
        if [ $(( $(date +%s) - started_at )) -ge "$timeout_seconds" ]; then
            err "Timed out waiting for $url"
        fi
        sleep 3
    done
    log "$url is reachable"
}

require_cmd git
require_cmd curl

if ! command -v docker >/dev/null 2>&1; then
    log "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable --now docker
fi

docker compose version >/dev/null 2>&1 || err "Docker Compose v2 plugin is required"

if [ -d "$APP_DIR/.git" ]; then
    log "Updating $APP_DIR from origin/$BRANCH..."
    cd "$APP_DIR"
    git fetch origin "$BRANCH"
    if [ "$(git rev-parse --abbrev-ref HEAD)" != "$BRANCH" ]; then
        git checkout "$BRANCH"
    fi
    git pull --ff-only origin "$BRANCH"
else
    log "Cloning $REPO_URL ($BRANCH) to $APP_DIR..."
    git clone --branch "$BRANCH" --single-branch "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
fi

if [ ! -f "$APP_DIR/.env" ]; then
    warn ".env not found. Creating it from .env.production.example."
    cp "$APP_DIR/.env.production.example" "$APP_DIR/.env"
    err "Edit $APP_DIR/.env with real secrets/domains, then run deploy.sh again."
fi

if grep -Eq 'REPLACE_|YOUR_DROPLET_IP|changeme' "$APP_DIR/.env"; then
    err ".env still contains placeholder values. Replace them before deploying."
fi

mkdir -p "$APP_DIR/nginx/certs"

log "Building production images..."
compose build --pull backend frontend

log "Stopping old containers..."
compose down --remove-orphans || true

log "Starting infrastructure services..."
compose up -d postgres redis chromadb neo4j

log "Starting backend..."
compose up -d backend
wait_for_container_healthy lancerai-backend 180

log "Running database migrations..."
compose exec -T backend uv run --no-sync alembic upgrade head

log "Starting worker, frontend, and nginx..."
compose up -d celery_worker frontend nginx
wait_for_container_healthy lancerai-frontend 90
wait_for_container_healthy lancerai-nginx 90

log "Checking public health endpoint..."
wait_for_http "http://localhost/health" 90

DROPLET_IP="$(curl -sf http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address 2>/dev/null || echo "YOUR_SERVER_IP")"

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  LancerAI deployment completed${NC}"
echo -e "${GREEN}============================================${NC}"
echo -e "  Branch:     $BRANCH"
echo -e "  Frontend:   http://$DROPLET_IP"
echo -e "  API Docs:   http://$DROPLET_IP/docs"
echo -e "  Health:     http://$DROPLET_IP/health"
echo ""
echo -e "  Logs:       docker compose -f $APP_DIR/$COMPOSE_FILE logs -f"
echo -e "  Stop:       docker compose -f $APP_DIR/$COMPOSE_FILE down"
echo -e "${GREEN}============================================${NC}"
