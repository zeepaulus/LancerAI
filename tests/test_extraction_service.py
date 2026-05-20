"""Tests for app.service.extraction.service — ExtractionService pipelines and fallback paths."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.service.extraction.service import ExtractionService, MAX_FILE_SIZE


@pytest.fixture
def mock_dependencies() -> tuple[MagicMock, MagicMock, MagicMock, MagicMock]:
    ocr = MagicMock()
    llm = AsyncMock()
    vector_repo = AsyncMock()
    cv_repo = AsyncMock()
    return ocr, llm, vector_repo, cv_repo


@pytest.fixture
def sample_extracted_json() -> str:
    return json.dumps({
        "personal_info": {
            "name": "Nguyễn Văn A",
            "email": "nguyenvana@email.com",
            "phone": "0901234567",
            "linkedin": "linkedin.com/in/nguyenvana",
            "location": "Ho Chi Minh City"
        },
        "education": [
            {
                "school": "HCMC University of Technology",
                "degree": "Bachelor",
                "major": "Computer Science",
                "gpa": "3.5",
                "period": "2018 - 2022"
            }
        ],
        "experience": [
            {
                "company": "TechCorp Vietnam",
                "title": "Backend Engineer",
                "period": "2022 - Present",
                "descriptions": ["Designed RESTful APIs"],
                "key_impacts": ["Reduced latency"],
                "tech_stack": ["Python", "FastAPI"]
            }
        ],
        "projects": [
            {
                "name": "CV Optimizer",
                "role": "Lead Developer",
                "tech_stack": ["LangGraph"],
                "description": "Multi-agent CV analysis",
                "key_impacts": ["Processed 500+ CVs"],
                "potential_roast_points": ["No metrics"]
            }
        ],
        "skills_matrix": {
            "languages": ["Python"],
            "frameworks": ["FastAPI"],
            "tools": ["Docker"],
            "soft_skills": ["Communication"]
        },
        "certifications": ["AWS Solutions Architect"],
        "languages": ["Vietnamese", "English"]
    })


class TestExtractionServiceValidation:
    """Test validation constraints on input files."""

    @pytest.mark.asyncio
    async def test_extract_from_image_oversized_raises(self, mock_dependencies: tuple) -> None:
        ocr, llm, vector_repo, cv_repo = mock_dependencies
        service = ExtractionService(ocr, llm, vector_repo, cv_repo)
        
        oversized_bytes = b"0" * (MAX_FILE_SIZE + 1)
        with pytest.raises(ValueError, match="File size exceeds the limit"):
            await service.extract_from_image(oversized_bytes, "cv.png", "user_123", AsyncMock())

    @pytest.mark.asyncio
    async def test_extract_from_pdf_oversized_raises(self, mock_dependencies: tuple) -> None:
        ocr, llm, vector_repo, cv_repo = mock_dependencies
        service = ExtractionService(ocr, llm, vector_repo, cv_repo)
        
        oversized_bytes = b"0" * (MAX_FILE_SIZE + 1)
        with pytest.raises(ValueError, match="File size exceeds the limit"):
            await service.extract_from_pdf(oversized_bytes, "cv.pdf", "user_123", AsyncMock())


class TestExtractionServiceImagePipeline:
    """Test image extraction pipeline."""

    @pytest.mark.asyncio
    async def test_extract_from_image_success(
        self,
        mock_dependencies: tuple,
        sample_extracted_json: str,
    ) -> None:
        ocr, llm, vector_repo, cv_repo = mock_dependencies
        service = ExtractionService(ocr, llm, vector_repo, cv_repo)

        # Mock OCR output
        ocr.extract_text_grouped.return_value = "Extracted Text Content"
        # Mock LLM output
        llm.generate.return_value = sample_extracted_json

        # Exec pipeline
        response = await service.extract_from_image(
            file_bytes=b"dummy_image_bytes",
            filename="cv.png",
            user_id="user_123",
            session=AsyncMock(),
        )

        # Asserts
        assert response.cv_id is not None
        assert response.personal_info.name == "Nguyễn Văn A"
        assert len(response.education) == 1
        assert response.experience[0].company == "TechCorp Vietnam"
        assert response.skills_matrix.languages == ["Python"]
        
        # Verify db and vector repositories were called
        cv_repo.create.assert_called_once()
        vector_repo.store_embedding.assert_called_once()


class TestExtractionServicePdfPipeline:
    """Test PDF extraction pipeline, including density check fallback paths."""

    @pytest.mark.asyncio
    @patch("fitz.open")
    async def test_extract_from_pdf_high_density_direct(
        self,
        mock_fitz_open: MagicMock,
        mock_dependencies: tuple,
        sample_extracted_json: str,
    ) -> None:
        ocr, llm, vector_repo, cv_repo = mock_dependencies
        service = ExtractionService(ocr, llm, vector_repo, cv_repo)

        # Mock PDF page with high density text
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "This is a very long text that represents a CV with high text density. " * 5
        mock_doc.load_page.return_value = mock_page
        mock_doc.__len__.return_value = 1
        mock_fitz_open.return_value = mock_doc

        # Mock LLM output
        llm.generate.return_value = sample_extracted_json

        # Exec pipeline
        response = await service.extract_from_pdf(
            file_bytes=b"dummy_pdf_bytes",
            filename="cv.pdf",
            user_id="user_123",
            session=AsyncMock(),
        )

        # Asserts
        assert response.personal_info.name == "Nguyễn Văn A"
        ocr.extract_text_grouped.assert_not_called()  # High density direct path, no OCR
        cv_repo.create.assert_called_once()
        vector_repo.store_embedding.assert_called_once()

    @pytest.mark.asyncio
    @patch("fitz.open")
    async def test_extract_from_pdf_low_density_ocr_fallback(
        self,
        mock_fitz_open: MagicMock,
        mock_dependencies: tuple,
        sample_extracted_json: str,
    ) -> None:
        ocr, llm, vector_repo, cv_repo = mock_dependencies
        service = ExtractionService(ocr, llm, vector_repo, cv_repo)

        # Mock PDF page with low density text (scanned PDF)
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "short"  # < 50 chars, triggers fallback
        
        mock_pixmap = MagicMock()
        mock_pixmap.tobytes.return_value = b"mocked_png_bytes"
        mock_page.get_pixmap.return_value = mock_pixmap
        
        mock_doc.load_page.return_value = mock_page
        mock_doc.__len__.return_value = 1
        mock_fitz_open.return_value = mock_doc

        # Mock OCR output and LLM output
        ocr.extract_text_grouped.return_value = "OCR Transcribed Text Content"
        llm.generate.return_value = sample_extracted_json

        # Exec pipeline
        response = await service.extract_from_pdf(
            file_bytes=b"dummy_pdf_bytes",
            filename="cv.pdf",
            user_id="user_123",
            session=AsyncMock(),
        )

        # Asserts
        assert response.personal_info.name == "Nguyễn Văn A"
        ocr.extract_text_grouped.assert_called_once_with(b"mocked_png_bytes")  # Fallback to OCR
        cv_repo.create.assert_called_once()
        vector_repo.store_embedding.assert_called_once()
