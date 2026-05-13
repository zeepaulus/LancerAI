
from app.workers.celery_app import celery_app
from app.workers.crawler_worker import crawl_job_listings
from app.workers.document_worker import generate_document


def test_celery_app_configured() -> None:
    assert celery_app is not None
    assert celery_app.conf.broker_url is not None

def test_crawler_worker_task_registered() -> None:
    assert crawl_job_listings.name == "app.workers.crawler_worker.crawl_job_listings"

def test_document_worker_task_registered() -> None:
    assert generate_document.name == "app.workers.document_worker.generate_document"
