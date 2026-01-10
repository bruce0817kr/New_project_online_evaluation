"""
OCR Manager 폴백 전략 테스트
"""
import pytest
from unittest.mock import AsyncMock, patch, Mock

from app.services.ocr import (
    OCRManager,
    FallbackStrategy,
    OCREngineType,
    DocumentType,
    OCRResult
)


class TestOCRManager:
    """OCR 매니저 테스트"""

    def test_initialization_tesseract_only(self, ocr_config_tesseract_only):
        """Tesseract만 초기화"""
        with patch('app.services.ocr.tesseract_engine.TesseractEngine.is_available') as mock_available:
            mock_available.return_value = True

            manager = OCRManager(ocr_config_tesseract_only)

            assert len(manager.engines) >= 1
            assert manager.engines[0].engine_type == OCREngineType.TESSERACT

    def test_initialization_with_multiple_engines(self, ocr_config_with_fallback):
        """여러 엔진 초기화"""
        with patch('app.services.ocr.tesseract_engine.TesseractEngine.is_available') as mock_tess:
            with patch('app.services.ocr.openai_engine.OpenAIEngine.is_available') as mock_openai:
                mock_tess.return_value = True
                mock_openai.return_value = True

                manager = OCRManager(ocr_config_with_fallback)

                available_types = [e.engine_type for e in manager.engines]
                assert OCREngineType.TESSERACT in available_types
                assert OCREngineType.OPENAI in available_types

    @pytest.mark.asyncio
    async def test_analyze_with_high_confidence_no_fallback(
        self,
        ocr_config_with_fallback,
        sample_image_path,
        mock_ocr_result
    ):
        """높은 신뢰도: 폴백 없이 첫 엔진 결과 반환"""
        with patch('app.services.ocr.tesseract_engine.TesseractEngine.is_available') as mock_available:
            with patch('app.services.ocr.tesseract_engine.TesseractEngine.analyze_document') as mock_analyze:
                mock_available.return_value = True
                mock_analyze.return_value = mock_ocr_result  # 신뢰도 0.92

                manager = OCRManager(ocr_config_with_fallback)
                result = await manager.analyze_document(sample_image_path)

                assert result.engine == OCREngineType.TESSERACT
                assert result.confidence_score == 0.92
                mock_analyze.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_with_low_confidence_fallback(
        self,
        ocr_config_with_fallback,
        sample_image_path,
        mock_low_confidence_result,
        mock_ocr_result
    ):
        """낮은 신뢰도: 다음 엔진으로 폴백"""
        with patch('app.services.ocr.tesseract_engine.TesseractEngine.is_available') as mock_tess_avail:
            with patch('app.services.ocr.openai_engine.OpenAIEngine.is_available') as mock_openai_avail:
                with patch('app.services.ocr.tesseract_engine.TesseractEngine.analyze_document') as mock_tess_analyze:
                    with patch('app.services.ocr.openai_engine.OpenAIEngine.analyze_document') as mock_openai_analyze:
                        mock_tess_avail.return_value = True
                        mock_openai_avail.return_value = True
                        mock_tess_analyze.return_value = mock_low_confidence_result  # 신뢰도 0.65

                        # OpenAI는 높은 신뢰도 반환
                        high_confidence = OCRResult(
                            engine=OCREngineType.OPENAI,
                            document_type=DocumentType.BUSINESS_LICENSE,
                            extracted_data={"사업자등록번호": "123-45-67890", "상호": "(주)테크이노베이션"},
                            confidence_score=0.95,
                            raw_text="",
                            needs_manual_verification=False,
                            processing_time_ms=200.0,
                            errors=[]
                        )
                        mock_openai_analyze.return_value = high_confidence

                        manager = OCRManager(ocr_config_with_fallback)
                        result = await manager.analyze_document(sample_image_path)

                        # OpenAI 결과가 반환되어야 함
                        assert result.engine == OCREngineType.OPENAI
                        assert result.confidence_score == 0.95
                        mock_tess_analyze.assert_called_once()
                        mock_openai_analyze.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_with_preferred_engine(
        self,
        ocr_config_with_fallback,
        sample_image_path,
        mock_ocr_result
    ):
        """선호 엔진 지정 시 우선 사용"""
        with patch('app.services.ocr.openai_engine.OpenAIEngine.is_available') as mock_avail:
            with patch('app.services.ocr.openai_engine.OpenAIEngine.analyze_document') as mock_analyze:
                mock_avail.return_value = True

                openai_result = OCRResult(
                    engine=OCREngineType.OPENAI,
                    document_type=DocumentType.BUSINESS_LICENSE,
                    extracted_data={"test": "data"},
                    confidence_score=0.95,
                    raw_text="",
                    needs_manual_verification=False,
                    processing_time_ms=150.0,
                    errors=[]
                )
                mock_analyze.return_value = openai_result

                manager = OCRManager(ocr_config_with_fallback)
                result = await manager.analyze_document(
                    sample_image_path,
                    preferred_engine=OCREngineType.OPENAI
                )

                assert result.engine == OCREngineType.OPENAI
                mock_analyze.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_with_ensemble_mode(
        self,
        ocr_config_ensemble,
        sample_image_path
    ):
        """앙상블 모드: 여러 엔진 병렬 실행"""
        with patch('app.services.ocr.tesseract_engine.TesseractEngine.is_available') as mock_tess_avail:
            with patch('app.services.ocr.openai_engine.OpenAIEngine.is_available') as mock_openai_avail:
                with patch('app.services.ocr.gemini_engine.GeminiEngine.is_available') as mock_gemini_avail:
                    mock_tess_avail.return_value = True
                    mock_openai_avail.return_value = True
                    mock_gemini_avail.return_value = True

                    # Mock 결과 (신뢰도 다름)
                    tess_result = OCRResult(
                        engine=OCREngineType.TESSERACT,
                        document_type=DocumentType.BUSINESS_LICENSE,
                        extracted_data={"test": "data"},
                        confidence_score=0.80,
                        raw_text="",
                        needs_manual_verification=False,
                        processing_time_ms=100.0,
                        errors=[]
                    )

                    openai_result = OCRResult(
                        engine=OCREngineType.OPENAI,
                        document_type=DocumentType.BUSINESS_LICENSE,
                        extracted_data={"test": "better_data"},
                        confidence_score=0.95,  # 가장 높음
                        raw_text="",
                        needs_manual_verification=False,
                        processing_time_ms=200.0,
                        errors=[]
                    )

                    gemini_result = OCRResult(
                        engine=OCREngineType.GEMINI,
                        document_type=DocumentType.BUSINESS_LICENSE,
                        extracted_data={"test": "data"},
                        confidence_score=0.88,
                        raw_text="",
                        needs_manual_verification=False,
                        processing_time_ms=150.0,
                        errors=[]
                    )

                    with patch('app.services.ocr.tesseract_engine.TesseractEngine.analyze_document') as mock_tess:
                        with patch('app.services.ocr.openai_engine.OpenAIEngine.analyze_document') as mock_openai:
                            with patch('app.services.ocr.gemini_engine.GeminiEngine.analyze_document') as mock_gemini:
                                mock_tess.return_value = tess_result
                                mock_openai.return_value = openai_result
                                mock_gemini.return_value = gemini_result

                                manager = OCRManager(ocr_config_ensemble)
                                result = await manager.analyze_document(sample_image_path)

                                # 가장 높은 신뢰도 (OpenAI)가 선택되어야 함
                                assert result.engine == OCREngineType.OPENAI
                                assert result.confidence_score == 0.95
                                assert "ensemble_info" in result.extracted_data

    def test_get_available_engines(self, ocr_config_with_fallback):
        """사용 가능한 엔진 목록 조회"""
        with patch('app.services.ocr.tesseract_engine.TesseractEngine.is_available') as mock_tess:
            with patch('app.services.ocr.openai_engine.OpenAIEngine.is_available') as mock_openai:
                mock_tess.return_value = True
                mock_openai.return_value = True

                manager = OCRManager(ocr_config_with_fallback)
                engines = manager.get_available_engines()

                assert "tesseract" in engines
                assert "openai" in engines

    @pytest.mark.asyncio
    async def test_extract_text_simple(self, ocr_config_tesseract_only, sample_image_path):
        """간단한 텍스트 추출"""
        with patch('app.services.ocr.tesseract_engine.TesseractEngine.is_available') as mock_avail:
            with patch('app.services.ocr.tesseract_engine.TesseractEngine.extract_text') as mock_extract:
                mock_avail.return_value = True
                mock_extract.return_value = "추출된 텍스트"

                manager = OCRManager(ocr_config_tesseract_only)
                text = await manager.extract_text_simple(sample_image_path)

                assert text == "추출된 텍스트"
                mock_extract.assert_called_once()

    def test_fallback_strategy_none(self, ocr_config_tesseract_only):
        """폴백 전략: None"""
        manager = OCRManager(ocr_config_tesseract_only)
        assert manager.fallback_strategy == FallbackStrategy.NONE

    def test_fallback_strategy_on_low_confidence(self, ocr_config_with_fallback):
        """폴백 전략: On Low Confidence"""
        manager = OCRManager(ocr_config_with_fallback)
        assert manager.fallback_strategy == FallbackStrategy.ON_LOW_CONFIDENCE
