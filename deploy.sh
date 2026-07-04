#!/usr/bin/env bash
# =============================================================================
# deploy.sh — Deploy LancerAI lên DigitalOcean Droplet
# Chạy script này TRÊN DROPLET (sau khi SSH vào):
#   bash deploy.sh
# Hoặc từ máy local (thay YOUR_DROPLET_IP):
#   ssh root@YOUR_DROPLET_IP 'bash -s' < deploy.sh
# =============================================================================
set -euo pipefail

REPO_URL="https://github.com/zeepaulus/LancerAI.git"
APP_DIR="/opt/lancerai"
BRANCH="Bao-version"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log()  { echo -e "${GREEN}[+]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
err()  { echo -e "${RED}[x]${NC} $*" >&2; exit 1; }

# ── 1. Cài Docker nếu chưa có ────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
    log "Cài Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable --now docker
    log "Docker đã cài xong: $(docker --version)"
else
    log "Docker đã có: $(docker --version)"
fi

# ── 2. Clone / pull code ─────────────────────────────────────────────────────
if [ -d "$APP_DIR/.git" ]; then
    log "Cập nhật code từ GitHub..."
    cd "$APP_DIR"
    git fetch origin
    git checkout "$BRANCH"
    git pull origin "$BRANCH"
else
    log "Clone repo từ GitHub..."
    git clone --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
fi

# ── 3. Kiểm tra .env ─────────────────────────────────────────────────────────
if [ ! -f "$APP_DIR/.env" ]; then
    warn ".env chưa tồn tại. Tạo từ template..."
    cp "$APP_DIR/.env.production.example" "$APP_DIR/.env"
    err "Hãy điền đầy đủ thông tin trong $APP_DIR/.env rồi chạy lại script!"
fi

# Cảnh báo nếu còn giá trị placeholder
if grep -q "REPLACE_" "$APP_DIR/.env"; then
    err ".env vẫn còn giá trị 'REPLACE_*'. Hãy điền thông tin thật trước khi deploy!"
fi

# ── 4. Tạo thư mục nginx certs (cho HTTPS sau này) ───────────────────────────
mkdir -p "$APP_DIR/nginx/certs"

# ── 5. Build và chạy Docker Compose production ───────────────────────────────
log "Build Docker images..."
cd "$APP_DIR"
docker compose -f docker-compose.prod.yml build --no-cache

log "Dừng containers cũ (nếu có)..."
docker compose -f docker-compose.prod.yml down --remove-orphans || true

log "Khởi động toàn bộ stack..."
docker compose -f docker-compose.prod.yml up -d

# ── 6. Chạy database migration ───────────────────────────────────────────────
log "Chờ PostgreSQL sẵn sàng (15s)..."
sleep 15

log "Chạy Alembic migration..."
docker compose -f docker-compose.prod.yml exec -T backend \
    uv run --no-sync alembic upgrade head

# ── 7. Kiểm tra health ────────────────────────────────────────────────────────
log "Kiểm tra health endpoint..."
sleep 5
if curl -sf http://localhost/health > /dev/null; then
    log "✅ Backend đang chạy tại http://localhost/health"
else
    warn "⚠️  Health check thất bại — xem logs: docker compose -f docker-compose.prod.yml logs backend"
fi

# ── 8. Tóm tắt ───────────────────────────────────────────────────────────────
DROPLET_IP=$(curl -sf http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address 2>/dev/null || echo "YOUR_DROPLET_IP")
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  🚀 LancerAI deployed thành công!${NC}"
echo -e "${GREEN}============================================${NC}"
echo -e "  Frontend:   http://$DROPLET_IP"
echo -e "  API Docs:   http://$DROPLET_IP/docs"
echo -e "  Health:     http://$DROPLET_IP/health"
echo ""
echo -e "  Xem logs:  docker compose -f $APP_DIR/docker-compose.prod.yml logs -f"
echo -e "  Dừng:      docker compose -f $APP_DIR/docker-compose.prod.yml down"
echo -e "${GREEN}============================================${NC}"
