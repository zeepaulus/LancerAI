"""Celery application instance — lazy settings loading.

Run the worker:
    celery -A app.workers.celery_app worker --loglevel=info

TODO:
    - Add periodic beat schedule for crawl_job_listings (daily).
    - Add dead-letter queue for failed tasks.
"""

import os

from celery import Celery  # type: ignore[import-untyped]

celery_app = Celery(
    "lancerai",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1"),
    backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/2"),
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=True,
)
