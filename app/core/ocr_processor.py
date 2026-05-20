"""OCR Processor — text recognition for scanned PDFs / images.

Interface used by ``ExtractionService``; the concrete stack should use
PaddleOCR (vi+en) or an equivalent.
"""

from typing import Any


class OCRProcessor:
    """OCR contract used by the CV extraction service."""

    def __init__(self, languages: list[str] | None = None) -> None:
        self._languages = languages or ["vi", "en"]
        self._ocr_engine = None

    def _get_ocr_engine(self) -> Any:
        """Lazily initialize the underlying PaddleOCR engine to reduce startup times."""
        if self._ocr_engine is None:
            # We import here to keep application startup light
            from paddleocr import PaddleOCR
            
            lang = self._languages[0] if self._languages else "vi"
            self._ocr_engine = PaddleOCR(use_angle_cls=True, lang=lang, show_log=False)
        return self._ocr_engine

    def extract_text(self, image_bytes: bytes) -> list[dict[str, Any]]:
        """Return a list of ``{text, confidence, bbox}`` blocks for a single image.

        Processes image bytes, runs PaddleOCR, and maps coordinates to [x1, y1, x2, y2].
        """
        import cv2
        import numpy as np

        # Decode image bytes
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Failed to decode image bytes.")

        ocr_engine = self._get_ocr_engine()
        result = ocr_engine.ocr(image, cls=True)
        # Expected result:
        # [
        #     [
        #         [
        #             [[34.0, 45.0], [120.0, 45.0], [120.0, 70.0], [34.0, 70.0]],
        #             ("Hello", 0.998)
        #         ],
        #         [
        #             [[50.0, 100.0], [200.0, 100.0], [200.0, 130.0], [50.0, 130.0]],
        #             ("World", 0.995)
        #         ]
        #     ]
        # ]

        blocks = []
        if result and result[0]:
            for line in result[0]:
                bbox = line[0]  # Format: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                text = line[1][0]
                confidence = float(line[1][1])

                # Extract bounding box edges
                xs = [pt[0] for pt in bbox]
                ys = [pt[1] for pt in bbox]
                x1, y1 = min(xs), min(ys)
                x2, y2 = max(xs), max(ys)

                blocks.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": [float(x1), float(y1), float(x2), float(y2)]
                })

        return blocks

    def extract_text_grouped(self, image_bytes: bytes) -> str:
        """Return a single concatenated string of all detected text blocks in one image.

        Applies spatial sorting logic (top-to-bottom, left-to-right) to reconstruct
        the logical reading order of a CV.
        """
        blocks = self.extract_text(image_bytes)
        if not blocks:
            return ""

        # Spatial sorting:
        # 1. Sort primarily by Y-coordinate (top-to-bottom)
        blocks.sort(key=lambda b: b["bbox"][1])

        lines = []
        current_line = []
        current_y_thresh = None
        
        # 15px threshold to group text segments on the same horizontal line
        LINE_THRESHOLD = 15.0

        for b in blocks:
            y1 = b["bbox"][1]
            if current_y_thresh is None:
                current_line.append(b)
                current_y_thresh = y1
            elif abs(y1 - current_y_thresh) < LINE_THRESHOLD:
                current_line.append(b)
            else:
                # Sort current line from left to right (X-coordinate)
                current_line.sort(key=lambda item: item["bbox"][0])
                lines.append(" ".join([item["text"] for item in current_line]))
                
                # Start a new line
                current_line = [b]
                current_y_thresh = y1

        if current_line:
            current_line.sort(key=lambda item: item["bbox"][0])
            lines.append(" ".join([item["text"] for item in current_line]))

        return "\n".join(lines)
