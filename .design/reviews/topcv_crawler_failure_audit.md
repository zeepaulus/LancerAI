# TopCV Crawler Failure Audit

Date: 2026-07-09

## Scope

Reviewed:

- `app/workers/celery_app.py`
- `app/workers/crawler_worker.py`
- `app/workers/document_worker.py`
- `app/workers/__init__.py`
- `app/models/job_listing.py`
- `app/router/v1/job_matching_api.py`
- `app/schema/response.py`
- `pyproject.toml`

## Findings

1. Celery task registration was fragile.
   - Before the fix, `celery_app.py` defined a beat schedule for `app.workers.crawler_worker.crawl_job_listings`, but did not include or import the worker module.
   - A worker started with `celery -A app.workers.celery_app worker --loglevel=info` could miss the crawler task and report an unregistered task.
   - Fixed by adding `include=["app.workers.crawler_worker", "app.workers.document_worker"]` to the Celery app.

2. Celery beat schedule was present.
   - Schedule name: `crawl-topcv-it-jobs-every-12-hours`.
   - Interval: 12 hours.
   - Args: `("topcv", 3)`.
   - Timezone: `Asia/Ho_Chi_Minh`.

3. URL building mostly preserved the approved TopCV parameters.
   - Approved path: `/tim-viec-lam-moi-nhat`.
   - Required params: `company_field=1`, `type_keyword=1`, `sba=1`, `saturday_status=0`.
   - The fixed implementation adds only a safe `page` param and accepts reordered query params.

4. URL validation needed to be stricter about page values.
   - Fixed validation now requires HTTPS, `www.topcv.vn`, the approved path, all required params, and positive numeric `page` values if present.

5. Static HTTP is currently blocked from this environment.
   - Smoke command result: TopCV returned `403 Forbidden` for page 1.
   - This means live collection cannot be confirmed from the current environment.
   - The crawler now fails gracefully with a `blocked:403` status instead of pretending fallback data was crawled.

6. Listing extraction was too dependent on fragile selectors.
   - The previous crawler used class-name selectors such as `job-item`, `job-list`, and `job-card`.
   - The fixed crawler extracts all public anchors whose canonical path contains `/viec-lam/`, filters action buttons, removes fragments/query tracking, and deduplicates by canonical URL.

7. Detail parsing did not use the most stable source first.
   - The fixed parser checks `script[type="application/ld+json"]` for schema.org `JobPosting` and prefers it for title, company, location, salary, description, requirements, benefits, employment type, and experience signals.
   - CSS selectors and cleaned page text remain as fallbacks.

8. Vietnamese labels were brittle.
   - The previous implementation included mojibake-like strings in regex labels.
   - The fixed implementation normalizes text by removing accents before matching labels such as salary, location, requirements, and benefits.

9. Saving to DB could be coupled to embedding success.
   - The old flow initialized LLM/vector dependencies before job processing and embedded inside the main per-job try block.
   - If embeddings failed, the job could be counted as skipped and the crawl could lose usable listings.
   - The fixed flow saves/updates the job first, commits it, then attempts embedding best-effort. Embedding failures are logged and do not invalidate the saved listing.

10. Deduplication is application-level.
    - The model has no visible unique constraint on `source_url`.
    - The fixed worker queries by `source_url` and updates existing rows instead of inserting duplicates.

11. Frontend/backend listing integration exists.
    - `GET /api/v1/jobs/listings` already exists and returns active crawled listings.
    - The response now includes `updated_at`.
    - `POST /api/v1/jobs/matches` was not changed.

## Root Cause

The crawler failed because task discovery was incomplete and the scraping layer was too brittle for real-world TopCV pages. Static HTTP can also be blocked by TopCV, as observed with a `403 Forbidden` smoke result. The previous implementation had limited fallback behavior and could let embedding/vector dependency failures affect job collection.

## Current Behavior After Fix

- Celery worker imports crawler and document tasks through app `include`.
- Beat still schedules TopCV every 12 hours.
- URL builder and validator preserve the approved TopCV source params.
- Static HTTP is attempted first with safe headers, timeout, redirect handling, and low request rate.
- Playwright is optional and used only when static HTML is successful but contains no usable job links.
- TopCV `401`, `403`, or `429` stops crawling gracefully.
- Parser prefers JSON-LD `JobPosting`, then robust selectors/text fallback.
- Jobs are deduplicated by `source_url`.
- Jobs are saved even if embedding generation or vector storage fails.

## Validation Notes

- Offline URL/parser tests passed: `3 passed`.
- Celery default module import registered:
  - `app.workers.crawler_worker.crawl_job_listings`
  - `app.workers.document_worker.generate_document`
- Live smoke test was blocked by TopCV with `403 Forbidden`, so `links_found` and parsed live fields could not be collected in this environment.

## Remaining Limitations

- If TopCV blocks the server IP or requires browser challenges, the crawler will not bypass those protections.
- Playwright fallback requires installed Playwright browsers; if missing, the crawler logs a warning and returns the static result.
- `source_url` deduplication is not protected by a DB unique index yet.
- The crawler intentionally caps page/detail work to keep MVP/demo crawling polite.
