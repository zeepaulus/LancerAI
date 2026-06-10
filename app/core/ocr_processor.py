"""OCR Processor — text recognition for scanned PDFs / images.

Interface used by ``ExtractionService``; the concrete stack uses
PaddleOCR (vi+en) with lazy initialisation.

Lazy Initialization: The OCR engine is created on the first method
call to avoid paying the torch/paddle import cost for workflows that
never touch OCR (e.g., native-text PDF paths).
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class OCRProcessor:
    """OCR contract used by the CV extraction service.

    Args:
        languages: List of BCP-47/PaddleOCR language codes.
                   Defaults to ``["vi", "en"]`` (Vietnamese + English).
        use_angle_cls: Enable automatic text angle classification.
    """

    def __init__(
        self,
        languages: list[str] | None = None,
        use_angle_cls: bool = True,
    ) -> None:
        self._languages = languages or ["vi", "en"]
        self._use_angle_cls = use_angle_cls
        self._ocr: Any = None  # PaddleOCR instance — lazy loaded

    # ------------------------------------------------------------------
    # Lazy initialisation
    # ------------------------------------------------------------------

    def _ensure_ocr(self) -> None:
        """Load PaddleOCR on the first call (deferred to avoid cold-start cost)."""
        if self._ocr is not None:
            return
        try:
            from paddleocr import PaddleOCR  # type: ignore[import-untyped]

            lang = self._languages[0] if self._languages else "en"
            logger.info("[OCR] Loading PaddleOCR (lang=%s, angle_cls=%s)", lang, self._use_angle_cls)
            self._ocr = PaddleOCR(
                use_angle_cls=self._use_angle_cls,
                lang=lang,
                enable_mkldnn=False,
            )
            logger.info("[OCR] PaddleOCR ready")
        except ImportError as exc:
            raise RuntimeError(
                "PaddleOCR is not installed. "
                "Run: uv add paddleocr paddlepaddle"
            ) from exc

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_text(self, image_bytes: bytes) -> list[dict[str, Any]]:
        """Return a list of ``{text, confidence, bbox}`` blocks for the image.

        Each block represents one detected text region:
        - ``text``: the recognised string.
        - ``confidence``: detection confidence in [0, 1].
        - ``bbox``: ``[x1, y1, x2, y2]`` bounding box (top-left → bottom-right).
        """
        self._ensure_ocr()

        # Decode bytes → numpy array (BGR, as expected by PaddleOCR)
        try:
            import cv2
            arr = np.frombuffer(image_bytes, dtype=np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if img is None:
                logger.warning("[OCR] cv2.imdecode returned None — empty/invalid image bytes")
                return []
        except ImportError:
            # Fallback: PIL → numpy (no cv2)
            import io

            from PIL import Image
            pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            img = np.array(pil_img)[:, :, ::-1]  # RGB → BGR

        try:
            raw = self._ocr.ocr(img, cls=self._use_angle_cls)
        except TypeError:
            raw = self._ocr.ocr(img)
        if not raw or raw[0] is None:
            return []

        if raw and isinstance(raw[0], dict):
            dict_data = raw[0]
            texts = dict_data.get("rec_texts", [])
            scores = dict_data.get("rec_scores", [])
            polys = dict_data.get("dt_polys") or dict_data.get("rec_polys") or dict_data.get("rec_boxes", [])
            
            classic_list = []
            for i in range(len(texts)):
                text = texts[i]
                score = scores[i] if i < len(scores) else 1.0
                poly = polys[i] if i < len(polys) else [[0, 0], [0, 0], [0, 0], [0, 0]]
                if hasattr(poly, "tolist"):
                    poly = poly.tolist()
                classic_list.append([poly, (text, score)])
            raw = [classic_list]

        results: list[dict[str, Any]] = []
        for line in raw[0]:
            if line is None:
                continue
            # PaddleOCR format: [[x1,y1],[x2,y1],[x2,y2],[x1,y2]], (text, conf)
            bbox_points, (text, confidence) = line
            xs = [pt[0] for pt in bbox_points]
            ys = [pt[1] for pt in bbox_points]
            bbox = [min(xs), min(ys), max(xs), max(ys)]
            results.append(
                {
                    "text": str(text),
                    "confidence": float(confidence),
                    "bbox": bbox,
                }
            )
        return results

    def extract_text_grouped(self, image_bytes: bytes, min_confidence: float = 0.4) -> str:
        """Return a single concatenated string of all detected text blocks.

        Blocks are sorted top-to-bottom (primary) and left-to-right (secondary)
        to reconstruct the natural reading order of the document.
        Blocks on roughly the same line are joined with a space; otherwise a
        newline is inserted.

        Improvements over the original:
          - Dynamic y_threshold based on average block height (adapts to font size).
          - Confidence filtering: blocks below ``min_confidence`` are skipped.
          - Empty/whitespace-only blocks are silently dropped.
        """
        blocks = self.extract_text(image_bytes)
        if not blocks:
            return ""

        # Filter low-confidence blocks (OCR noise)
        blocks = [b for b in blocks if b["confidence"] >= min_confidence and b["text"].strip()]
        if not blocks:
            return ""

        # Sort: y1 primary (top-to-bottom), x1 secondary (left-to-right)
        blocks_sorted = sorted(blocks, key=lambda b: (b["bbox"][1], b["bbox"][0]))

        # Compute dynamic y_threshold based on median block height
        heights = [b["bbox"][3] - b["bbox"][1] for b in blocks_sorted if b["bbox"][3] > b["bbox"][1]]
        if heights:
            heights.sort()
            median_height = heights[len(heights) // 2]
            y_threshold = max(5, median_height * 0.5)  # half the median block height
        else:
            y_threshold = 10  # fallback

        lines: list[str] = []
        prev_y = None
        line_buffer: list[str] = []

        for block in blocks_sorted:
            y1 = block["bbox"][1]
            text = block["text"].strip()
            if not text:
                continue

            if prev_y is None or abs(y1 - prev_y) <= y_threshold:
                # Same line — accumulate
                line_buffer.append(text)
            else:
                # New line
                if line_buffer:
                    lines.append(" ".join(line_buffer))
                line_buffer = [text]

            prev_y = y1

        if line_buffer:
            lines.append(" ".join(line_buffer))

        return "\n".join(lines)

