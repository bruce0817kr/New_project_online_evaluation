"""
OCR API 엔드포인트 통합 테스트
"""
import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from io import BytesIO
from PIL import Image

from app.main import app
from app.services.ocr import OCRResult, OCREngineType, DocumentType


@pytest.fixture
def client():
    """테스트 클라이언트"""
    return TestClient(app)


@pytest.fixture
def mock_user_token():
    """Mock 사용자 토큰"""
    # 실제 JWT 토큰 생성 로직을 Mock
    return "Bearer mock-jwt-token"


@pytest.fixture
def sample_upload_file():
    """업로드용 테스트 이미지 파일"""
    # 간단한 이미지 생성
    img = Image.new('RGB', (100, 100), color='white')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return ("test.jpg", img_byte_arr, "image/jpeg")


class TestOCRAPI:
    """OCR API 테스트"""

    @pytest.mark.asyncio
    async def test_analyze_document_success(
        self,
        client,
        mock_user_token,
        sample_upload_file
    ):
        """문서 분석 성공"""
        with patch('app.api.v1.endpoints.ocr_complete.get_current_user') as mock_user:
            with patch('app.api.v1.endpoints.ocr_complete.get_ocr_manager') as mock_manager:
                # Mock 사용자
                mock_user.return_value = Mock(id="test-user-id", username="test_user")

                # Mock OCR 결과
                mock_result = OCRResult(
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

                mock_ocr = Mock()
                mock_ocr.analyze_document = Mock(return_value=mock_result)
                mock_manager.return_value = mock_ocr

                # API 호출
                response = client.post(
                    "/api/v1/ocr/analyze",
                    files={"file": sample_upload_file},
                    data={"document_type": "사업자등록증"},
                    headers={"Authorization": mock_user_token}
                )

                assert response.status_code == 200
                data = response.json()

                assert data["success"] is True
                assert data["engine"] == "tesseract"
                assert "사업자등록번호" in data["extracted_data"]
                assert data["confidence_score"] == 0.92
                assert data["needs_manual_verification"] is False

    @pytest.mark.asyncio
    async def test_analyze_document_invalid_file_type(self, client, mock_user_token):
        """잘못된 파일 형식"""
        with patch('app.api.v1.endpoints.ocr_complete.get_current_user') as mock_user:
            mock_user.return_value = Mock(id="test-user-id", username="test_user")

            # .txt 파일 (허용되지 않음)
            invalid_file = ("test.txt", BytesIO(b"text content"), "text/plain")

            response = client.post(
                "/api/v1/ocr/analyze",
                files={"file": invalid_file},
                data={"document_type": "사업자등록증"},
                headers={"Authorization": mock_user_token}
            )

            assert response.status_code == 400
            assert "지원하지 않는 파일 형식" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_analyze_document_with_preferred_engine(
        self,
        client,
        mock_user_token,
        sample_upload_file
    ):
        """선호 엔진 지정"""
        with patch('app.api.v1.endpoints.ocr_complete.get_current_user') as mock_user:
            with patch('app.api.v1.endpoints.ocr_complete.get_ocr_manager') as mock_manager:
                mock_user.return_value = Mock(id="test-user-id", username="test_user")

                mock_result = OCRResult(
                    engine=OCREngineType.OPENAI,
                    document_type=DocumentType.BUSINESS_LICENSE,
                    extracted_data={"test": "data"},
                    confidence_score=0.95,
                    raw_text="",
                    needs_manual_verification=False,
                    processing_time_ms=200.0,
                    errors=[]
                )

                mock_ocr = Mock()
                mock_ocr.analyze_document = Mock(return_value=mock_result)
                mock_manager.return_value = mock_ocr

                response = client.post(
                    "/api/v1/ocr/analyze",
                    files={"file": sample_upload_file},
                    data={
                        "document_type": "사업자등록증",
                        "preferred_engine": "openai"
                    },
                    headers={"Authorization": mock_user_token}
                )

                assert response.status_code == 200
                data = response.json()
                assert data["engine"] == "openai"

    @pytest.mark.asyncio
    async def test_get_available_engines(self, client, mock_user_token):
        """사용 가능한 엔진 목록 조회"""
        with patch('app.api.v1.endpoints.ocr_complete.get_current_user') as mock_user:
            with patch('app.api.v1.endpoints.ocr_complete.get_ocr_manager') as mock_manager:
                mock_user.return_value = Mock(id="test-user-id", username="test_user")

                mock_ocr = Mock()
                mock_ocr.get_available_engines = Mock(return_value=["tesseract", "openai"])
                mock_ocr.fallback_strategy.value = "on_low_confidence"
                mock_ocr.confidence_threshold = 0.85
                mock_ocr.enable_ensemble = False
                mock_manager.return_value = mock_ocr

                response = client.get(
                    "/api/v1/ocr/engines",
                    headers={"Authorization": mock_user_token}
                )

                assert response.status_code == 200
                data = response.json()

                assert "engines" in data
                assert "tesseract" in data["engines"]
                assert data["fallback_strategy"] == "on_low_confidence"
                assert data["confidence_threshold"] == 0.85

    @pytest.mark.asyncio
    async def test_extract_text_only(self, client, mock_user_token, sample_upload_file):
        """간단한 텍스트 추출"""
        with patch('app.api.v1.endpoints.ocr_complete.get_current_user') as mock_user:
            with patch('app.api.v1.endpoints.ocr_complete.get_ocr_manager') as mock_manager:
                mock_user.return_value = Mock(id="test-user-id", username="test_user")

                mock_ocr = Mock()
                mock_ocr.extract_text_simple = Mock(return_value="추출된 텍스트입니다")
                mock_manager.return_value = mock_ocr

                response = client.post(
                    "/api/v1/ocr/extract-text",
                    files={"file": sample_upload_file},
                    headers={"Authorization": mock_user_token}
                )

                assert response.status_code == 200
                data = response.json()

                assert data["success"] is True
                assert data["text"] == "추출된 텍스트입니다"

    @pytest.mark.asyncio
    async def test_analyze_document_unauthorized(self, client, sample_upload_file):
        """인증 없이 요청 시 401 에러"""
        response = client.post(
            "/api/v1/ocr/analyze",
            files={"file": sample_upload_file},
            data={"document_type": "사업자등록증"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_analyze_document_ocr_failure(
        self,
        client,
        mock_user_token,
        sample_upload_file
    ):
        """OCR 처리 실패"""
        with patch('app.api.v1.endpoints.ocr_complete.get_current_user') as mock_user:
            with patch('app.api.v1.endpoints.ocr_complete.get_ocr_manager') as mock_manager:
                mock_user.return_value = Mock(id="test-user-id", username="test_user")

                mock_ocr = Mock()
                mock_ocr.analyze_document = Mock(side_effect=Exception("OCR 실패"))
                mock_manager.return_value = mock_ocr

                response = client.post(
                    "/api/v1/ocr/analyze",
                    files={"file": sample_upload_file},
                    data={"document_type": "사업자등록증"},
                    headers={"Authorization": mock_user_token}
                )

                assert response.status_code == 500
                assert "OCR 처리 실패" in response.json()["detail"]
