# 핵심 기술 역량 (Skills)

이 프로젝트를 구현하기 위해 필요한 핵심 로직 모듈과 기술 가이드입니다.

## 1. OCR_Parser

### 개요
pytesseract와 정규표현식(RegEx)를 활용한 서류 내 핵심 지표 추출 기술입니다.

### 주요 기능
- **텍스트 추출**: 이미지/PDF에서 한글 및 영문 텍스트 추출
- **데이터 파싱**: 사업자등록번호, 기업명, 대표자명 등 구조화된 데이터 추출
- **신뢰도 평가**: 추출된 데이터의 정확도 평가

### 구현 가이드

#### 기본 OCR 처리
```python
import pytesseract
from PIL import Image

def extract_text(image_path: str, language: str = "kor+eng") -> str:
    """이미지에서 텍스트 추출"""
    image = Image.open(image_path)
    text = pytesseract.image_to_string(
        image,
        lang=language,
        config="--psm 6 --oem 3"
    )
    return text
```

#### 사업자등록번호 추출
```python
import re

def extract_business_number(text: str) -> str:
    """
    사업자등록번호 추출 (XXX-XX-XXXXX 형식)
    예: 123-45-67890
    """
    pattern = r'\d{3}-\d{2}-\d{5}'
    match = re.search(pattern, text)
    return match.group(0) if match else None
```

#### 전처리 기법
- **이미지 보정**: 명암 조절, 노이즈 제거
- **회전 보정**: 기울어진 문서 자동 보정
- **해상도 향상**: DPI 조정으로 인식률 향상

## 2. PDF_Engine

### 개요
react-pdf-viewer를 활용한 Canvas 기반의 고성능 문서 렌더링 기술입니다.

### 주요 기능
- **PDF 렌더링**: 브라우저에서 PDF 문서 직접 렌더링
- **페이지 내비게이션**: 페이지 이동, 확대/축소 기능
- **텍스트 선택**: PDF 내 텍스트 선택 및 복사

### 구현 가이드

#### PDF 뷰어 컴포넌트
```javascript
import { Worker, Viewer } from '@react-pdf-viewer/core';
import '@react-pdf-viewer/core/lib/styles/index.css';

function PDFViewer({ fileUrl }) {
  return (
    <Worker workerUrl="https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.min.js">
      <Viewer fileUrl={fileUrl} />
    </Worker>
  );
}
```

#### 페이지 제어
```javascript
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';

function AdvancedPDFViewer({ fileUrl }) {
  const defaultLayoutPluginInstance = defaultLayoutPlugin();

  return (
    <Worker workerUrl="...">
      <Viewer
        fileUrl={fileUrl}
        plugins={[defaultLayoutPluginInstance]}
      />
    </Worker>
  );
}
```

### 최적화 전략
- **Lazy Loading**: 현재 보이는 페이지만 렌더링
- **캐싱**: 이미 렌더링된 페이지는 캐시에 저장
- **Progressive Loading**: 문서를 점진적으로 로드

## 3. Aggregation_Logic

### 개요
최고/최저점 제외 평균(Trimmed Mean) 및 가중치 합산 알고리즘입니다.

### 주요 기능
- **단순 평균**: 모든 점수의 평균 계산
- **Trimmed Mean**: 최고/최저점 제외 평균
- **가중치 적용**: 항목별 가중치를 적용한 점수 계산

### 구현 가이드

#### Trimmed Mean 계산
```python
def calculate_trimmed_mean(scores: list[float], trim_count: int = 1) -> float:
    """
    최고/최저점 제외 평균

    Args:
        scores: 점수 리스트
        trim_count: 제외할 최고/최저 점수 개수

    Returns:
        소수점 둘째 자리 반올림한 평균값
    """
    if len(scores) < 5:
        # 5인 미만인 경우 단순 평균
        return round(sum(scores) / len(scores), 2)

    # 정렬 후 최고/최저 제외
    sorted_scores = sorted(scores)
    trimmed_scores = sorted_scores[trim_count:-trim_count]

    return round(sum(trimmed_scores) / len(trimmed_scores), 2)
```

#### 가중치 적용
```python
def apply_weights(
    scores: dict[str, float],
    weights: dict[str, float]
) -> float:
    """
    가중치 적용 점수 계산

    Args:
        scores: {"항목1": 85, "항목2": 90, ...}
        weights: {"항목1": 0.3, "항목2": 0.4, ...}

    Returns:
        가중치 합산 점수
    """
    total = sum(
        scores.get(item, 0) * weight
        for item, weight in weights.items()
    )
    return round(total, 2)
```

### 계산 규칙
- **반올림**: 소수점 셋째 자리에서 반올림
- **정렬**: 최고/최저점 식별을 위해 점수 정렬 필요
- **예외 처리**: 점수가 부족한 경우 단순 평균 사용

## 4. Signature_Capture

### 개요
react-signature-canvas를 이용한 전자서명 데이터의 이미지 변환 및 저장 기술입니다.

### 주요 기능
- **서명 입력**: 마우스/터치로 서명 입력
- **이미지 변환**: Canvas 데이터를 PNG 이미지로 변환
- **데이터 저장**: Base64 또는 파일로 저장

### 구현 가이드

#### 서명 컴포넌트
```javascript
import React, { useRef } from 'react';
import SignatureCanvas from 'react-signature-canvas';

function SignaturePad({ onSave }) {
  const sigCanvas = useRef(null);

  const clear = () => {
    sigCanvas.current.clear();
  };

  const save = () => {
    // PNG 이미지로 변환 (Base64)
    const imageData = sigCanvas.current.toDataURL('image/png');
    onSave(imageData);
  };

  return (
    <div>
      <SignatureCanvas
        ref={sigCanvas}
        canvasProps={{
          width: 500,
          height: 200,
          className: 'signature-canvas'
        }}
      />
      <button onClick={clear}>지우기</button>
      <button onClick={save}>저장</button>
    </div>
  );
}
```

#### 서명 데이터 처리
```python
import base64
from io import BytesIO
from PIL import Image

def save_signature(base64_data: str, file_path: str):
    """Base64 서명 데이터를 파일로 저장"""
    # "data:image/png;base64," 제거
    image_data = base64_data.split(',')[1]
    image_bytes = base64.b64decode(image_data)

    # 이미지 저장
    image = Image.open(BytesIO(image_bytes))
    image.save(file_path, 'PNG')
```

### 보안 고려사항
- **서명 검증**: 제출된 서명은 변경 불가능하도록 해시값 저장
- **타임스탬프**: 서명 시각을 함께 기록
- **암호화**: 민감한 서명 데이터는 암호화하여 저장

## 5. Auto_Save

### 개요
Debounce 패턴을 활용한 자동 저장 기능입니다.

### 구현 가이드

#### Debounce Hook
```javascript
import { useEffect, useRef } from 'react';

function useDebounce(callback, delay) {
  const timeoutRef = useRef(null);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const debouncedCallback = (...args) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      callback(...args);
    }, delay);
  };

  return debouncedCallback;
}
```

#### Auto-save 적용
```javascript
function ScoreInput({ scores, onSave }) {
  const autoSave = useDebounce((data) => {
    console.log('Auto-saving:', data);
    onSave(data);
  }, 3000);

  useEffect(() => {
    autoSave(scores);
  }, [scores]);

  return (
    // Input components
  );
}
```

### 사용자 경험 개선
- **시각적 피드백**: 저장 중/완료 상태 표시
- **에러 처리**: 저장 실패 시 재시도 로직
- **네트워크 최적화**: 불필요한 요청 최소화
