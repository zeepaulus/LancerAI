"""Tests for app.core.ocr_processor — OCR Processor initialization, lazy loading, and spatial sorting."""

from __future__ import annotations

from unittest.mock import MagicMock, patch
import pytest

from app.core.ocr_processor import OCRProcessor


class TestOCRProcessorInitialization:
    """Test standard initialization and lazy loading properties."""

    def test_default_initialization(self) -> None:
        processor = OCRProcessor()
        assert processor._languages == ["vi"]
        assert processor._ocr_engine is None

    def test_custom_languages_initialization(self) -> None:
        processor = OCRProcessor(languages=["vi", "en"])
        assert processor._languages == ["vi", "en"]
        assert processor._ocr_engine is None


class TestOCRProcessorLazyLoading:
    """Test that the PaddleOCR engine is only loaded and initialized when needed."""

    def test_lazy_loading_occurs_on_demand(self) -> None:
        import sys
        from unittest.mock import MagicMock
        
        # Mock the paddleocr module and class to prevent real imports
        mock_paddleocr_module = MagicMock()
        mock_paddle_ocr_class = MagicMock()
        mock_paddleocr_module.PaddleOCR = mock_paddle_ocr_class
        
        original_module = sys.modules.get("paddleocr")
        
        try:
            sys.modules["paddleocr"] = mock_paddleocr_module
            
            processor = OCRProcessor()
            assert processor._ocr_engine is None

            # Call the getter for the engine which triggers dynamic import
            engine = processor._get_ocr_engine()
            
            # Verify PaddleOCR mock class was instantiated with correct args
            mock_paddle_ocr_class.assert_called_once_with(use_angle_cls=True, lang="vi", show_log=False)
            assert engine == mock_paddle_ocr_class.return_value
            assert processor._ocr_engine == mock_paddle_ocr_class.return_value
            
        finally:
            # Restore the module registry
            if original_module is not None:
                sys.modules["paddleocr"] = original_module
            else:
                sys.modules.pop("paddleocr", None)


class TestOCRProcessorSpatialSorting:
    """Test spatial sorting and text line reconstruction in extract_text_grouped."""

    def test_extract_text_grouped_empty(self) -> None:
        processor = OCRProcessor()
        
        # Mock extract_text to return empty list
        with patch.object(processor, "extract_text", return_value=[]):
            result = processor.extract_text_grouped(b"dummy_image_bytes")
            assert result == ""

    def test_extract_text_grouped_spatial_sorting_logic(self) -> None:
        processor = OCRProcessor()
        
        # We will mock the output of extract_text with blocks that are:
        # - Out of order vertically and horizontally
        # - Some are on the same line (Y-coords within 15px threshold)
        mocked_blocks = [
            # Line 2 (Y ≈ 100), Right block
            {"text": "Dòng 2 Phải", "confidence": 0.99, "bbox": [200.0, 102.0, 300.0, 120.0]},
            # Line 1 (Y ≈ 50), Left block
            {"text": "Dòng 1 Trái", "confidence": 0.98, "bbox": [10.0, 50.0, 100.0, 70.0]},
            # Line 1 (Y ≈ 50), Right block (slightly different Y, < 15px difference)
            {"text": "Dòng 1 Phải", "confidence": 0.97, "bbox": [150.0, 53.0, 250.0, 72.0]},
            # Line 2 (Y ≈ 100), Left block
            {"text": "Dòng 2 Trái", "confidence": 0.96, "bbox": [15.0, 99.0, 110.0, 118.0]},
            # Line 3 (Y ≈ 200), Middle block
            {"text": "Dòng 3", "confidence": 0.95, "bbox": [80.0, 200.0, 180.0, 220.0]}
        ]

        with patch.object(processor, "extract_text", return_value=mocked_blocks):
            result = processor.extract_text_grouped(b"dummy_image_bytes")
            
            # Expected text line reconstruction:
            # Line 1: "Dòng 1 Trái Dòng 1 Phải"
            # Line 2: "Dòng 2 Trái Dòng 2 Phải"
            # Line 3: "Dòng 3"
            expected_lines = [
                "Dòng 1 Trái Dòng 1 Phải",
                "Dòng 2 Trái Dòng 2 Phải",
                "Dòng 3"
            ]
            assert result == "\n".join(expected_lines)
