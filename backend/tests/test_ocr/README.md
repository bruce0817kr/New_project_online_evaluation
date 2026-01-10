# OCR 시스템 테스트

## 개요

이 디렉토리는 멀티 OCR 엔진 시스템의 단위 테스트 및 통합 테스트를 포함합니다.

## 테스트 구조

```
test_ocr/
├── conftest.py                  # 공통 fixtures 및 mock 데이터
├── test_tesseract_engine.py    # Tesseract 엔진 단위 테스트
├── test_ocr_manager.py          # OCR 매니저 폴백 전략 테스트
└── test_ocr_api.py              # OCR API 엔드포인트 통합 테스트
```

## 테스트 커버리지

### 1. Tesseract 엔진 (`test_tesseract_engine.py`)
- ✅ 엔진 타입 확인
- ✅ 설치 여부 검증
- ✅ 텍스트 추출
- ✅ 사업자등록증 파싱
- ✅ 법인등기부등본 파싱
- ✅ 사업자번호 체크섬 검증
- ✅ 신뢰도 계산
- ✅ 오류 처리

### 2. OCR 매니저 (`test_ocr_manager.py`)
- ✅ 단일/다중 엔진 초기화
- ✅ 높은 신뢰도 시 폴백 없음
- ✅ 낮은 신뢰도 시 자동 폴백
- ✅ 선호 엔진 지정
- ✅ 앙상블 모드 (병렬 실행)
- ✅ 사용 가능 엔진 목록
- ✅ 폴백 전략 검증

### 3. OCR API (`test_ocr_api.py`)
- ✅ 문서 분석 성공
- ✅ 잘못된 파일 형식 거부
- ✅ 선호 엔진 지정 API
- ✅ 사용 가능 엔진 조회
- ✅ 간단 텍스트 추출
- ✅ 인증 검증
- ✅ OCR 실패 처리

## 테스트 실행

### 전체 OCR 테스트 실행
```bash
cd backend
pytest tests/test_ocr/ -v
```

### 특정 테스트 파일만 실행
```bash
# Tesseract 엔진만
pytest tests/test_ocr/test_tesseract_engine.py -v

# OCR 매니저만
pytest tests/test_ocr/test_ocr_manager.py -v

# API 엔드포인트만
pytest tests/test_ocr/test_ocr_api.py -v
```

### 커버리지 리포트
```bash
pytest tests/test_ocr/ --cov=app/services/ocr --cov-report=html
```

### 특정 테스트만 실행
```bash
# 폴백 전략 테스트만
pytest tests/test_ocr/test_ocr_manager.py::TestOCRManager::test_analyze_with_low_confidence_fallback -v
```

## Mock 전략

### 외부 API Mock
실제 API 키 없이도 테스트가 가능하도록 모든 외부 API 호출은 Mock으로 처리됩니다:

- **OpenAI API**: `mock_openai_response` fixture
- **Gemini API**: `mock_gemini_response` fixture
- **Mistral API**: Mock response 생성

### 파일 시스템 Mock
- `tmp_path` fixture로 임시 파일 생성
- 테스트 후 자동 정리

## 예제

### 1. Tesseract 텍스트 추출 테스트
```python
@pytest.mark.asyncio
async def test_extract_text(sample_image_path):
    with patch('pytesseract.image_to_string') as mock_ocr:
        mock_ocr.return_value = "추출된 텍스트"

        engine = TesseractEngine()
        text = await engine.extract_text(sample_image_path)

        assert "추출된 텍스트" in text
```

### 2. 폴백 전략 테스트
```python
@pytest.mark.asyncio
async def test_fallback_on_low_confidence():
    # Tesseract: 신뢰도 0.65 (낮음)
    # OpenAI: 신뢰도 0.95 (높음)
    # → OpenAI 결과가 반환되어야 함

    manager = OCRManager(config)
    result = await manager.analyze_document(image_path)

    assert result.engine == OCREngineType.OPENAI
```

### 3. API 통합 테스트
```python
def test_analyze_document_api():
    response = client.post(
        "/api/v1/ocr/analyze",
        files={"file": image_file},
        data={"document_type": "사업자등록증"}
    )

    assert response.status_code == 200
    assert "extracted_data" in response.json()
```

## 테스트 데이터

### Fixtures (`conftest.py`)
- `sample_business_license_text`: 사업자등록증 샘플 텍스트
- `sample_corporate_registry_text`: 법인등기부등본 샘플 텍스트
- `sample_image_path`: 테스트용 이미지 파일
- `expected_business_license_data`: 예상 파싱 결과
- `mock_ocr_result`: Mock OCR 결과 (고신뢰도)
- `mock_low_confidence_result`: Mock OCR 결과 (저신뢰도)

## CI/CD 통합

### GitHub Actions 예시
```yaml
name: OCR Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run OCR tests
        run: pytest tests/test_ocr/ -v --cov
```

## 트러블슈팅

### Tesseract 설치 필요
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-kor

# macOS
brew install tesseract tesseract-lang
```

### 비동기 테스트 오류
`pytest-asyncio` 설치 확인:
```bash
pip install pytest-asyncio
```

### Mock 관련 오류
`unittest.mock`이 제대로 import되는지 확인.

## 참고

- **개발 가이드**: `.claude/skills/biz-support-eval-dev/`
- **보안 표준**: `references/security_standard.md`
- **평가 가이드라인**: `references/eval_guidelines.md`
