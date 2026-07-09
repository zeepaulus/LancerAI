# TopCV Crawler Runbook

Date: 2026-07-09

## What It Does

The crawler collects public IT job postings from TopCV for LancerAI job matching.

It does not bypass CAPTCHA, login, paywalls, browser challenges, or anti-bot protections. If TopCV returns `401`, `403`, or `429`, the crawler stops and reports a blocked status.

## Redis

Start Redis before Celery worker and beat.

Docker example:

```bash
docker compose up -d redis
```

Local Redis example:

```bash
redis-server
```

## Celery Worker

```bash
celery -A app.workers.celery_app worker --loglevel=info
```

Expected registered tasks include:

```text
app.workers.crawler_worker.crawl_job_listings
app.workers.document_worker.generate_document
```

Python verification:

```bash
python - <<'PY'
from app.workers.celery_app import celery_app
celery_app.loader.import_default_modules()
print([name for name in celery_app.tasks if name.startswith("app.workers")])
PY
```

PowerShell verification:

```powershell
@'
from app.workers.celery_app import celery_app
celery_app.loader.import_default_modules()
print([name for name in celery_app.tasks if name.startswith("app.workers")])
'@ | .\.venv\Scripts\python.exe -
```

## Celery Beat

```bash
celery -A app.workers.celery_app beat --loglevel=info
```

Expected schedule:

```text
crawl-topcv-it-jobs-every-12-hours
task: app.workers.crawler_worker.crawl_job_listings
schedule: every 12 hours
args: ("topcv", 3)
timezone: Asia/Ho_Chi_Minh
```

## Manual Crawl

From a Python shell:

```bash
python - <<'PY'
from app.workers.crawler_worker import crawl_job_listings
result = crawl_job_listings.delay("topcv", 1)
print(result.id)
PY
```

PowerShell:

```powershell
@'
from app.workers.crawler_worker import crawl_job_listings
result = crawl_job_listings.delay("topcv", 1)
print(result.id)
'@ | .\.venv\Scripts\python.exe -
```

Synchronous local check without Celery broker:

```powershell
@'
from app.workers.crawler_worker import _crawl_source_sync
jobs, status = _crawl_source_sync("topcv", 1)
print(status)
print(len(jobs))
print(jobs[0] if jobs else None)
'@ | .\.venv\Scripts\python.exe -
```

## Smoke Test

The smoke test validates the URL, fetches only page 1, extracts links, fetches only one detail page, parses fields, and does not save to DB.

```bash
python -m app.workers.crawler_worker --smoke
```

PowerShell with the project venv:

```powershell
.\.venv\Scripts\python.exe -m app.workers.crawler_worker --smoke
```

Expected successful output shape:

```text
approved_url_valid=True
page_1_url=https://www.topcv.vn/tim-viec-lam-moi-nhat?company_field=1&type_keyword=1&sba=1&saturday_status=0&page=1
page_1_url_valid=True
listing_status_code=200
links_found=<number>
detail_url=<topcv job url>
detail_status_code=200
parsed_job={"title": "...", "company": "...", "location": "..."}
```

If TopCV blocks the request:

```text
listing_blocked=TopCV blocked listing request (403)
```

This is expected behavior for a protected environment. Do not bypass it.

## Common Errors

### Unregistered task

Symptom:

```text
Received unregistered task of type 'app.workers.crawler_worker.crawl_job_listings'
```

Fix:

- Start worker with `celery -A app.workers.celery_app worker --loglevel=info`.
- Confirm `celery_app.py` includes `app.workers.crawler_worker`.
- Restart worker after code changes.

### Redis not running

Symptom:

```text
Error 10061 connecting to localhost:6379
```

Fix:

- Start Redis.
- Confirm `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND`.

### TopCV 403/429

Symptom:

```text
blocked: TopCV blocked listing request (403)
```

Fix:

- Do not bypass anti-bot protections.
- Reduce max pages.
- Try again later from an allowed environment.
- Use manual import or dev fallback data clearly labeled as fallback if live crawling is unavailable.

### No links found

Symptom:

```text
links_found=0
```

Fix:

- Inspect listing HTML manually.
- Confirm TopCV did not return a challenge page.
- Confirm Playwright is installed and browsers are available if rendered HTML is required.

### Parser returns empty fields

Fix:

- Check whether JSON-LD `JobPosting` exists.
- Inspect heading labels in the page.
- Add a selector/text fallback only for public page content.

### DB connection error

Fix:

- Confirm backend database env vars.
- Run migrations.
- Confirm `job_listings` table exists.

### Embedding error

Behavior:

- Job remains saved.
- Embedding failure is logged as a warning.

Fix:

- Confirm LLM connector config.
- Confirm vector repository config.
- Retry embedding later if needed.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_topcv_crawler.py -q
```

```powershell
@'
from app.workers.celery_app import celery_app
celery_app.loader.import_default_modules()
print([name for name in celery_app.tasks if name.startswith("app.workers")])
'@ | .\.venv\Scripts\python.exe -
```

```powershell
.\.venv\Scripts\python.exe -m app.workers.crawler_worker --smoke
```
