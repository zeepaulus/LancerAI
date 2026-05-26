import base64
from unittest.mock import AsyncMock, MagicMock, patch

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


@patch("app.workers.crawler_worker._crawl_source_sync")
@patch("app.core.database._get_session_factory")
@patch("app.core.providers.connectors.get_vector_repository")
@patch("app.core.providers.connectors.get_llm_connector")
def test_crawler_worker_flow(
    mock_get_llm: MagicMock,
    mock_get_vector_repo: MagicMock,
    mock_get_session_factory: MagicMock,
    mock_crawl_source: MagicMock,
) -> None:
    # Arrange: Mock crawler return values
    mock_crawl_source.return_value = [
        {
            "source": "topcv",
            "source_url": "https://example.com/job1",
            "title": "Python Dev",
            "company": "Company A",
            "location": "Hà Nội",
            "salary_range": "Negotiable",
            "description": "Python job description text",
            "requirements": {"skills": ["Python"]},
        }
    ]

    # Arrange: Mock session and DB queries
    mock_session = AsyncMock()
    mock_session.add = MagicMock()  # .add() is synchronous in SQLAlchemy
    mock_session_maker = MagicMock()
    mock_session_maker.return_value.__aenter__.return_value = mock_session
    mock_get_session_factory.return_value = mock_session_maker

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None  # No existing job found
    mock_session.execute.return_value = mock_result

    # Arrange: Mock LLM and Vector repo
    mock_llm = MagicMock()
    mock_llm.embed = AsyncMock(return_value=[0.1, 0.2, 0.3])
    mock_get_llm.return_value = mock_llm

    mock_vector = MagicMock()
    mock_vector.store_embedding = AsyncMock()
    mock_get_vector_repo.return_value = mock_vector

    # Act
    res = crawl_job_listings(source="topcv", max_pages=1)

    # Assert
    assert res["status"] == "success"
    assert res["source"] == "topcv"
    assert res["jobs_added"] == 1
    assert res["jobs_skipped"] == 0

    # Verify sessions and methods called
    mock_session.add.assert_called_once()
    mock_llm.embed.assert_called_once()
    mock_vector.store_embedding.assert_called_once()
    mock_session.commit.assert_called_once()


def test_generate_document_pdf() -> None:
    cv_data = {"personal_info": {"name": "John Doe"}}
    with patch("app.workers.document_worker.CVTemplateRenderer") as mock_renderer_cls:
        mock_renderer = MagicMock()
        mock_renderer.render_pdf = AsyncMock(return_value=b"pdf_mock_bytes")
        mock_renderer_cls.return_value = mock_renderer

        res = generate_document(cv_data, template="standard_ats", output_format="pdf")

        assert res["status"] == "success"
        assert res["output_format"] == "pdf"
        assert res["document_b64"] is not None
        assert base64.b64decode(res["document_b64"]) == b"pdf_mock_bytes"


def test_generate_document_docx() -> None:
    cv_data = {
        "personal_info": {"name": "John Doe", "email": "john@example.com"},
        "education": [{"school": "University", "degree": "Bachelor", "major": "CS", "period": "2020-2024"}],
        "experience": [
            {
                "company": "Company",
                "title": "Developer",
                "period": "2024-Present",
                "key_impacts": ["Impact 1"],
            }
        ],
        "projects": [{"name": "Project", "role": "Lead", "tech_stack": ["Python"], "description": "Desc"}],
        "skills_matrix": {"languages": ["Python"]},
    }

    res = generate_document(cv_data, template="standard_ats", output_format="docx")

    assert res["status"] == "success"
    assert res["output_format"] == "docx"
    assert res["document_b64"] is not None

    decoded = base64.b64decode(res["document_b64"])
    assert decoded.startswith(b"PK")  # Standard ZIP signature for DOCX
