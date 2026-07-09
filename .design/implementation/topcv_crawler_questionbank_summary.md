# TopCV Crawler and Question Bank Implementation Summary

## TopCV Source URL

Approved source URL:

`https://www.topcv.vn/tim-viec-lam-moi-nhat?company_field=1&type_keyword=1&sba=1&saturday_status=0`

The crawler treats:

- Scheme/host: `https://www.topcv.vn`
- Base path: `/tim-viec-lam-moi-nhat`
- Required query params:
  - `company_field=1`
  - `type_keyword=1`
  - `sba=1`
  - `saturday_status=0`

`build_topcv_search_url(page)` preserves those params and adds only `page=N`.

## URL Validation

`validate_topcv_source_url(url)` checks the exact scheme, host, path, and required query params using `urlparse` and `parse_qs`.

It intentionally does not treat page title text such as `[Update date]` as a URL parameter.

## Pagination Strategy

- Page 1..`max_pages`
- Default scheduled crawl uses `max_pages=3`
- The crawler preserves the approved query params and appends only a safe `page` parameter.

## Crawler Safety Rules

- Public listing/detail pages only.
- No login, CAPTCHA, paywall, or anti-bot bypass.
- Clear User-Agent: `LancerAIJobCrawler/1.0`.
- Low request rate with delay between page/detail requests.
- Request timeout and limited Celery retries.
- Detail pages that return 401/403/429 are skipped and reported through crawl status.
- If live crawling yields no IT jobs, fallback demo jobs are used and the status includes `fallback`.

## Storage and Deduplication

- Jobs are stored in `job_listings`.
- Deduplication key: `source_url`.
- Existing jobs are updated instead of duplicated.
- Embeddings are generated from title, company, location, salary, description, and requirements when the vector repository supports it.

## 12-Hour Schedule

Celery Beat schedule:

- Name: `crawl-topcv-it-jobs-every-12-hours`
- Task: `app.workers.crawler_worker.crawl_job_listings`
- Args: `("topcv", 3)`
- Interval: every 12 hours
- Timezone: `Asia/Ho_Chi_Minh`

## How To Run

Redis:

```powershell
redis-server
```

Celery worker:

```powershell
celery -A app.workers.celery_app worker --loglevel=info
```

Celery beat:

```powershell
celery -A app.workers.celery_app beat --loglevel=info
```

Manual task invocation:

```powershell
celery -A app.workers.celery_app call app.workers.crawler_worker.crawl_job_listings --args='["topcv", 1]'
```

## Job Matching Frontend Flow

1. User selects/has a structured CV.
2. Job Matching loads `GET /api/v1/jobs/listings?source=topcv`.
3. If backend returns no jobs or fails, a small clearly-labeled demo fallback is shown.
4. User searches/filters and selects a job.
5. Frontend converts the selected job to JD text.
6. Existing `POST /api/v1/jobs/matches` receives `cv_id` + `jd_text`.
7. Existing backend scoring returns match score, missing skills, and feedback.

The existing match API is preserved; no `job_id` request contract was required.

## Question Bank Dataset

- `frontend/src/data/questionBank.js`
- 60 realistic IT recruitment themes x 5 levels = 300 generated question objects.
- Vietnamese question/detail content.
- Backward-compatible aliases are kept:
  - `question`
  - `answerStructure`
  - `expectations`
  - `commonMistakes`
  - `sampleAnswer`

## Question Bank UI Changes

- Question Bank is now a library only, not an interview-session builder.
- Removed practice/session CTAs.
- Added compact horizontal filter bar.
- Detail is opened only after clicking a question card.
- Detail modal includes Vietnamese sections:
  - Câu hỏi
  - Mục đích nhà tuyển dụng muốn kiểm tra
  - Gợi ý cách trả lời
  - Cấu trúc trả lời đề xuất
  - Lỗi thường gặp
  - Gợi ý câu trả lời mẫu nếu phù hợp

## Remaining Limitations

- TopCV DOM can change; parser is best-effort and intentionally conservative.
- Live crawling may be blocked or rate-limited by TopCV; fallback is explicit and does not hide blocked crawl as success.
- Demo fallback jobs are intentionally small and should be replaced by real crawled rows in production.
- Frontend uses selected job as `jd_text` to keep `POST /jobs/matches` stable.
