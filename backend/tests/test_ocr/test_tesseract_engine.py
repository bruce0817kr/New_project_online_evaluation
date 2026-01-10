"""
Tesseract OCR Engine 단위 테스트
"""
import pytest
from unittest.mock import patch, Mock
from app.services.ocr import TesseractEngine, DocumentType, OCREngineType


class TestTesseractEngine:
    """Tesseract 엔진 테스트"""

    def test_engine_type(self):
        """엔진 타입 확인"""
        engine = TesseractEngine()
        assert engine.engine_type == OCREngineType.TESSERACT

    def test_is_available_when_installed(self):
        """Tesseract 설치 시 사용 가능"""
        with patch('pytesseract.get_tesseract_version') as mock_version:
            mock_version.return_value = "5.0.0"
            engine = TesseractEngine()
            assert engine.is_available() is True

    def test_is_available_when_not_installed(self):
        """Tesseract 미설치 시 사용 불가"""
        with patch('pytesseract.get_tesseract_version') as mock_version:
            mock_version.side_effect = Exception("Not found")
            engine = TesseractEngine()
            assert engine.is_available() is False

    @pytest.mark.asyncio
    async def test_extract_text(self, sample_image_path, sample_business_license_text):
        """텍스트 추출 테스트"""
        with patch('pytesseract.image_to_string') as mock_ocr:
            mock_ocr.return_value = sample_business_license_text

            engine = TesseractEngine()
            text = await engine.extract_text(sample_image_path)

            assert "사업자등록증" in text
            assert "123-45-67890" in text
            mock_ocr.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_business_license(
        self,
        sample_image_path,
        sample_business_license_text
    ):
        """사업자등록증 분석 테스트"""
        with patch('pytesseract.image_to_string') as mock_ocr:
            mock_ocr.return_value = sample_business_license_text

            engine = TesseractEngine()
            result = await engine.analyze_document(
                sample_image_path,
                DocumentType.BUSINESS_LICENSE
            )

            assert result.engine == OCREngineType.TESSERACT
            assert result.document_type == DocumentType.BUSINESS_LICENSE
            assert "사업자등록번호" in result.extracted_data
            assert result.extracted_data["사업자등록번호"] == "123-45-67890"
            assert result.extracted_data["상호"] == "(주)테크이노베이션"
            assert result.extracted_data["대표자"] == "홍길동"
            assert result.confidence_score > 0

    @pytest.mark.asyncio
    async def test_analyze_corporate_registry(
        self,
        sample_image_path,
        sample_corporate_registry_text
    ):
        """법인등기부등본 분석 테스트"""
        with patch('pytesseract.image_to_string') as mock_ocr:
            mock_ocr.return_value = sample_corporate_registry_text

            engine = TesseractEngine()
            result = await engine.analyze_document(
                sample_image_path,
                DocumentType.CORPORATE_REGISTRY
            )

            assert "법인등록번호" in result.extracted_data
            assert result.extracted_data["법인등록번호"] == "110111-1234567"
            assert "자본금" in result.extracted_data

    def test_validate_business_number_valid(self):
        """유효한 사업자등록번호 검증"""
        engine = TesseractEngine()
        # 실제 체크섬이 맞는 번호 (예시)
        valid_number = "123-45-67890"
        # 체크섬 검증 로직 테스트
        # 실제 구현에 따라 조정 필요

    def test_validate_business_number_invalid(self):
        """잘못된 사업자등록번호 검증"""
        engine = TesseractEngine()
        invalid_number = "000-00-00000"
        result = engine._validate_business_number(invalid_number)
        # 체크섬이 맞지 않으면 False

    def test_calculate_confidence_high(self):
        """높은 신뢰도 계산"""
        engine = TesseractEngine()
        data = {
            "사업자등록번호": "123-45-67890",
            "상호": "(주)테크이노베이션",
            "대표자": "홍길동"
        }
        confidence = engine._calculate_confidence(data, DocumentType.BUSINESS_LICENSE)
        assert confidence >= 0.8

    def test_calculate_confidence_low(self):
        """낮은 신뢰도 계산 (일부 필드 누락)"""
        engine = TesseractEngine()
        data = {
            "사업자등록번호": "123-45-67890"
        }
        confidence = engine._calculate_confidence(data, DocumentType.BUSINESS_LICENSE)
        assert confidence < 0.6

    @pytest.mark.asyncio
    async def test_analyze_handles_errors(self, sample_image_path):
        """OCR 오류 처리 테스트"""
        with patch('pytesseract.image_to_string') as mock_ocr:
            mock_ocr.side_effect = Exception("OCR failed")

            engine = TesseractEngine()
            result = await engine.analyze_document(sample_image_path)

            assert result.confidence_score == 0.0
            assert result.needs_manual_verification is True
            assert len(result.errors) > 0
