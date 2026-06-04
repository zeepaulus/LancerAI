#!/usr/bin/env pwsh
<#
.SYNOPSIS
  LancerAI - Khoi dong server sau khi Docker compose da chay
.DESCRIPTION
  Script tu dong:
  1. Kiem tra Docker containers dang healthy
  2. Chay Alembic migration de tao/cap nhat schema DB
  3. Khoi dong uvicorn development server
  4. (Tuy chon) Khoi dong Celery worker trong terminal rieng
#>

Write-Host "`n* LancerAI - Startup Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# --- 1. Kiem tra Docker containers ---
Write-Host "`n[1/4] Kiem tra Docker containers..." -ForegroundColor Yellow
$containers = docker ps --format "{{.Names}} {{.Status}}" 2>&1
Write-Host $containers

$required = @("lancerai-postgres", "lancerai-redis", "lancerai-chromadb", "lancerai-neo4j")
$allUp = $true
foreach ($c in $required) {
    if ($containers -notmatch $c) {
        Write-Host "  * Container $c chua chay - hay chay 'docker compose up -d' truoc" -ForegroundColor Red
        $allUp = $false
    }
}

if (-not $allUp) {
    Write-Host "`nDang khoi dong containers..." -ForegroundColor Yellow
    docker compose up -d
    Write-Host "Cho 10s cho services on dinh..."
    Start-Sleep 10
}

# --- 2. Alembic Migration ---
Write-Host "`n[2/4] Chay Alembic migration (tao/cap nhat DB schema)..." -ForegroundColor Yellow
.venv\Scripts\python -m alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "  * Migration that bai! Kiem tra DATABASE_URL trong .env" -ForegroundColor Red
    Write-Host "     Dam bao PostgreSQL dang chay va database 'lancerai' ton tai"
    exit 1
}
Write-Host "  * Migration hoan thanh" -ForegroundColor Green

# --- 3. Kiem tra ket noi cac services ---
Write-Host "`n[3/4] Kiem tra ket noi services..." -ForegroundColor Yellow

# PostgreSQL
$pgCheck = .venv\Scripts\python -c @'
import asyncio, asyncpg, os
from dotenv import load_dotenv
load_dotenv()
async def check():
    try:
        conn = await asyncpg.connect(os.environ['DATABASE_URL'].replace('+asyncpg',''))
        await conn.close()
        print('  * PostgreSQL: OK')
    except Exception as e:
        print(f'  * PostgreSQL: {e}')
asyncio.run(check())
'@ 2>&1
Write-Host $pgCheck

# ChromaDB
try {
    $chromaResp = Invoke-WebRequest -Uri "http://localhost:8001/api/v1/heartbeat" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    Write-Host "  * ChromaDB: OK" -ForegroundColor Green
} catch {
    Write-Host "  * ChromaDB: Chua san sang (cho them hoac kiem tra port 8001)" -ForegroundColor Yellow
}

# Neo4j
try {
    $neo4jResp = Invoke-WebRequest -Uri "http://localhost:7474" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  * Neo4j: OK (Browser: http://localhost:7474)" -ForegroundColor Green
} catch {
    Write-Host "  * Neo4j: Chua san sang (Neo4j thuong mat 30-60s de khoi dong)" -ForegroundColor Yellow
}

# --- 4. Khoi dong uvicorn ---
Write-Host "`n[4/4] Khoi dong FastAPI server..." -ForegroundColor Yellow
Write-Host "  * API:  http://localhost:8000/api/v1"
Write-Host "  * Docs: http://localhost:8000/docs"
Write-Host "  * De chay Celery worker, mo terminal moi va chay:"
Write-Host "     .venv\Scripts\celery -A app.workers.celery_app worker --loglevel=info -P threads" -ForegroundColor Gray
Write-Host ""
Write-Host "  [Ctrl+C de dung server]" -ForegroundColor DarkGray
Write-Host ""

.venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
