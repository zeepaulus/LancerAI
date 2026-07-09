"""Celery application instance with scheduled crawler jobs.

Run the worker:
    celery -A app.workers.celery_app worker --loglevel=info

Run beat:
    celery -A app.workers.celery_app beat --loglevel=info
"""

import os
from datetime import timedelta

from celery import Celery  # type: ignore[import-untyped]

celery_app = Celery(
    "lancerai",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1"),
    backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/2"),
    include=[
        "app.workers.crawler_worker",
        "app.workers.document_worker",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=True,
    beat_schedule={
        "crawl-topcv-it-jobs-every-12-hours": {
            "task": "app.workers.crawler_worker.crawl_job_listings",
            "schedule": timedelta(hours=12),
            "args": ("topcv", 3),
        },
    },
)
