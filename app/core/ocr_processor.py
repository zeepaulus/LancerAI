"""OCR Processor — text recognition for scanned PDFs / images.

Interface used by ``ExtractionService``; the concrete stack should use
PaddleOCR (vi+en) or an equivalent.

TODO:
    - Lazy Initialization: Initialize the underlying OCR engine (e.g.,
      `PaddleOCR(use_angle_cls=True, lang="vi")`) lazily upon the first method
      call to minimize startup times and memory usage for non-OCR workflows.
    - `extract_text`: Convert `image_bytes` to a NumPy array/OpenCV format. Execute
      the OCR engine over the image. Process the output to return a list of dictionaries,
      each containing `{"text": str, "confidence": float, "bbox": [x1, y1, x2, y2]}`.
    - `extract_text_grouped`: Wrap `extract_text` and implement a heuristic to concatenate
      the individual text blocks intelligently (e.g., sort by Y-coordinate then X-coordinate)
      to return a cohesive, single multiline string representing the document's content.
"""

from typing import Any


class OCRProcessor:
    """OCR contract used by the CV extraction service."""

    def __init__(self, languages: list[str] | None = None) -> None:
        self._languages = languages or ["vi", "en"]

    def extract_text(self, image_bytes: bytes) -> list[dict[str, Any]]:
        """Return a list of ``{text, confidence, bbox}`` blocks for the image.

        TODO:
            - Decode `image_bytes` into a format compatible with the OCR engine
              (e.g., using `cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)`).
            - Run the OCR inference.
            - Transform the raw inference results into the target structure:
              `[{"text": "Sample", "confidence": 0.98, "bbox": [...]}]`.
        """
        raise NotImplementedError("OCRProcessor.extract_text is not implemented yet.")

    def extract_text_grouped(self, image_bytes: bytes) -> str:
        """Return a single concatenated string of all detected text blocks.

        TODO:
            - Call `self.extract_text(image_bytes)`.
            - Apply spatial sorting logic to the blocks (top-to-bottom, left-to-right)
              to reconstruct logical reading order.
            - Join the text segments using `\n` or ` ` depending on vertical proximity.
            - Return the assembled string.
        """
        raise NotImplementedError("OCRProcessor.extract_text_grouped is not implemented yet.")
