"""Module 1 — CV extraction.

Owns the ingest pipeline:
    File upload  ->  text/OCR extraction  ->  LLM entity parsing  ->  persist.

All persistence goes through ``cv_repository``; raw text + structured JSON are
stored on ``CVRecord``. Vector embeddings are pushed to ``vector_repository``
so later modules (matching, retrieval agent) can run RAG.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

from app.core.llm_connector import LLMConnector
from app.core.ocr_processor import OCRProcessor
from app.models.cv_record import CVRecord
from app.repository.base_vector_repository import BaseVectorRepository
from app.repository.relational_repository import RelationalRepository
from app.schema.response import CVExtractionResponse

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB upload cap

# Minimum characters per page before we consider it a "text-layer" PDF.
# Below this threshold we assume the page is scanned and run OCR.
_MIN_TEXT_DENSITY = 5

_CV_EXTRACTION_SYSTEM = """Bạn là chuyên gia phân tích CV tuyển dụng.
Nhiệm vụ: Trích xuất thông tin từ CV và trả về JSON HỢP LỆ theo schema sau.
Chỉ trả về JSON thuần, không thêm markdown hay giải thích.

Schema:
{
  "personal_info": {"name":"","email":"","phone":"","linkedin":"","location":""},
  "education": [{"school":"","degree":"","major":"","gpa":"","period":""}],
  "experience": [{"company":"","title":"","period":"","descriptions":[],"key_impacts":[],"tech_stack":[]}],
  "projects": [{"name":"","role":"","tech_stack":[],"description":"","key_impacts":[],"potential_roast_points":[]}],
  "skills_matrix": {"languages":[],"frameworks":[],"tools":[],"soft_skills":[]},
  "certifications": [],
  "languages": []
}"""


def _build_extraction_prompt(raw_text: str) -> str:
    return f"""Trích xuất thông tin từ CV sau:\n\n{raw_text[:6000]}\n\nTrả về JSON theo schema đã cho:"""


def _parse_extraction_response(raw: str, cv_id: str) -> CVExtractionResponse:
    """Parse LLM JSON output into CVExtractionResponse, with a safe fallback."""
    try:
        from app.core.json_extractor import clean_and_parse_json
        data: dict[str, Any] = clean_and_parse_json(raw)
        return CVExtractionResponse(cv_id=cv_id, **data)
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        logger.warning("[Extraction] LLM JSON parse failed (%s) — returning empty schema", exc)
        return CVExtractionResponse(cv_id=cv_id)


class ExtractionService:
    """File-in / structured-CV-out service."""

    def __init__(
        self,
        ocr_processor: OCRProcessor,
        llm_connector: LLMConnector,
        vector_repository: BaseVectorRepository,
        cv_repository: RelationalRepository[CVRecord],
    ) -> None:
        self._ocr = ocr_processor
        self._llm = llm_connector
        self._vector_repo = vector_repository
        self._cv_repo = cv_repository

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def extract_from_pdf(
        self,
        file_bytes: bytes,
        filename: str,
        user_id: str,
        session: AsyncSession,
    ) -> CVExtractionResponse:
        """Extract structured CV data from a PDF upload.

        Pipeline:
          1. Validate file size.
          2. Use PyMuPDF to read the text layer.
          3. If text density is low (scanned pages), convert each page to an
             image and run OCR.
          4. Feed aggregated raw text to the LLM for structured extraction.
          5. Persist CVRecord + vector embedding.
          6. Return CVExtractionResponse.
        """
        if len(file_bytes) > MAX_FILE_SIZE:
            raise ValueError(f"File too large: {len(file_bytes)} bytes (max {MAX_FILE_SIZE})")

        raw_text = await self._extract_text_from_pdf(file_bytes)
        return await self._parse_and_persist(raw_text, filename, user_id, session)

    async def extract_from_image(
        self,
        file_bytes: bytes,
        filename: str,
        user_id: str,
        session: AsyncSession,
    ) -> CVExtractionResponse:
        """Extract structured CV data from an image upload.

        Pipeline:
          1. Validate file size.
          2. Run OCR on the image bytes.
          3. Feed raw text to the LLM for structured extraction.
          4. Persist CVRecord + vector embedding.
          5. Return CVExtractionResponse.
        """
        if len(file_bytes) > MAX_FILE_SIZE:
            raise ValueError(f"File too large: {len(file_bytes)} bytes (max {MAX_FILE_SIZE})")

        import asyncio
        loop = asyncio.get_event_loop()
        raw_text = await loop.run_in_executor(None, self._ocr.extract_text_grouped, file_bytes)
        return await self._parse_and_persist(raw_text, filename, user_id, session)

    async def get_cv(
        self,
        session: AsyncSession,
        cv_id: str,
        user_id: str,
    ) -> CVRecord | None:
        """Return a CV record owned by the given user, or None if not found."""
        results = await self._cv_repo.filter_by(session, id=cv_id, user_id=user_id)
        return results[0] if results else None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _extract_text_from_pdf(self, file_bytes: bytes) -> str:
        """Extract text from PDF, falling back to OCR for scanned pages."""
        import asyncio
        import io

        try:
            import fitz  # type: ignore[import-untyped]
        except ImportError as exc:
            raise RuntimeError(
                "PyMuPDF is not installed. Run: pip install pymupdf"
            ) from exc

        loop = asyncio.get_event_loop()

        def _sync_extract() -> str:
            doc = fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf")
            page_texts: list[str] = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text").strip()

                if len(text) >= _MIN_TEXT_DENSITY:
                    # Native text layer — use directly
                    page_texts.append(text)
                else:
                    # Scanned or image-based — render to PNG then OCR
                    logger.debug("[Extraction] Page %d: low text density (%d chars), using OCR", page_num, len(text))
                    try:
                        mat = fitz.Matrix(2.0, 2.0)  # 2× scale for better OCR accuracy
                        pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
                        img_bytes = pix.tobytes("png")
                        ocr_text = self._ocr.extract_text_grouped(img_bytes)
                        if ocr_text:
                            page_texts.append(ocr_text)
                    except Exception as exc:
                        logger.warning("[Extraction] OCR failed on page %d: %s", page_num, exc)
                        if text:
                            page_texts.append(text)

            doc.close()
            return "\n\n".join(page_texts)

        return await loop.run_in_executor(None, _sync_extract)

    async def _parse_and_persist(
        self,
        raw_text: str,
        filename: str,
        user_id: str,
        session: AsyncSession,
    ) -> CVExtractionResponse:
        """LLM parse → persist CVRecord → store vector embedding."""
        # 1. LLM structured extraction
        prompt = _build_extraction_prompt(raw_text)
        llm_response = await self._llm.generate(
            prompt,
            system=_CV_EXTRACTION_SYSTEM,
            use_cloud=bool(self._llm._cloud_api_key),
            json_mode=True,
        )

        # 2. Persist CVRecord
        cv_record = await self._cv_repo.create(
            session,
            user_id=user_id,
            filename=filename,
            language="vi",
            extracted_data={"raw_text": raw_text, "llm_raw": llm_response},
        )
        await session.commit()
        await session.refresh(cv_record)

        # 3. Parse LLM response into schema
        extraction = _parse_extraction_response(llm_response, cv_record.id)

        # 4. Update CVRecord with parsed structured data
        structured: dict[str, Any] = {
            "raw_text": raw_text,
            **extraction.model_dump(exclude={"cv_id"}),
        }
        await self._cv_repo.update(session, cv_record.id, extracted_data=structured)
        await session.commit()

        # 5. Generate & store vector embedding (best-effort; non-fatal)
        try:
            embed_text = _build_embed_text(extraction)
            embedding = await self._llm.embed(embed_text)
            if embedding:
                await self._vector_repo.store_embedding(
                    doc_id=cv_record.id,
                    text=embed_text,
                    embedding=embedding,
                    metadata={"user_id": user_id, "filename": filename, "type": "cv"},
                )
                logger.info("[Extraction] Stored embedding for CV %s (dim=%d)", cv_record.id, len(embedding))
        except Exception as exc:
            logger.warning("[Extraction] Embedding/vector store failed (non-fatal): %s", exc)

        return extraction


def _build_embed_text(extraction: CVExtractionResponse) -> str:
    """Build a compact text representation of the CV for embedding."""
    parts: list[str] = []

    pi = extraction.personal_info
    if pi.name:
        parts.append(f"Ứng viên: {pi.name}")

    skills = extraction.skills_matrix
    all_skills = skills.languages + skills.frameworks + skills.tools
    if all_skills:
        parts.append("Kỹ năng: " + ", ".join(all_skills[:30]))

    for exp in extraction.experience[:3]:
        line = f"{exp.title} tại {exp.company}"
        if exp.key_impacts:
            line += " — " + "; ".join(exp.key_impacts[:2])
        parts.append(line)

    for proj in extraction.projects[:2]:
        parts.append(f"Dự án: {proj.name} ({', '.join(proj.tech_stack[:5])})")

    return "\n".join(parts)
