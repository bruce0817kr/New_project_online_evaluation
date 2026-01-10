"""
OCR Test Fixtures and Mock Data

테스트용 샘플 데이터 및 Mock 객체를 제공합니다.
"""
import pytest
from PIL import Image
import io
import os
from unittest.mock import Mock, AsyncMock, patch

from app.services.ocr import (
    OCREngineType,
    DocumentType,
    OCRResult
)


@pytest.fixture
def sample_business_license_text():
    """사업자등록증 샘플 텍스트"""
    return """
    사업자등록증

    사업자등록번호: 123-45-67890
    상 호: (주)테크이노베이션
    대표자: 홍길동
    개업일자: 2020년 3월 15일
    사업장 소재지: 서울특별시 강남구 테헤란로 123
    업 태: 정보통신업
    종 목: 소프트웨어 개발 및 공급
    """


@pytest.fixture
def sample_corporate_registry_text():
    """법인등기부등본 샘플 텍스트"""
    return """
    법인등기부등본

    법인등록번호: 110111-1234567
    상 호: 주식회사 테크이노베이션
    자본금: 100,000,000원
    대표이사: 홍길동
    """


@pytest.fixture
def sample_image_path(tmp_path):
    """테스트용 이미지 파일 생성"""
    # 100x100 흰색 이미지 생성
    image = Image.new('RGB', (100, 100), color='white')
    image_path = tmp_path / "test_document.jpg"
    image.save(image_path)
    return str(image_path)


@pytest.fixture
def expected_business_license_data():
    """예상되는 사업자등록증 파싱 결과"""
    return {
        "사업자등록번호": "123-45-67890",
        "상호": "(주)테크이노베이션",
        "대표자": "홍길동",
        "개업일자": "2020년 3월 15일",
        "사업장주소": "서울특별시 강남구 테헤란로 123",
        "업태": "정보통신업",
        "종목": "소프트웨어 개발 및 공급"
    }


@pytest.fixture
def mock_ocr_result():
    """Mock OCR 결과"""
    return OCRResult(
        engine=OCREngineType.TESSERACT,
        document_type=DocumentType.BUSINESS_LICENSE,
        extracted_data={
            "사업자등록번호": "123-45-67890",
            "상호": "(주)테크이노베이션",
            "대표자": "홍길동"
        },
        confidence_score=0.92,
        raw_text="사업자등록증...",
        needs_manual_verification=False,
        processing_time_ms=150.5,
        errors=[]
    )


@pytest.fixture
def mock_low_confidence_result():
    """낮은 신뢰도 OCR 결과"""
    return OCRResult(
        engine=OCREngineType.TESSERACT,
        document_type=DocumentType.BUSINESS_LICENSE,
        extracted_data={
            "사업자등록번호": "123-45-67890"
        },
        confidence_score=0.65,
        raw_text="불완전한 텍스트...",
        needs_manual_verification=True,
        processing_time_ms=120.0,
        errors=["상호를 찾을 수 없습니다"]
    )


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API 응답"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = """
    {
        "사업자등록번호": "123-45-67890",
        "상호": "(주)테크이노베이션",
        "대표자": "홍길동",
        "사업장주소": "서울특별시 강남구 테헤란로 123",
        "confidence": 0.95
    }
    """
    return mock_response


@pytest.fixture
def mock_gemini_response():
    """Mock Gemini API 응답"""
    mock_response = Mock()
    mock_response.text = """
    ```json
    {
        "사업자등록번호": "123-45-67890",
        "상호": "(주)테크이노베이션",
        "대표자": "홍길동",
        "confidence": 0.93
    }
    ```
    """
    return mock_response


@pytest.fixture
def ocr_config_tesseract_only():
    """Tesseract만 사용하는 설정"""
    return {
        "tesseract": {
            "confidence_threshold": 0.85
        },
        "fallback_strategy": "none"
    }


@pytest.fixture
def ocr_config_with_fallback():
    """폴백이 활성화된 설정"""
    return {
        "tesseract": {},
        "openai": {
            "api_key": "sk-test-key"
        },
        "fallback_strategy": "on_low_confidence",
        "confidence_threshold": 0.85
    }


@pytest.fixture
def ocr_config_ensemble():
    """앙상블 모드 설정"""
    return {
        "tesseract": {},
        "openai": {"api_key": "sk-test"},
        "gemini": {"api_key": "test-key"},
        "enable_ensemble": True,
        "confidence_threshold": 0.85
    }
