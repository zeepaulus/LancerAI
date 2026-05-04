# `app/workers/` — Celery Background Task Workers

Package chứa các **Celery shared tasks** xử lý công việc nặng/chậm không phù hợp để chạy trong request-response cycle của FastAPI. Tasks được broker qua **Redis** và có thể schedule bằng Celery Beat hoặc Prefect/Airflow.

## Architecture

```
FastAPI Router
  └─→ .delay() / .apply_async()
      └─→ Redis (broker, DB 1)
          └─→ Celery Worker process
              └─→ Result → Redis (backend, DB 2)
```

Workers chạy trên process riêng biệt (hoặc Spot instances), hoàn toàn độc lập với API server.

## Files

### `crawler_worker.py` — JD Collection Task

```python
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def crawl_job_listings(self, source="topcv", max_pages=5) -> dict
```

**Purpose**: Thu thập Job Descriptions từ các job boards về lưu vào `job_listings` table.

**Design decisions:**
- `max_retries=3`, `default_retry_delay=60s` — retry-safe cho Spot instance interruptions.
- Light-crawl strategy: giới hạn `max_pages` mỗi run, schedule daily.
- `bind=True` — `self` cho phép gọi `self.retry()` trong exception handler.

**Target sources:**
- `topcv` — TopCV.vn
- `itviec` — ITviec.com
- `linkedin` — LinkedIn (future)

**Technology (planned):** Scrapy hoặc Playwright cho dynamic pages.

---

### `document_worker.py` — CV Export Task

```python
@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def generate_document(self, cv_data, template="standard_ats", output_format="pdf") -> dict
```

**Purpose**: Render structured CV data thành file PDF hoặc DOCX với ATS-friendly templates.

**Templates:**
- `standard_ats` — Clean, ATS-parseable format
- `modern_tech` — Tech-focused visual layout
- `management` — Executive/management style

**Output formats:**
- `pdf` — via **WeasyPrint** (HTML → PDF)
- `docx` — via **python-docx**

**Design**: Chạy async để tránh block API response khi render PDF. Kết quả được lưu vào object storage (S3/MinIO) và trả về signed URL.

## Technology

| Component | Library |
|---|---|
| Task queue | **Celery** (`shared_task`, `bind=True`) |
| Message broker | **Redis** (DB 1) |
| Result backend | **Redis** (DB 2) |
| Web scraping | Scrapy / Playwright (planned) |
| PDF rendering | **WeasyPrint** (planned) |
| DOCX generation | **python-docx** (planned) |
| Scheduling | Celery Beat / Prefect / Airflow |

## Configuration

Broker và backend URLs được cấu hình trong `core/settings.py`:

```python
celery_broker_url  = "redis://localhost:6379/1"
celery_result_backend = "redis://localhost:6379/2"
```
