# `app/workers/` - Celery Background Workers

`app/workers/` contains Celery tasks for work that should not block the FastAPI request-response cycle.

## Architecture

```text
FastAPI / CLI / scheduler
  -> Celery task
  -> Redis broker
  -> Celery worker
  -> PostgreSQL / vector DB / document output
  -> Redis result backend
```

Configuration is read from `Settings`:

- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`

## Files

| File | Role |
|---|---|
| `celery_app.py` | Celery app factory/config |
| `crawler_worker.py` | TopCV job crawler and parser |
| `document_worker.py` | CV export task for PDF/DOCX |

## Run Worker

```bash
uv run celery -A app.workers.celery_app worker --loglevel=info -P threads -c 2
```

Production compose uses:

```bash
uv run --no-sync celery -A app.workers.celery_app worker --loglevel=info -P threads -c 2
```

## `crawler_worker.py`

Task:

```python
crawl_job_listings(source="topcv", max_pages=5)
```

Current behavior:

- Supports `topcv`.
- Builds approved TopCV listing URLs.
- Fetches static HTML with polite headers and delay.
- Falls back to Playwright only when static HTML does not expose job links.
- Parses listing cards and detail pages.
- Filters for IT/software-related jobs.
- Upserts `JobListing` by `source_url`.
- Stores job embeddings best-effort.

Result payload includes:

- `status`
- `crawl_status`
- `source`
- `approved_source_url`
- `pages_crawled`
- `jobs_seen`
- `jobs_added`
- `jobs_updated`
- `jobs_skipped`

Smoke utility:

```bash
uv run python -m app.workers.crawler_worker --smoke
```

## `document_worker.py`

Task:

```python
generate_document(cv_data, template="standard_ats", output_format="pdf")
```

Supported output:

- `pdf`: uses `CVTemplateRenderer.render_pdf`.
- `docx`: uses `python-docx` to build an ATS-friendly document.

The task returns base64 document bytes in `document_b64`.

## Follow-Ups

- Store generated documents in object storage or a local artifact directory instead of only returning base64.
- Add scheduled crawler runbook and monitoring.
- Add retry job for embeddings that failed during crawl.
