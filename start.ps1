#!/usr/bin/env pwsh
<#
.SYNOPSIS
  LancerAI — Khởi động server sau khi Docker compose đã chạy

.DESCRIPTION
  Script tự động:
  1. Kiểm tra Docker containers đang healthy
  2. Chạy Alembic migration để tạo/cập nhật schema DB
  3. Khởi động uvicorn development server
  4. (Tuỳ chọn) Khởi động Celery worker trong terminal riêng
#>

Write-Host "`n🚀 LancerAI — Startup Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# ─── 1. Kiểm tra Docker containers ───────────────────────────────────────────
Write-Host "`n[1/4] Kiểm tra Docker containers..." -ForegroundColor Yellow
$containers = docker ps --format "{{.Names}} {{.Status}}" 2>&1
Write-Host $containers

$required = @("lancerai-postgres", "lancerai-redis", "lancerai-chromadb", "lancerai-neo4j")
$allUp = $true
foreach ($c in $required) {
    if ($containers -notmatch $c) {
        Write-Host "  ❌ Container $c chưa chạy — hãy chạy 'docker compose up -d' trước" -ForegroundColor Red
        $allUp = $false
    }
}

if (-not $allUp) {
    Write-Host "`nĐang khởi động containers..." -ForegroundColor Yellow
    docker compose up -d
    Write-Host "Chờ 10s cho services ổn định..."
    Start-Sleep 10
}

# ─── 2. Alembic Migration ────────────────────────────────────────────────────
Write-Host "`n[2/4] Chạy Alembic migration (tạo/cập nhật DB schema)..." -ForegroundColor Yellow
.venv\Scripts\python -m alembic -c migration\alembic.ini upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ Migration thất bại! Kiểm tra DATABASE_URL trong .env" -ForegroundColor Red
    Write-Host "     Đảm bảo PostgreSQL đang chạy và database 'lancerai' tồn tại"
    exit 1
}
Write-Host "  ✅ Migration hoàn thành" -ForegroundColor Green

# ─── 3. Kiểm tra kết nối các services ────────────────────────────────────────
Write-Host "`n[3/4] Kiểm tra kết nối services..." -ForegroundColor Yellow

# PostgreSQL
$pgCheck = .venv\Scripts\python -c "
import asyncio, asyncpg, os
from dotenv import load_dotenv
load_dotenv()
async def check():
    try:
        conn = await asyncpg.connect(os.environ['DATABASE_URL'].replace('+asyncpg',''))
        await conn.close()
        print('  ✅ PostgreSQL: OK')
    except Exception as e:
        print(f'  ❌ PostgreSQL: {e}')
asyncio.run(check())
" 2>&1
Write-Host $pgCheck

# ChromaDB
try {
    $chromaResp = Invoke-WebRequest -Uri "http://localhost:8001/api/v1/heartbeat" -TimeoutSec 3 -ErrorAction Stop
    Write-Host "  ✅ ChromaDB: OK" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  ChromaDB: Chưa sẵn sàng (chờ thêm hoặc kiểm tra port 8001)" -ForegroundColor Yellow
}

# Neo4j
try {
    $neo4jResp = Invoke-WebRequest -Uri "http://localhost:7474" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  ✅ Neo4j: OK (Browser: http://localhost:7474)" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  Neo4j: Chưa sẵn sàng (Neo4j thường mất 30-60s để khởi động)" -ForegroundColor Yellow
}

# ─── 4. Khởi động uvicorn ────────────────────────────────────────────────────
Write-Host "`n[4/4] Khởi động FastAPI server..." -ForegroundColor Yellow
Write-Host "  📡 API:  http://localhost:8000/api/v1"
Write-Host "  📖 Docs: http://localhost:8000/docs"
Write-Host "  🔄 Để chạy Celery worker, mở terminal mới và chạy:"
Write-Host "     .venv\Scripts\celery -A app.workers.celery_app worker --loglevel=info -P threads" -ForegroundColor Gray
Write-Host ""
Write-Host "  [Ctrl+C để dừng server]" -ForegroundColor DarkGray
Write-Host ""

.venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
