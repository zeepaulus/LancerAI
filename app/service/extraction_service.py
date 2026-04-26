"""Module 1 — CV extraction.

Owns the ingest pipeline:
    File upload  ->  text/OCR extraction  ->  LLM entity parsing  ->  persist.

All persistence goes through ``cv_repository``; raw text + structured JSON are
stored on ``CVRecord``. Vector embeddings are pushed to ``vector_repository``
so later modules (matching, retrieval agent) can run RAG.

TODO:
    - ``extract_from_pdf``: parse text with PyMuPDF, fall back to OCR when text
      density is too low.
    - ``extract_from_image``: pure OCR pipeline with PaddleOCR.
    - Use the LLM connector to turn raw text into the Deep JSON schema described
      in ``app/schema/response.py::CVExtractionResponse``.
    - Multi-tenancy: every record must store ``user_id`` and the tenant the
      user belongs to (filter all reads by tenant in the repository layer).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.core.llm_connector import LLMConnector
from app.core.ocr_processor import OCRProcessor
from app.models.cv_record import CVRecord
from app.repository.relational_repository import RelationalRepository
from app.repository.vector_repository import VectorRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB upload cap


class ExtractionService:
    """File-in / structured-CV-out service."""

    def __init__(
        self,
        ocr_processor: OCRProcessor,
        llm_connector: LLMConnector,
        vector_repository: VectorRepository,
        cv_repository: RelationalRepository[CVRecord],
    ) -> None:
        self._ocr = ocr_processor
        self._llm = llm_connector
        self._vector_repo = vector_repository
        self._cv_repo = cv_repository

    async def extract_from_pdf(
        self,
        file_bytes: bytes,
        filename: str,
        user_id: str,
        session: AsyncSession,
    ) -> dict[str, Any]:
        """Extract structured CV data from a PDF upload."""
        raise NotImplementedError("ExtractionService.extract_from_pdf is not implemented yet.")

    async def extract_from_image(
        self,
        file_bytes: bytes,
        filename: str,
        user_id: str,
        session: AsyncSession,
    ) -> dict[str, Any]:
        """Extract structured CV data from an image upload."""
        raise NotImplementedError("ExtractionService.extract_from_image is not implemented yet.")
