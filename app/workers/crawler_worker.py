"""Crawler Worker: Scheduled JD collection from job boards.

Runs as Celery async task on Spot instances.
Scheduled via Prefect/Airflow for daily light-crawl.
"""

from typing import Any

from celery import shared_task  # type: ignore[import-untyped]

# Import the Celery app so @shared_task can find and register with it
from app.workers.celery_app import celery_app as _celery_app  # noqa: F401


@shared_task(bind=True, max_retries=3, default_retry_delay=60)  # type: ignore[untyped-decorator]
def crawl_job_listings(self: Any, source: str = "topcv", max_pages: int = 5) -> dict[str, Any]:
    """Crawl job listings from a specified source.

    Light-crawl strategy: Limited pages per run, daily schedule.
    Designed to be retry-safe for Spot instance interruptions.

    Sources: topcv, itviec, linkedin (future).

    TODO: Implement Scrapy/Playwright crawling logic.
    """
    return {"status": "not_implemented", "source": source, "pages_crawled": 0}
