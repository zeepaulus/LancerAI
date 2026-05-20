"""Module 1 — CV extraction.

Owns the ingest pipeline:
    File upload  ->  text/OCR extraction  ->  LLM entity parsing  ->  persist.

All persistence goes through ``cv_repository``; raw text + structured JSON are
stored on ``CVRecord``. Vector embeddings are pushed to ``vector_repository``
so later modules (matching, retrieval agent) can run RAG.
"""

from __future__ import annotations

import json
import uuid
from typing import TYPE_CHECKING, Any

from app.core.llm_connector import LLMConnector
from app.core.ocr_processor import OCRProcessor
from app.models.cv_record import CVRecord
from app.repository.base_vector_repository import BaseVectorRepository
from app.repository.relational_repository import RelationalRepository
from app.schema.response import CVExtractionResponse

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB upload cap
MIN_WORDS_DENSITY = 50

SYSTEM_PROMPT = """
Act as an expert CV (Curriculum Vitae) parser. Your task is to analyze the content of a CV and extract its information into a structured JSON format. The CV may be in Vietnamese or English.

Follow these rules:
1.  **Identify Sections**: Recognize standard CV sections such as:
    *   Personal Information (name, contact, links, location)
    *   Education (degree, major, school, duration, GPA)
    *   Work Experience (company, title, duration, responsibilities, achievements)
    *   Projects (project name, role, tech stack, description, impact)
    *   Skills (technical skills, soft skills, tools, languages)
    *   Certifications
    *   Awards
    *   Other relevant sections

2.  **Extract Data**: For each section, extract the relevant information and map it to the corresponding fields in the JSON schema below.
    *   Ensure dates are parsed correctly (e.g., "2018 - 2022", "Jan 2020 - May 2021", "Present").
    *   For descriptions and responsibilities, capture the key points accurately.
    *   For skills, categorize them appropriately.

3.  **Handle Unclear or Missing Information**: 
    *   If a field cannot be determined with reasonable confidence, set it to null.
    *   Do not make up or guess information that is not explicitly present in the text.
    *   If the entire CV is unclear, ambiguous, or cannot be parsed, return an empty JSON object.

4.  **Output Format**: Return a valid JSON object that strictly adheres to the following schema.
    *   **language**: Detect the primary language of the CV (e.g., "vi", "en") and set it accordingly.
    *   **personal_info**: Extract the candidate's personal information.
        *   **name**: Full name of the candidate.
        *   **email**: Primary email address.
        *   **phone**: Phone number (including country code if available).
        *   **linkedin**: LinkedIn profile URL.
        *   **github**: GitHub profile URL.
        *   **location**: Candidate's location (city, country).
        *   **portfolio**: Portfolio/website URL.
    *   **education**: A list of educational experiences, ordered chronologically (most recent first).
        *   **school**: Name of the institution.
        *   **degree**: Degree obtained (e.g., Bachelor, Master, PhD).
        *   **major**: Field of study.
        *   **gpa**: Grade Point Average (if available).
        *   **period**: Duration of study (e.g., "2018 - 2022").
        *   **description**: Additional details about the education.
    *   **experience**: A list of work experiences, ordered chronologically (most recent first).
        *   **company**: Name of the company.
        *   **title**: Job title/position.
        *   **period**: Duration of employment (e.g., "Jan 2020 - May 2021").
        *   **descriptions**: A list of responsibilities and duties.
        *   **key_impacts**: A list of significant achievements and impacts.
        *   **tech_stack**: A list of technologies, tools, and frameworks used.
    *   **projects**: A list of projects the candidate has worked on, ordered by relevance or recency.
        *   **name**: Project name.
        *   **role**: Role in the project.
        *   **tech_stack**: Technologies and tools used.
        *   **description**: Brief description of the project.
        *   **key_impacts**: Key achievements and outcomes.
        *   **potential_roast_points**: Weaknesses, risks, or areas that might attract scrutiny.
    *   **skills_matrix**: A structured breakdown of skills.
        *   **languages**: Programming languages (e.g., ["Python", "JavaScript"]).
        *   **frameworks**: Frameworks and libraries (e.g., ["React", "Django"]).
        *   **tools**: Tools and software (e.g., ["Docker", "Git"]).
        *   **soft_skills**: Soft skills (e.g., ["Communication", "Teamwork"]).
    *   **certifications**: A list of professional certifications.
    *   **languages**: A list of languages spoken and proficiency levels.

5.  **Handling Unstructured Text**: If the CV is heavily unstructured or appears to be a scanned document without selectable text, attempt to extract the text as best as possible. However, if the extracted text is fragmented or makes the CV ambiguous, return an empty JSON object.

6.  **Consistency**: Ensure that all information is consistent and accurate based on the provided text. Do not infer information that is not present.

Return only the JSON object, without any additional text, explanations, or markdown formatting.
"""

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

    def _generate_mock_embedding(self) -> list[float]:
        """Generate a mock embedding vector (384 dimensions) for temporary storage."""
        return [0.1] * 384

    async def extract_from_pdf(
        self,
        file_bytes: bytes,
        filename: str,
        user_id: str,
        session: AsyncSession,
    ) -> CVExtractionResponse:
        """Extract structured CV data from a PDF upload.

        Uses PyMuPDF (fitz) to read the PDF. Automatically falls back to OCR
        if character density on any page is low (e.g., scanned PDF).
        """
        # Input Validation
        if len(file_bytes) > MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds the limit of {MAX_FILE_SIZE} bytes.")

        import fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        
        raw_text_parts = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            
            # Density Check: if text is short, convert page to image and use OCR
            if len(text.strip()) < MIN_WORDS_DENSITY:
                pix = page.get_pixmap()
                img_bytes = pix.tobytes("png")
                ocr_text = self._ocr.extract_text_grouped(img_bytes)
                raw_text_parts.append(ocr_text)
            else:
                raw_text_parts.append(text)
                
        raw_text = "\n".join(raw_text_parts)

        # LLM Structuring
        system_prompt = SYSTEM_PROMPT
        user_prompt = f"Raw CV Text:\n{raw_text}"
        
        llm_response = await self._llm.generate(
            prompt=user_prompt,
            system=system_prompt,
            json_mode=True,
        )
        
        extracted_dict = json.loads(llm_response)

        # Relational Persistence
        cv_id = str(uuid.uuid4())
        await self._cv_repo.create(
            session,
            id=cv_id,
            user_id=user_id,
            filename=filename,
            language="vi",
            extracted_data=extracted_dict,
        )

        # Vector Persistence (Using mock embedding for temporary storage)
        mock_embedding = self._generate_mock_embedding()
        metadata = {"user_id": user_id, "filename": filename}
        await self._vector_repo.store_embedding(
            doc_id=cv_id,
            text=raw_text,
            embedding=mock_embedding,
            metadata=metadata,
        )

        # Build response schema
        from app.schema.response import PersonalInfo, Education, Experience, Project, SkillsMatrix
        
        personal_info = PersonalInfo(**extracted_dict.get("personal_info", {}))
        education_list = [Education(**edu) for edu in extracted_dict.get("education", [])]
        experience_list = [Experience(**exp) for exp in extracted_dict.get("experience", [])]
        projects_list = [Project(**proj) for proj in extracted_dict.get("projects", [])]
        skills_matrix = SkillsMatrix(**extracted_dict.get("skills_matrix", {}))
        certifications = extracted_dict.get("certifications", [])
        languages = extracted_dict.get("languages", [])

        return CVExtractionResponse(
            cv_id=cv_id,
            personal_info=personal_info,
            education=education_list,
            experience=experience_list,
            projects=projects_list,
            skills_matrix=skills_matrix,
            certifications=certifications,
            languages=languages,
        )

    async def get_cv(
        self,
        session: AsyncSession,
        cv_id: str,
        user_id: str,
    ) -> CVRecord | None:
        """Return a CV record owned by the given user, or None if not found."""
        results = await self._cv_repo.filter_by(session, id=cv_id, user_id=user_id)
        return results[0] if results else None

    async def extract_from_image(
        self,
        file_bytes: bytes,
        filename: str,
        user_id: str,
        session: AsyncSession,
    ) -> CVExtractionResponse:
        """Extract structured CV data from an image upload.

        Processes the image bytes directly through OCR to yield raw text blocks,
        maps it to structured JSON via LLM, and persists.
        """
        # Input Validation
        if len(file_bytes) > MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds the limit of {MAX_FILE_SIZE} bytes.")

        # OCR Processing
        raw_text = self._ocr.extract_text_grouped(file_bytes)

        # LLM Structuring
        system_prompt = SYSTEM_PROMPT
        user_prompt = f"Raw CV Text:\n{raw_text}"
        
        llm_response = await self._llm.generate(
            prompt=user_prompt,
            system=system_prompt,
            json_mode=True,
        )
        
        extracted_dict = json.loads(llm_response)

        # DB Persistence
        cv_id = str(uuid.uuid4())
        await self._cv_repo.create(
            session,
            id=cv_id,
            user_id=user_id,
            filename=filename,
            language="vi",
            extracted_data=extracted_dict,
        )

        # Vector Persistence (Using mock embedding for temporary storage)
        mock_embedding = self._generate_mock_embedding()
        metadata = {"user_id": user_id, "filename": filename}
        await self._vector_repo.store_embedding(
            doc_id=cv_id,
            text=raw_text,
            embedding=mock_embedding,
            metadata=metadata,
        )

        # Build response schema
        from app.schema.response import PersonalInfo, Education, Experience, Project, SkillsMatrix
        
        personal_info = PersonalInfo(**extracted_dict.get("personal_info", {}))
        education_list = [Education(**edu) for edu in extracted_dict.get("education", [])]
        experience_list = [Experience(**exp) for exp in extracted_dict.get("experience", [])]
        projects_list = [Project(**proj) for proj in extracted_dict.get("projects", [])]
        skills_matrix = SkillsMatrix(**extracted_dict.get("skills_matrix", {}))
        certifications = extracted_dict.get("certifications", [])
        languages = extracted_dict.get("languages", [])

        return CVExtractionResponse(
            cv_id=cv_id,
            personal_info=personal_info,
            education=education_list,
            experience=experience_list,
            projects=projects_list,
            skills_matrix=skills_matrix,
            certifications=certifications,
            languages=languages,
        )
