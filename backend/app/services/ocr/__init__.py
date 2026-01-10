"""
OCR Services - 멀티 엔진 통합

사용 가능한 엔진:
- Tesseract (온프레미스)
- OpenAI Vision API (GPT-4o)
- Google Gemini Vision
- Mistral Pixtral

사용 예시:
    from app.services.ocr import OCRManager, DocumentType

    manager = OCRManager(config={
        "openai": {"api_key": "sk-..."},
        "fallback_strategy": "on_low_confidence"
    })

    result = await manager.analyze_document(
        "path/to/image.jpg",
        DocumentType.BUSINESS_LICENSE
    )
"""
from .base import BaseOCREngine, OCREngineType, DocumentType, OCRResult
from .manager import OCRManager, FallbackStrategy
from .tesseract_engine import TesseractEngine
from .openai_engine import OpenAIEngine
from .gemini_engine import GeminiEngine
from .mistral_engine import MistralEngine

__all__ = [
    "BaseOCREngine",
    "OCREngineType",
    "DocumentType",
    "OCRResult",
    "OCRManager",
    "FallbackStrategy",
    "TesseractEngine",
    "OpenAIEngine",
    "GeminiEngine",
    "MistralEngine",
]
