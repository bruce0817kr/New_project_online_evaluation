"""
OCR Engine Interface - 추상화 레이어

모든 OCR 엔진의 공통 인터페이스를 정의합니다.
참고: .claude/skills/biz-support-eval-dev/scripts/ocr_parser.py
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class OCREngineType(Enum):
    """OCR 엔진 유형"""
    TESSERACT = "tesseract"
    OPENAI = "openai"
    GEMINI = "gemini"
    MISTRAL = "mistral"


class DocumentType(Enum):
    """지원 문서 유형"""
    BUSINESS_LICENSE = "사업자등록증"
    CORPORATE_REGISTRY = "법인등기부등본"
    FINANCIAL_STATEMENT = "재무제표"
    GENERAL = "일반문서"


@dataclass
class OCRResult:
    """OCR 분석 결과"""
    engine: OCREngineType
    document_type: DocumentType
    extracted_data: Dict[str, Any]
    confidence_score: float  # 0.0 ~ 1.0
    raw_text: str
    needs_manual_verification: bool
    processing_time_ms: float
    errors: list[str]


class BaseOCREngine(ABC):
    """
    OCR 엔진 추상 클래스

    모든 OCR 구현체는 이 인터페이스를 따라야 합니다.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.engine_type = self._get_engine_type()

    @abstractmethod
    def _get_engine_type(self) -> OCREngineType:
        """엔진 타입 반환"""
        pass

    @abstractmethod
    async def extract_text(self, image_path: str) -> str:
        """
        이미지에서 텍스트 추출

        Args:
            image_path: 이미지 파일 경로

        Returns:
            추출된 텍스트
        """
        pass

    @abstractmethod
    async def analyze_document(
        self,
        image_path: str,
        document_type: DocumentType = DocumentType.GENERAL
    ) -> OCRResult:
        """
        문서 분석 및 구조화된 데이터 추출

        Args:
            image_path: 이미지 파일 경로
            document_type: 문서 유형

        Returns:
            OCRResult 객체
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        엔진 사용 가능 여부 확인

        Returns:
            True if available, False otherwise
        """
        pass

    def get_confidence_threshold(self) -> float:
        """
        신뢰도 임계값 반환 (기본값: 0.85)

        Returns:
            임계값 (0.0 ~ 1.0)
        """
        return self.config.get("confidence_threshold", 0.85)
