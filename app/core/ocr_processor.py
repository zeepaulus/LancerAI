"""OCR Processor — text recognition for scanned PDFs / images.

Interface used by ``ExtractionService``; the concrete stack should use
PaddleOCR (vi+en) or an equivalent.

TODO:
    - Lazy-init PaddleOCR with use_angle_cls=True, lang="vi".
    - Implement ``extract_text`` returning per-block (text, confidence, bbox).
    - Implement ``extract_text_grouped`` joining blocks into one string.
"""

from typing import Any


class OCRProcessor:
    """OCR contract used by the CV extraction service."""

    def __init__(self, languages: list[str] | None = None) -> None:
        self._languages = languages or ["vi", "en"]

    def extract_text(self, image_bytes: bytes) -> list[dict[str, Any]]:
        """Return a list of ``{text, confidence, bbox}`` blocks for the image."""
        raise NotImplementedError("OCRProcessor.extract_text is not implemented yet.")

    def extract_text_grouped(self, image_bytes: bytes) -> str:
        """Return a single concatenated string of all detected text blocks."""
        raise NotImplementedError("OCRProcessor.extract_text_grouped is not implemented yet.")
