"""CV template rendering — JSON projection and PDF generation."""

from __future__ import annotations

from typing import Any

from app.core.llm_connector import LLMConnector

_ALLOWED_TEMPLATES = {"harvard", "modern", "minimal", "creative"}


class CVTemplateRenderer:
    """Renders structured CV data into named templates (JSON and PDF)."""

    def __init__(self, llm_connector: LLMConnector) -> None:
        self._llm = llm_connector

    async def render_cv(self, cv_data: dict[str, Any], template: str = "harvard") -> dict[str, Any]:
        """Project CV data into a named template via the LLM.

        TODO:
            - Validate `template` against `_ALLOWED_TEMPLATES`.
            - Construct an LLM prompt with template requirements and `cv_data`.
            - Request structured JSON output matching the template schema.
            - Return the structured dict.
        """
        raise NotImplementedError("CVTemplateRenderer.render_cv is not implemented yet.")

    async def render_pdf(self, cv_data: dict[str, Any], template: str = "harvard") -> bytes:
        """Render the chosen template to a PDF byte stream.

        TODO:
            - Call `self.render_cv(cv_data, template)` to get structured data.
            - Render HTML via a Jinja2 template matching `template`.
            - Convert HTML to PDF with WeasyPrint `HTML(string=html).write_pdf()`.
            - Return raw bytes.
        """
        raise NotImplementedError("CVTemplateRenderer.render_pdf is not implemented yet.")
